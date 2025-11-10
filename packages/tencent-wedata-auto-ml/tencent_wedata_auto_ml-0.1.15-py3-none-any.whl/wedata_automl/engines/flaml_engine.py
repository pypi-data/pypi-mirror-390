from typing import Any, Dict, List, Optional

import mlflow
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline as SkPipe
from sklearn.metrics import accuracy_score
import logging

logger = logging.getLogger(__name__)


# Robust import for FLAML across versions
try:
    from flaml import AutoML  # preferred public import (flaml >= 2.0)
    import flaml as flaml_pkg
except ImportError:
    try:
        from flaml.automl.automl import AutoML  # flaml < 2.0 or flaml[automl] not installed
        import flaml as flaml_pkg
    except ImportError as e:
        raise ImportError(
            "Cannot import AutoML from flaml. "
            "Please install flaml with AutoML support: pip install 'flaml[automl]==2.3.6' or pip install 'tencent-wedata-auto-ml[full]'"
        ) from e

from wedata_automl.config import normalize_config
from wedata_automl.utils.sk_pipeline import build_numeric_preprocessor
from wedata_automl.artifact_contract import (
    log_feature_list,
    log_best_config_overall,
    log_best_config_per_estimator,
    log_engine_meta,
)
from wedata_automl.utils.spark_utils import compute_split_and_weights
from wedata_automl.utils.print_utils import safe_print, print_section, print_dict
from wedata_automl.utils.notebook_generator import generate_notebook_code


def _load_pdf_from_cfg(cfg: Dict[str, Any], spark) -> pd.DataFrame:
    if cfg.get("table"):
        if spark is None:
            raise RuntimeError("Spark session is required to read table. Provide 'spark' or run in Spark notebook.")

        df = spark.read.table(cfg["table"])

        # Limit rows if specified
        limit = cfg.get("limit_rows")
        if limit is not None and limit > 0:
            safe_print(f"Limiting data to first {limit} rows", level="WARNING")
            df = df.limit(limit)

        return df.toPandas()
    raise ValueError("No data source specified. Provide 'table' in config for V1.")


