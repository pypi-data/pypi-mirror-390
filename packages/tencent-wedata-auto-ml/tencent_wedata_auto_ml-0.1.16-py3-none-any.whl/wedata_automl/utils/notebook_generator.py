"""
Notebook 代码生成器

在 AutoML 训练完成后，生成一个可执行的 Notebook 代码，
使用最佳估计器和最佳超参数重新训练模型。
"""

import json
from typing import Dict, Any, List


def generate_notebook_code(
    cfg: Dict[str, Any],
    best_estimator: str,
    best_config: Dict[str, Any],
    features: List[str],
    label: str,
    run_id: str,
    experiment_name: str,
) -> str:
    """
    生成 Notebook 代码
    
    Args:
        cfg: AutoML 配置
        best_estimator: 最佳估计器名称
        best_config: 最佳超参数配置
        features: 特征列表
        label: 标签列名
        run_id: MLflow run ID
        experiment_name: MLflow 实验名称
    
    Returns:
        str: Notebook 代码（Python 格式）
    """
    
    # 提取配置信息
    table_name = cfg.get("table", "your_table")
    task = cfg.get("task", "classification")
    metric = cfg.get("metric", "accuracy")
    split_config = cfg.get("split", {})
    train_ratio = split_config.get("train_ratio", 0.6)
    val_ratio = split_config.get("val_ratio", 0.2)
    test_ratio = split_config.get("test_ratio", 0.2)
    stratify = split_config.get("stratify", True)
    seed = cfg.get("seed", 42)
    
    # 注册配置
    register_config = cfg.get("register", {})
    model_name = register_config.get("model_name", "automl_model")
    
    # 特征工程配置
    feature_store_config = cfg.get("feature_store", {})
    use_feature_store = feature_store_config.get("use_training_set", False)
    feature_table_name = feature_store_config.get("table_name", "")
    primary_keys = feature_store_config.get("primary_keys", [])
    
    # 估计器映射
    estimator_map = {
        "lgbm": "LGBMClassifier" if task == "classification" else "LGBMRegressor",
        "xgboost": "XGBClassifier" if task == "classification" else "XGBRegressor",
        "rf": "RandomForestClassifier" if task == "classification" else "RandomForestRegressor",
        "extra_tree": "ExtraTreesClassifier" if task == "classification" else "ExtraTreesRegressor",
        "lrl1": "LogisticRegression" if task == "classification" else "Ridge",
        "lrl2": "LogisticRegression" if task == "classification" else "Ridge",
    }
    
    estimator_class = estimator_map.get(best_estimator, "RandomForestClassifier")
    
    # 导入语句映射
    import_map = {
        "LGBMClassifier": "from lightgbm import LGBMClassifier",
        "LGBMRegressor": "from lightgbm import LGBMRegressor",
        "XGBClassifier": "from xgboost import XGBClassifier",
        "XGBRegressor": "from xgboost import XGBRegressor",
        "RandomForestClassifier": "from sklearn.ensemble import RandomForestClassifier",
        "RandomForestRegressor": "from sklearn.ensemble import RandomForestRegressor",
        "ExtraTreesClassifier": "from sklearn.ensemble import ExtraTreesClassifier",
        "ExtraTreesRegressor": "from sklearn.ensemble import ExtraTreesRegressor",
        "LogisticRegression": "from sklearn.linear_model import LogisticRegression",
        "Ridge": "from sklearn.linear_model import Ridge",
    }
    
    estimator_import = import_map.get(estimator_class, "from sklearn.ensemble import RandomForestClassifier")
    
    # 格式化超参数
    params_str = json.dumps(best_config, indent=4)
    
    # 格式化特征列表
    features_str = json.dumps(features, indent=4)
    
    # 生成代码
    code = f'''# %% [markdown]
# # AutoML 最佳模型训练 Notebook
# 
# 本 Notebook 由 WeData AutoML 自动生成，使用最佳估计器和最佳超参数重新训练模型。
# 
# **AutoML 训练信息**:
# - 实验名称: {experiment_name}
# - Run ID: {run_id}
# - 最佳估计器: {best_estimator}
# - 任务类型: {task}
# - 评估指标: {metric}

# %% [markdown]
# ## 1. 安装依赖包

# %%
# 安装 WeData 特征工程包（如果使用特征库）
%pip install tencent-wedata-feature-engineering==0.1.33 -i https://mirrors.tencent.com/pypi/simple --trusted-host mirrors.tencent.com

# %% [markdown]
# ## 2. 导入必要的库

# %%
import os
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, 
    roc_auc_score, confusion_matrix, classification_report
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
{estimator_import}

# 可视化库
import matplotlib.pyplot as plt
import seaborn as sns

# 设置随机种子
np.random.seed({seed})

print("✓ 库导入完成")

# %% [markdown]
# ## 3. 配置信息

# %%
# 数据配置
TABLE_NAME = "{table_name}"
LABEL_COL = "{label}"
FEATURE_COLS = {features_str}

# 训练配置
TASK = "{task}"
METRIC = "{metric}"
RANDOM_SEED = {seed}

# 数据划分配置
TRAIN_RATIO = {train_ratio}
VAL_RATIO = {val_ratio}
TEST_RATIO = {test_ratio}
STRATIFY = {stratify}

# 模型配置
BEST_ESTIMATOR = "{best_estimator}"
BEST_PARAMS = {params_str}

# 注册配置
MODEL_NAME = "{model_name}"
EXPERIMENT_NAME = "{experiment_name}_retrain"

# 特征库配置
USE_FEATURE_STORE = {use_feature_store}
FEATURE_TABLE_NAME = "{feature_table_name}"
PRIMARY_KEYS = {json.dumps(primary_keys)}

print("✓ 配置加载完成")
print(f"  - 表名: {{TABLE_NAME}}")
print(f"  - 标签列: {{LABEL_COL}}")
print(f"  - 特征数: {{len(FEATURE_COLS)}}")
print(f"  - 最佳估计器: {{BEST_ESTIMATOR}}")

# %% [markdown]
# ## 4. 读取数据

# %%
if USE_FEATURE_STORE:
    # 使用 WeData 特征库
    from wedata.feature_store.client import FeatureStoreClient
    from wedata.feature_store.entities.feature_lookup import FeatureLookup
    
    # 构建特征工程客户端
    client = FeatureStoreClient(spark)
    
    # 读取基础数据（包含标签）
    base_df = spark.read.table(TABLE_NAME)
    
    # 定义特征查找
    feature_lookup = FeatureLookup(
        table_name=FEATURE_TABLE_NAME,
        lookup_key=PRIMARY_KEYS[0] if PRIMARY_KEYS else "id"
    )
    
    # 创建训练集
    training_set = client.create_training_set(
        df=base_df,
        feature_lookups=[feature_lookup],
        label=LABEL_COL,
        exclude_columns=PRIMARY_KEYS
    )
    
    # 加载训练数据
    df = training_set.load_df().toPandas()
    
    print(f"✓ 从特征库加载数据: {{len(df)}} 行")
else:
    # 直接从表读取
    df = spark.read.table(TABLE_NAME).toPandas()
    print(f"✓ 从表加载数据: {{len(df)}} 行")

# 显示数据信息
print(f"\\n数据形状: {{df.shape}}")
print(f"标签分布:\\n{{df[LABEL_COL].value_counts()}}")

# 显示前几行
display(df.head())

# %% [markdown]
# ## 5. 数据划分

# %%
# 准备特征和标签
X = df[FEATURE_COLS]
y = df[LABEL_COL]

# 第一次划分: train+val vs test
if STRATIFY and TASK == "classification":
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=TEST_RATIO, random_state=RANDOM_SEED, stratify=y
    )
else:
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=TEST_RATIO, random_state=RANDOM_SEED
    )

# 第二次划分: train vs val
val_ratio_adjusted = VAL_RATIO / (TRAIN_RATIO + VAL_RATIO)
if STRATIFY and TASK == "classification":
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio_adjusted, random_state=RANDOM_SEED, stratify=y_temp
    )
else:
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_ratio_adjusted, random_state=RANDOM_SEED
    )

print("✓ 数据划分完成")
print(f"  - 训练集: {{len(X_train)}} 行 ({{len(X_train)/len(X)*100:.1f}}%)")
print(f"  - 验证集: {{len(X_val)}} 行 ({{len(X_val)/len(X)*100:.1f}}%)")
print(f"  - 测试集: {{len(X_test)}} 行 ({{len(X_test)/len(X)*100:.1f}}%)")

# %% [markdown]
# ## 6. 创建和训练模型

# %%
# 设置 MLflow 实验
mlflow.set_experiment(EXPERIMENT_NAME)

# 开始 MLflow run
with mlflow.start_run(run_name=f"{{BEST_ESTIMATOR}}_retrain") as run:
    run_id = run.info.run_id
    print(f"MLflow Run ID: {{run_id}}")
    
    # 记录参数
    mlflow.log_params({{
        "table": TABLE_NAME,
        "label": LABEL_COL,
        "n_rows": len(df),
        "n_features": len(FEATURE_COLS),
        "task": TASK,
        "metric": METRIC,
        "estimator": BEST_ESTIMATOR,
        "train_ratio": TRAIN_RATIO,
        "val_ratio": VAL_RATIO,
        "test_ratio": TEST_RATIO,
        "random_seed": RANDOM_SEED,
    }})
    
    # 记录超参数
    for key, value in BEST_PARAMS.items():
        mlflow.log_param(f"model__{{key}}", value)
    
    # 创建预处理器
    preprocessor = StandardScaler()
    
    # 创建模型
    model = {estimator_class}(**BEST_PARAMS, random_state=RANDOM_SEED)
    
    # 创建 Pipeline
    pipeline = Pipeline([
        ("preprocess", preprocessor),
        ("clf", model)
    ])
    
    print("\\n开始训练...")
    pipeline.fit(X_train, y_train)
    print("✓ 训练完成")
    
    # 预测
    y_train_pred = pipeline.predict(X_train)
    y_val_pred = pipeline.predict(X_val)
    y_test_pred = pipeline.predict(X_test)
    
    # 计算指标
    train_acc = accuracy_score(y_train, y_train_pred)
    val_acc = accuracy_score(y_val, y_val_pred)
    test_acc = accuracy_score(y_test, y_test_pred)
    
    train_f1 = f1_score(y_train, y_train_pred, average='weighted', zero_division=0)
    val_f1 = f1_score(y_val, y_val_pred, average='weighted', zero_division=0)
    test_f1 = f1_score(y_test, y_test_pred, average='weighted', zero_division=0)
    
    train_precision = precision_score(y_train, y_train_pred, average='weighted', zero_division=0)
    val_precision = precision_score(y_val, y_val_pred, average='weighted', zero_division=0)
    test_precision = precision_score(y_test, y_test_pred, average='weighted', zero_division=0)
    
    train_recall = recall_score(y_train, y_train_pred, average='weighted', zero_division=0)
    val_recall = recall_score(y_val, y_val_pred, average='weighted', zero_division=0)
    test_recall = recall_score(y_test, y_test_pred, average='weighted', zero_division=0)
    
    # 记录指标
    mlflow.log_metrics({{
        "train_accuracy": train_acc,
        "val_accuracy": val_acc,
        "test_accuracy": test_acc,
        "train_f1": train_f1,
        "val_f1": val_f1,
        "test_f1": test_f1,
        "train_precision": train_precision,
        "val_precision": val_precision,
        "test_precision": test_precision,
        "train_recall": train_recall,
        "val_recall": val_recall,
        "test_recall": test_recall,
    }})
    
    print("\\n✓ 评估指标:")
    print(f"  训练集 - Accuracy: {{train_acc:.4f}}, F1: {{train_f1:.4f}}")
    print(f"  验证集 - Accuracy: {{val_acc:.4f}}, F1: {{val_f1:.4f}}")
    print(f"  测试集 - Accuracy: {{test_acc:.4f}}, F1: {{test_f1:.4f}}")

# %% [markdown]
# ## 7. 生成可视化

# %%
# 混淆矩阵 - 验证集
cm_val = confusion_matrix(y_val, y_val_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm_val, annot=True, fmt='d', cmap='Blues')
plt.title('Validation Set Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
mlflow.log_figure(plt.gcf(), "artifacts/val_confusion_matrix.png")
plt.show()

# 混淆矩阵 - 测试集
cm_test = confusion_matrix(y_test, y_test_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm_test, annot=True, fmt='d', cmap='Blues')
plt.title('Test Set Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.tight_layout()
mlflow.log_figure(plt.gcf(), "artifacts/test_confusion_matrix.png")
plt.show()

print("✓ 混淆矩阵已生成")

# %%
# 特征重要性（如果模型支持）
if hasattr(pipeline.named_steps['clf'], 'feature_importances_'):
    importances = pipeline.named_steps['clf'].feature_importances_
    feature_importance_df = pd.DataFrame({{
        'feature': FEATURE_COLS,
        'importance': importances
    }}).sort_values('importance', ascending=False)
    
    # 保存 JSON
    mlflow.log_dict(feature_importance_df.to_dict('records'), "artifacts/feature_importance.json")
    
    # 绘制图表
    plt.figure(figsize=(10, 6))
    top_n = min(20, len(feature_importance_df))
    sns.barplot(data=feature_importance_df.head(top_n), x='importance', y='feature')
    plt.title(f'Top {{top_n}} Feature Importances')
    plt.xlabel('Importance')
    plt.tight_layout()
    mlflow.log_figure(plt.gcf(), "artifacts/feature_importance.png")
    plt.show()
    
    print("✓ 特征重要性已生成")
else:
    print("⚠️  模型不支持特征重要性")

# %% [markdown]
# ## 8. 注册模型

# %%
with mlflow.start_run(run_id=run_id):
    # 推断模型签名
    from mlflow.models.signature import infer_signature
    signature = infer_signature(X_train, pipeline.predict(X_train))
    
    # 准备输入示例
    input_example = X_train.head(5)
    
    # 记录模型
    model_info = mlflow.sklearn.log_model(
        sk_model=pipeline,
        artifact_path="model",
        signature=signature,
        input_example=input_example,
        registered_model_name=MODEL_NAME,
        metadata={{
            "task": TASK,
            "metric": METRIC,
            "best_estimator": BEST_ESTIMATOR,
            "framework": "sklearn",
            "source": "wedata_automl_retrain",
        }}
    )
    
    # 获取模型版本
    if hasattr(model_info, 'registered_model_version'):
        version = int(model_info.registered_model_version)
    else:
        version = None
    
    # 记录额外的 artifacts
    mlflow.log_dict({{
        "feature_columns": FEATURE_COLS,
        "label_column": LABEL_COL,
        "best_params": BEST_PARAMS,
    }}, "artifacts/model_config.json")
    
    mlflow.log_dict({{
        "total_samples": len(df),
        "train_samples": len(X_train),
        "val_samples": len(X_val),
        "test_samples": len(X_test),
        "num_features": len(FEATURE_COLS),
    }}, "artifacts/dataset_stats.json")
    
    # 添加标签
    mlflow.set_tags({{
        "framework": "sklearn",
        "task": TASK,
        "estimator": BEST_ESTIMATOR,
        "metric": METRIC,
        "source": "wedata_automl_retrain",
    }})
    
    print(f"\\n✓ 模型已注册: {{MODEL_NAME}}")
    print(f"  - 版本: {{version if version else 'N/A'}}")
    print(f"  - URI: {{model_info.model_uri}}")

# %% [markdown]
# ## 9. 模型推理测试

# %%
# 加载注册的模型
model_uri = f"models:/{{MODEL_NAME}}/{{version if version else 'latest'}}"
loaded_model = mlflow.pyfunc.load_model(model_uri)

print(f"✓ 模型已加载: {{model_uri}}")

# 准备推理数据（使用测试集的前 5 行）
inference_data = X_test.head(5)

# 执行推理
predictions = loaded_model.predict(inference_data)

# 显示结果
result_df = inference_data.copy()
result_df['prediction'] = predictions
result_df['actual'] = y_test.head(5).values

print("\\n推理结果:")
display(result_df)

# %% [markdown]
# ## 10. 总结

# %%
print("="*80)
print("模型训练和注册完成!")
print("="*80)
print(f"实验名称: {{EXPERIMENT_NAME}}")
print(f"Run ID: {{run_id}}")
print(f"模型名称: {{MODEL_NAME}}")
print(f"模型版本: {{version if version else 'N/A'}}")
print(f"\\n关键指标:")
print(f"  - 验证集 Accuracy: {{val_acc:.4f}}")
print(f"  - 测试集 Accuracy: {{test_acc:.4f}}")
print(f"  - 验证集 F1: {{val_f1:.4f}}")
print(f"  - 测试集 F1: {{test_f1:.4f}}")
print("="*80)
print("\\n💡 下一步:")
print("  1. 在 MLflow UI 中查看实验详情")
print("  2. 部署模型到生产环境")
print("  3. 监控模型性能")
print("="*80)
'''
    
    return code


def save_notebook_code(code: str, output_path: str):
    """
    保存 Notebook 代码到文件
    
    Args:
        code: Notebook 代码
        output_path: 输出文件路径
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code)