def run(cfg: Dict[str, Any], spark=None, pdf: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    cfg = normalize_config(cfg)
    # Setup logging based on config
    level_name = str(cfg.get("log_level", "INFO")).upper()
    level = getattr(logging, level_name, logging.INFO)
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            force=True
        )

    # Enable FLAML verbose logging (default to True for better visibility)
    flaml_verbose = cfg.get("flaml_verbose", True)
    if flaml_verbose:
        # Enable FLAML's internal logging
        logging.getLogger("flaml").setLevel(logging.INFO)
        logging.getLogger("flaml.automl").setLevel(logging.INFO)
        logging.getLogger("flaml.tune").setLevel(logging.INFO)
        safe_print("FLAML verbose logging enabled (verbose=3)", level="DEBUG")
    else:
        safe_print("FLAML verbose logging disabled (verbose=0)", level="DEBUG")

    logger.setLevel(level)

    # Print to stdout for Notebook visibility
    print_section("WeData AutoML - FLAML Engine")
    safe_print(f"Engine: {cfg['engine']} | Task: {cfg['task']} | Metric: {cfg['metric']}")
    safe_print(f"Time Budget: {cfg['time_budget']}s | Seed: {cfg.get('seed')}")
    safe_print(f"Data Source: table={cfg.get('table')}, provided_pdf={pdf is not None}")


    # 1) Load data
    if pdf is None:
        pdf = _load_pdf_from_cfg(cfg, spark)

    safe_print(f"Loaded data with shape={getattr(pdf, 'shape', None)}")


    label = cfg["label_col"]
    disable_cols = set(cfg.get("disable_cols", [])) | {label}
    features: List[str] = [c for c in pdf.columns if c not in disable_cols]

    safe_print(f"Label column: {label}; Selected {len(features)} feature columns")

    if cfg["task"] == "classification":
        try:
            _dist = pd.Series(pdf[label]).value_counts().to_dict()
            safe_print(f"Label distribution (top 10): {dict(list(_dist.items())[:10])}", level="DEBUG")
        except Exception:
            pass


    # 2) Compute split marker and sample weights
    split_col, sample_weights = compute_split_and_weights(
        y=pdf[label].values,
        task=cfg["task"],
        train_ratio=float(cfg["split"]["train_ratio"]),
        val_ratio=float(cfg["split"]["val_ratio"]),
        test_ratio=float(cfg["split"]["test_ratio"]),
        stratify=bool(cfg["split"]["stratify"]),
        random_state=int(cfg.get("seed", 42)),
    )
    pdf["_automl_split_col_0000"] = split_col.values
    pdf["_automl_sample_weight_0000"] = sample_weights.values

    train_cnt = int((pdf["_automl_split_col_0000"] == 0).sum())
    val_cnt = int((pdf["_automl_split_col_0000"] == 1).sum())
    test_cnt = int((pdf["_automl_split_col_0000"] == 2).sum())
    safe_print(f"Split counts: train={train_cnt}, val={val_cnt}, test={test_cnt}")

    if cfg["task"] == "classification":
        import numpy as _np
        _sw = sample_weights.values if hasattr(sample_weights, "values") else sample_weights
        safe_print(f"Sample weights: min={float(_np.min(_sw)):.4f}, mean={float(_np.mean(_sw)):.4f}, max={float(_np.max(_sw)):.4f}")


    # 3) Build preprocessor and split dataframes
    pre = build_numeric_preprocessor(features)
    train_df = pdf[pdf["_automl_split_col_0000"] == 0]
    val_df = pdf[pdf["_automl_split_col_0000"] == 1]
    test_df = pdf[pdf["_automl_split_col_0000"] == 2]

    X_train = train_df[features]
    y_train = train_df[label].values
    sw_train = train_df["_automl_sample_weight_0000"].values

    X_val = val_df[features]
    y_val = val_df[label].values
    sw_val = val_df["_automl_sample_weight_0000"].values

    X_test = test_df[features]
    y_test = test_df[label].values
    sw_test = test_df["_automl_sample_weight_0000"].values

    safe_print(f"Split shapes: X_train={getattr(X_train, 'shape', None)}, X_val={getattr(X_val, 'shape', None)}, X_test={getattr(X_test, 'shape', None)}")


    # Fit preprocessor on train only to avoid leakage
    X_train_num = pre.fit_transform(X_train)
    X_val_num = pre.transform(X_val)

    safe_print(f"Preprocessor fitted. Transformed shapes: X_train_num={getattr(X_train_num, 'shape', None)}, X_val_num={getattr(X_val_num, 'shape', None)}")


    # 4) FLAML settings
    automl = AutoML()

    # Enable verbose logging for FLAML
    flaml_verbose = cfg.get("flaml_verbose", True)  # Default to True for better visibility
    verbose_level = 3 if flaml_verbose else 0  # 0=silent, 1=minimal, 2=normal, 3=detailed

    settings = {
        "task": cfg["task"],
        "metric": cfg["metric"],
        "time_budget": int(cfg["time_budget"]),
        "eval_method": "holdout",
        "ensemble": False,
        "verbose": verbose_level,
        "estimator_list": cfg.get("estimators", ["lgbm", "xgboost", "rf", "lrl1"]),
        "seed": int(cfg.get("seed", 42)),
        "log_file_name": None,  # Don't write to file, output to stdout
    }

    safe_print(f"FLAML version={getattr(flaml_pkg, '__version__', 'unknown')}")
    safe_print(f"FLAML settings: time_budget={settings['time_budget']}s, metric={settings['metric']}, estimators={settings['estimator_list']}, seed={settings['seed']}, verbose={settings['verbose']}")


    # Get or create MLflow experiment
    experiment_name = cfg.get("experiment_name", "wedata_automl")
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
        safe_print(f"Created new MLflow experiment: {experiment_name} (ID: {experiment_id})", level="INFO")
    else:
        experiment_id = experiment.experiment_id
        safe_print(f"Using existing MLflow experiment: {experiment_name} (ID: {experiment_id})", level="INFO")

    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=f"{cfg['engine']}_automl_main") as parent_run:
        parent_run_id = parent_run.info.run_id
        safe_print(f"MLflow parent run started: run_id={parent_run_id}", level="START")
        safe_print(f"Experiment: {experiment_name} | Parent Run: {parent_run_id}")

        # Parent run logging
        mlflow.log_params({
            "table": cfg.get("table"),
            "label": label,
            "n_rows": len(pdf),
            "n_features": len(features),
            **{f"flaml__{k}": v for k, v in settings.items()},
        })
        mlflow.log_dict({
            "train_ratio": cfg["split"]["train_ratio"],
            "val_ratio": cfg["split"]["val_ratio"],
            "test_ratio": cfg["split"]["test_ratio"],
            "stratify": cfg["split"]["stratify"],
            "counts": {
                "train": int((pdf["_automl_split_col_0000"] == 0).sum()),
                "val": int((pdf["_automl_split_col_0000"] == 1).sum()),
                "test": int((pdf["_automl_split_col_0000"] == 2).sum()),
            }
        }, "artifacts/split_stats.json")
        log_feature_list(features)
        log_engine_meta({"engine": "flaml", "version": getattr(flaml_pkg, "__version__", "unknown")})

        # 5) Train with FLAML using our validation split
        safe_print(f"Starting AutoML.fit: X_train_num={getattr(X_train_num, 'shape', None)}, X_val_num={getattr(X_val_num, 'shape', None)}", level="START")
        safe_print(f"FLAML will try estimators: {settings['estimator_list']}")
        safe_print(f"Training in progress... (this may take up to {settings['time_budget']}s)")
        safe_print(f"MLflow trial logging: ENABLED - Each FLAML trial will be logged as a child run", level="INFO")

        import time
        start_time = time.time()

        # Enable MLflow logging for FLAML trials
        # Each trial will be logged as a nested run under the parent run
        automl.fit(
            X_train=X_train_num,
            y_train=y_train,
            X_val=X_val_num,
            y_val=y_val,
            mlflow_logging=True,  # Enable trial-level logging
            **settings,
        )

        elapsed_time = time.time() - start_time
        safe_print(f"AutoML.fit completed in {elapsed_time:.1f}s", level="SUCCESS")

        best_est = automl.best_estimator
        best_cfg = automl.best_config
        log_best_config_overall(best_cfg)
        if getattr(automl, "best_config_per_estimator", None):
            log_best_config_per_estimator(automl.best_config_per_estimator)
        _bpe = getattr(automl, "best_config_per_estimator", {}) or {}
        safe_print(f"AutoML finished. best_estimator={best_est}, best_loss={getattr(automl, 'best_loss', None)}", level="SUCCESS")
        safe_print(f"AutoML trials summary: estimators_tried={len(_bpe)}, per-estimator best configs={list(_bpe.keys()) if isinstance(_bpe, dict) else type(_bpe)}")
        mlflow.log_param("best_estimator", best_est)

        # 6) Build serving pipeline: DataFrame -> pre -> estimator
        clf = automl.model
        pipe = SkPipe([("preprocess", pre), ("clf", clf)])
        safe_print(f"Serving pipeline built. Fitting pipeline on raw X_train with shape={getattr(X_train, 'shape', None)}")

        pipe.fit(X_train, y_train)

        # quick metrics on all splits (unweighted + weighted)
        if cfg["task"] == "classification":
            from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score, confusion_matrix
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            import seaborn as sns
            import tempfile
            import os

            for name, X, y_true, sw in [
                ("train", X_train, y_train, sw_train),
                ("val", X_val, y_val, sw_val),
                ("test", X_test, y_test, sw_test),
            ]:
                pred = pipe.predict(X)

                # Accuracy metrics
                acc = float(accuracy_score(y_true, pred))
                accw = float(accuracy_score(y_true, pred, sample_weight=sw))
                mlflow.log_metric(f"{name}_accuracy", acc)
                mlflow.log_metric(f"{name}_accuracy_weighted", accw)

                # F1, Precision, Recall metrics
                f1 = float(f1_score(y_true, pred, average='weighted', zero_division=0))
                precision = float(precision_score(y_true, pred, average='weighted', zero_division=0))
                recall = float(recall_score(y_true, pred, average='weighted', zero_division=0))
                mlflow.log_metric(f"{name}_f1", f1)
                mlflow.log_metric(f"{name}_precision", precision)
                mlflow.log_metric(f"{name}_recall", recall)

                # ROC AUC (if predict_proba is available)
                if hasattr(pipe, 'predict_proba'):
                    try:
                        pred_proba = pipe.predict_proba(X)
                        # For binary classification
                        if pred_proba.shape[1] == 2:
                            auc = float(roc_auc_score(y_true, pred_proba[:, 1], sample_weight=sw))
                        # For multi-class classification
                        else:
                            auc = float(roc_auc_score(y_true, pred_proba, multi_class='ovr', average='weighted', sample_weight=sw))
                        mlflow.log_metric(f"{name}_roc_auc", auc)
                        safe_print(f"{name} metrics: accuracy={acc:.4f}, f1={f1:.4f}, precision={precision:.4f}, recall={recall:.4f}, roc_auc={auc:.4f}, n={len(y_true)}")
                    except Exception as e:
                        safe_print(f"{name} metrics: accuracy={acc:.4f}, f1={f1:.4f}, precision={precision:.4f}, recall={recall:.4f}, n={len(y_true)} (ROC AUC failed: {e})")
                else:
                    safe_print(f"{name} metrics: accuracy={acc:.4f}, f1={f1:.4f}, precision={precision:.4f}, recall={recall:.4f}, n={len(y_true)}")

                # Generate confusion matrix visualization (for val and test sets)
                if name in ["val", "test"]:
                    try:
                        cm = confusion_matrix(y_true, pred)
                        plt.figure(figsize=(10, 8))
                        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True)
                        plt.title(f'{name.capitalize()} Confusion Matrix')
                        plt.ylabel('True Label')
                        plt.xlabel('Predicted Label')
                        plt.tight_layout()

                        # Save to temporary file and log as artifact
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                            temp_path = f.name
                        plt.savefig(temp_path, bbox_inches='tight', dpi=100)
                        mlflow.log_artifact(temp_path, f"artifacts/{name}_confusion_matrix.png")
                        os.unlink(temp_path)
                        plt.close()
                        safe_print(f"✓ {name} 混淆矩阵已保存")
                    except Exception as e:
                        safe_print(f"⚠️  {name} 混淆矩阵生成失败: {e}", level="WARNING")
                        plt.close('all')

            # Generate feature importance visualization (if available)
            try:
                # Check if the final estimator has feature_importances_
                final_estimator = None
                if hasattr(pipe, 'named_steps'):
                    # Try to get the classifier step
                    if 'classifier' in pipe.named_steps:
                        final_estimator = pipe.named_steps['classifier']
                    elif 'estimator' in pipe.named_steps:
                        final_estimator = pipe.named_steps['estimator']

                if final_estimator and hasattr(final_estimator, 'feature_importances_'):
                    importances = final_estimator.feature_importances_

                    # Create feature importance DataFrame
                    feature_importance_df = pd.DataFrame({
                        'feature': features,
                        'importance': importances
                    }).sort_values('importance', ascending=False)

                    # Save as JSON
                    mlflow.log_dict(feature_importance_df.to_dict('records'), "artifacts/feature_importance.json")

                    # Plot top 20 features
                    top_n = min(20, len(feature_importance_df))
                    plt.figure(figsize=(10, max(6, top_n * 0.3)))
                    plt.barh(range(top_n), feature_importance_df['importance'][:top_n])
                    plt.yticks(range(top_n), feature_importance_df['feature'][:top_n])
                    plt.xlabel('Importance')
                    plt.title(f'Top {top_n} Feature Importances ({best_est})')
                    plt.gca().invert_yaxis()
                    plt.tight_layout()

                    # Save to temporary file and log as artifact
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                        temp_path = f.name
                    plt.savefig(temp_path, bbox_inches='tight', dpi=100)
                    mlflow.log_artifact(temp_path, "artifacts/feature_importance.png")
                    os.unlink(temp_path)
                    plt.close()
                    safe_print(f"✓ 特征重要性图已保存 (top {top_n} features)")
                else:
                    safe_print(f"ℹ️  {best_est} 不支持 feature_importances_，跳过特征重要性分析", level="INFO")
            except Exception as e:
                safe_print(f"⚠️  特征重要性分析失败: {e}", level="WARNING")
                plt.close('all')

            # Generate SHAP values analysis (optional, requires shap library)
            if cfg.get("enable_shap", False):
                try:
                    import shap
                    safe_print("🔍 开始 SHAP 值分析（这可能需要一些时间）...", level="INFO")

                    # Use a sample of training data as background (max 100 samples for speed)
                    background_size = min(100, len(X_train))
                    background_data = X_train.sample(n=background_size, random_state=cfg.get("seed", 42))

                    # Use a sample of validation data for explanation (max 50 samples)
                    explain_size = min(50, len(X_val))
                    explain_data = X_val.sample(n=explain_size, random_state=cfg.get("seed", 42))

                    # Create SHAP explainer
                    explainer = shap.Explainer(pipe.predict, background_data)
                    shap_values = explainer(explain_data)

                    # Generate SHAP summary plot
                    plt.figure(figsize=(10, 8))
                    shap.summary_plot(shap_values, explain_data, feature_names=features, show=False)
                    plt.tight_layout()

                    # Save to temporary file and log as artifact
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                        temp_path = f.name
                    plt.savefig(temp_path, bbox_inches='tight', dpi=100)
                    mlflow.log_artifact(temp_path, "artifacts/shap_summary.png")
                    os.unlink(temp_path)
                    plt.close()
                    safe_print(f"✓ SHAP 摘要图已保存 (background={background_size}, explain={explain_size})")

                except ImportError:
                    safe_print("⚠️  SHAP 库未安装，跳过 SHAP 分析。安装方法: pip install shap", level="WARNING")
                except Exception as e:
                    safe_print(f"⚠️  SHAP 分析失败: {e}", level="WARNING")
                    plt.close('all')

        # 7) Registration via WeData client.log_model
        input_example = X_train.head(3)
        uri = f"runs:/{mlflow.active_run().info.run_id}/{cfg.get('artifact_path', 'model')}"
        version = None

        register_config = cfg.get("register", {})
        register_enabled = register_config.get("enable", False)

        # Print registration status to stdout for Notebook
        print_section("模型注册配置")
        safe_print(f"注册启用: {register_enabled}")
        if register_enabled:
            safe_print(f"注册后端: {register_config.get('backend', 'wedata')}")
            safe_print(f"模型名称: {register_config.get('model_name', 'wedata_model')}")

        if register_enabled:
            backend = cfg["register"].get("backend", "wedata")
            base = cfg["register"].get("model_name", "wedata_model")
            per_cand = cfg["register"].get("per_candidate", False)
            register_name = f"{base}_{best_est}" if per_cand else base

            safe_print(f"开始注册模型: {register_name} (后端: {backend})", level="START")


            if backend == "wedata":
                try:
                    try:
                        from wedata.feature_store.client import FeatureStoreClient
                    except ImportError:
                        raise ImportError(
                            "WeData Feature Store client not found. "
                            "Please install: pip install tencent-wedata-feature-engineering"
                        )
                    from wedata.feature_store.entities.feature_lookup import FeatureLookup

                    if spark is None:
                        raise RuntimeError("Spark session is required for WeData registration.")
                    client = FeatureStoreClient(spark)
                    safe_print("WeData FeatureStoreClient initialized")

                    training_set_obj = None
                    if cfg["feature_store"].get("use_training_set", True):
                        fs_table = cfg["feature_store"].get("table_name") or cfg.get("table")
                        pks = list(cfg["feature_store"].get("primary_keys", []))
                        safe_print(f"Feature store config: use_training_set=True, table={fs_table}, primary_keys={pks}, label={label}")

                        if len(pks) == 1:
                            pk = pks[0]
                            # Build inference df with PK + label
                            inf_df = spark.read.table(fs_table).select(pk, label)
                            fl = FeatureLookup(table_name=fs_table, lookup_key=pk)
                            # Exclude columns: user-provided + label
                            exclude_cols = list(set(cfg["feature_store"].get("exclude_columns", [])) | {label})
                            training_set_obj = client.create_training_set(
                                df=inf_df,
                                feature_lookups=[fl],
                                label=label,
                                exclude_columns=exclude_cols,
                            )
                            safe_print(f"TrainingSet created: table={fs_table}, pk={pk}, exclude_columns={exclude_cols}")
                        else:
                            safe_print("No or multiple primary_keys provided; skip TrainingSet creation.", level="WARNING")
                            mlflow.log_text("No or multiple primary_keys provided; skip TrainingSet creation.", "artifacts/registration_warning.txt")

                    # Use client.log_model (with or without training_set)
                    log_kwargs = dict(
                        model=pipe,
                        artifact_path=cfg.get("artifact_path", "model"),
                        flavor=mlflow.sklearn,
                        registered_model_name=register_name,
                    )
                    if training_set_obj is not None:
                        log_kwargs["training_set"] = training_set_obj
                    _with_ts = training_set_obj is not None
                    safe_print(f"Calling WeData client.log_model: artifact_path={cfg.get('artifact_path', 'model')}, registered_model_name={register_name}, with_training_set={_with_ts}")

                    # Call client.log_model and get model version
                    model_info = client.log_model(**log_kwargs)

                    # Extract version from model_info if available
                    if hasattr(model_info, 'registered_model_version'):
                        version = int(model_info.registered_model_version)
                        safe_print(f"WeData 注册成功: {register_name} (版本: {version})", level="SUCCESS")
                    else:
                        safe_print(f"WeData 注册成功: {register_name} (版本信息不可用)", level="SUCCESS")

                    mlflow.log_text(register_name, "artifacts/registered_model_name.txt")
                    if version is not None:
                        mlflow.log_text(str(version), "artifacts/registered_model_version.txt")

                except Exception as e:
                    mlflow.log_text(str(e), "artifacts/registration_error.txt")
                    safe_print(f"WeData 注册失败: {str(e)}", level="ERROR")
                    # Keep logger.error for stack trace in logs
                    logger.error("WeData registration failed: %s", str(e), exc_info=True)

            else:
                # MLflow registration with detailed artifacts and metadata
                safe_print(f"使用 MLflow 注册: artifact_path={cfg.get('artifact_path', 'model')}, register_name={register_name}")

                try:
                    # 1. Log model with signature and input example
                    from mlflow.models.signature import infer_signature

                    # Infer model signature
                    signature = infer_signature(X_train, pipe.predict(X_train))
                    safe_print(f"模型签名已推断: inputs={signature.inputs}, outputs={signature.outputs}")

                    # Log model with all metadata
                    model_info = mlflow.sklearn.log_model(
                        sk_model=pipe,
                        artifact_path=cfg.get("artifact_path", "model"),
                        signature=signature,
                        input_example=input_example,
                        registered_model_name=register_name,
                        metadata={
                            "task": cfg["task"],
                            "metric": cfg["metric"],
                            "best_estimator": best_est,
                            "time_budget": cfg["time_budget"],
                            "framework": "flaml",
                            "framework_version": getattr(flaml_pkg, '__version__', 'unknown'),
                        }
                    )

                    # Extract version
                    if hasattr(model_info, 'registered_model_version'):
                        version = int(model_info.registered_model_version)
                    else:
                        version = None

                    safe_print(f"模型已记录到 MLflow: {model_info.model_uri}")

                    # 2. Log additional artifacts
                    safe_print("记录额外的 artifacts...")

                    # Log training configuration
                    import json
                    config_to_log = {
                        "task": cfg["task"],
                        "metric": cfg["metric"],
                        "time_budget": cfg["time_budget"],
                        "estimators": cfg.get("estimators", []),
                        "seed": cfg.get("seed", 42),
                        "best_estimator": best_est,
                        "best_config": best_cfg,
                        "split_config": cfg.get("split", {}),
                    }
                    mlflow.log_dict(config_to_log, "artifacts/training_config.json")
                    safe_print("✓ 训练配置已保存")

                    # Log dataset statistics
                    dataset_stats = {
                        "total_samples": len(pdf),
                        "train_samples": len(X_train),
                        "val_samples": len(X_val),
                        "test_samples": len(X_test),
                        "num_features": len(features),
                        "feature_columns": features,
                        "label_column": label,
                        "label_distribution": pdf[label].value_counts().to_dict() if cfg["task"] == "classification" else {},
                    }
                    mlflow.log_dict(dataset_stats, "artifacts/dataset_stats.json")
                    safe_print("✓ 数据集统计已保存")

                    # Log model performance summary
                    performance_summary = {
                        "best_estimator": best_est,
                        "best_loss": float(getattr(automl, 'best_loss', 0)),
                        "metrics": {}
                    }

                    # Collect all logged metrics
                    run = mlflow.active_run()
                    if run:
                        run_data = mlflow.get_run(run.info.run_id)
                        performance_summary["metrics"] = run_data.data.metrics

                    mlflow.log_dict(performance_summary, "artifacts/performance_summary.json")
                    safe_print("✓ 性能摘要已保存")

                    # 3. Log model tags
                    safe_print("添加模型标签...")
                    mlflow.set_tags({
                        "framework": "flaml",
                        "task": cfg["task"],
                        "best_estimator": best_est,
                        "metric": cfg["metric"],
                        "automl_engine": "flaml",
                        "model_type": "sklearn_pipeline",
                    })
                    safe_print("✓ 模型标签已添加")

                    # 4. Save registration info
                    mlflow.log_text(register_name, "artifacts/registered_model_name.txt")
                    if version is not None:
                        mlflow.log_text(str(version), "artifacts/registered_model_version.txt")

                    safe_print(f"MLflow 注册成功: {register_name} (版本: {version if version else 'N/A'})", level="SUCCESS")

                except Exception as e:
                    mlflow.log_text(str(e), "artifacts/registration_error.txt")
                    safe_print(f"MLflow 注册失败: {str(e)}", level="ERROR")
                    logger.error("MLflow registration failed: %s", str(e), exc_info=True)
        else:
            safe_print("模型注册已禁用。要启用注册，请设置 cfg['register']['enable']=True", level="WARNING")

        # Always log the computed model URI
        mlflow.log_text(uri, "artifacts/model_uri.txt")

        # Generate notebook code for retraining with best model
        safe_print("生成最佳模型训练 Notebook 代码...", level="INFO")
        try:
            notebook_code = generate_notebook_code(
                cfg=cfg,
                best_estimator=best_est,
                best_config=best_cfg,
                features=features,
                label=label,
                run_id=run.info.run_id if run else "unknown",
                experiment_name=experiment_name,
            )

            # Log notebook code as artifact
            mlflow.log_text(notebook_code, "artifacts/best_model_notebook.py")
            safe_print("✓ 最佳模型训练 Notebook 代码已生成: artifacts/best_model_notebook.py", level="SUCCESS")
            safe_print("  你可以使用这个 Notebook 代码重新训练最佳模型", level="INFO")
        except Exception as e:
            safe_print(f"⚠️  生成 Notebook 代码失败: {e}", level="WARNING")
            logger.warning("Failed to generate notebook code: %s", str(e), exc_info=True)

        # Collect all metrics for return
        run = mlflow.active_run()
        all_metrics = {}
        if run:
            run_data = mlflow.get_run(run.info.run_id)
            all_metrics = run_data.data.metrics

        # Print final summary to stdout
        print_section("AutoML 训练完成!")
        safe_print(f"最佳估计器: {best_est}", level="COMPLETE")
        safe_print(f"模型 URI: {uri}")
        safe_print(f"Run ID: {run.info.run_id if run else 'N/A'}")
        safe_print(f"模型版本: {version if version else 'N/A'}")

        # Print key metrics
        if all_metrics:
            safe_print("\n关键指标:")
            for metric_name in ['train_accuracy', 'val_accuracy', 'test_accuracy']:
                if metric_name in all_metrics:
                    safe_print(f"  {metric_name}: {all_metrics[metric_name]:.4f}")

        return {
            "best_estimator": best_est,
            "best_config": best_cfg,
            "model_uri": uri,
            "model_version": version,
            "run_id": run.info.run_id if run else None,
            **all_metrics,  # Include all metrics in return value
        }

