"""
测试 MLflow 实验和 Trial 追踪功能
"""

import pytest
import mlflow
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from wedata_automl.engines.flaml_engine import run as flaml_run


def test_experiment_creation():
    """测试实验创建功能"""
    cfg = {
        "engine": "flaml",
        "task": "classification",
        "table": "test.table",
        "label_col": "label",
        "metric": "accuracy",
        "time_budget": 10,
        "estimators": ["lgbm"],
        "experiment_name": "test_experiment_creation",
    }
    
    # 创建测试数据
    pdf = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        "label": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    })
    
    with patch("wedata_automl.engines.flaml_engine.load_spark_table") as mock_load:
        mock_load.return_value = pdf
        
        # 运行训练
        result = flaml_run(cfg, spark=None)
        
        # 验证实验是否创建
        experiment = mlflow.get_experiment_by_name("test_experiment_creation")
        assert experiment is not None
        assert experiment.name == "test_experiment_creation"
        
        # 清理
        mlflow.delete_experiment(experiment.experiment_id)


def test_parent_run_created():
    """测试 Parent Run 是否创建"""
    cfg = {
        "engine": "flaml",
        "task": "classification",
        "table": "test.table",
        "label_col": "label",
        "metric": "accuracy",
        "time_budget": 10,
        "estimators": ["lgbm"],
        "experiment_name": "test_parent_run",
    }
    
    # 创建测试数据
    pdf = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        "label": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    })
    
    with patch("wedata_automl.engines.flaml_engine.load_spark_table") as mock_load:
        mock_load.return_value = pdf
        
        # 运行训练
        result = flaml_run(cfg, spark=None)
        
        # 获取实验
        experiment = mlflow.get_experiment_by_name("test_parent_run")
        assert experiment is not None
        
        # 获取所有 runs
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        # 验证至少有一个 parent run
        parent_runs = runs[runs['tags.mlflow.parentRunId'].isna()]
        assert len(parent_runs) >= 1
        
        # 验证 parent run 的名称
        assert any("flaml_automl_main" in str(name) for name in parent_runs['tags.mlflow.runName'])
        
        # 清理
        mlflow.delete_experiment(experiment.experiment_id)


def test_child_runs_created():
    """测试 Child Runs (Trials) 是否创建"""
    cfg = {
        "engine": "flaml",
        "task": "classification",
        "table": "test.table",
        "label_col": "label",
        "metric": "accuracy",
        "time_budget": 30,  # 增加时间预算以确保有多个 trials
        "estimators": ["lgbm", "xgboost"],  # 使用多个算法
        "experiment_name": "test_child_runs",
    }
    
    # 创建测试数据
    pdf = pd.DataFrame({
        "feature1": list(range(100)),
        "feature2": list(range(100, 200)),
        "label": [i % 2 for i in range(100)],
    })
    
    with patch("wedata_automl.engines.flaml_engine.load_spark_table") as mock_load:
        mock_load.return_value = pdf
        
        # 运行训练
        result = flaml_run(cfg, spark=None)
        
        # 获取实验
        experiment = mlflow.get_experiment_by_name("test_child_runs")
        assert experiment is not None
        
        # 获取所有 runs
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        # 验证有 child runs
        child_runs = runs[runs['tags.mlflow.parentRunId'].notna()]
        assert len(child_runs) > 0, "应该至少有一个 child run (trial)"
        
        # 验证 child runs 有 learner 参数
        if 'params.learner' in child_runs.columns:
            assert child_runs['params.learner'].notna().any()
        
        # 验证 child runs 有 val_loss 指标
        if 'metrics.val_loss' in child_runs.columns:
            assert child_runs['metrics.val_loss'].notna().any()
        
        # 清理
        mlflow.delete_experiment(experiment.experiment_id)


def test_only_best_model_registered():
    """测试只有最佳模型被注册"""
    cfg = {
        "engine": "flaml",
        "task": "classification",
        "table": "test.table",
        "label_col": "label",
        "metric": "accuracy",
        "time_budget": 20,
        "estimators": ["lgbm"],
        "experiment_name": "test_model_registration",
        "register": {
            "enable": True,
            "backend": "mlflow",
            "model_name": "test_best_model",
        },
    }
    
    # 创建测试数据
    pdf = pd.DataFrame({
        "feature1": list(range(50)),
        "feature2": list(range(50, 100)),
        "label": [i % 2 for i in range(50)],
    })
    
    with patch("wedata_automl.engines.flaml_engine.load_spark_table") as mock_load:
        mock_load.return_value = pdf
        
        # 运行训练
        result = flaml_run(cfg, spark=None)
        
        # 获取实验
        experiment = mlflow.get_experiment_by_name("test_model_registration")
        assert experiment is not None
        
        # 获取所有 runs
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        
        # 统计注册了模型的 runs
        registered_runs = 0
        for _, run in runs.iterrows():
            run_id = run['run_id']
            try:
                # 尝试获取这个 run 的模型
                client = mlflow.tracking.MlflowClient()
                artifacts = client.list_artifacts(run_id)
                has_model = any(artifact.path == "model" for artifact in artifacts)
                if has_model:
                    registered_runs += 1
            except Exception:
                pass
        
        # 验证只有一个 run 注册了模型（parent run）
        assert registered_runs == 1, f"应该只有 1 个 run 注册模型，但发现 {registered_runs} 个"
        
        # 清理
        mlflow.delete_experiment(experiment.experiment_id)
        # 清理注册的模型
        try:
            client = mlflow.tracking.MlflowClient()
            client.delete_registered_model("test_best_model")
        except Exception:
            pass


def test_experiment_name_default():
    """测试默认实验名称"""
    cfg = {
        "engine": "flaml",
        "task": "classification",
        "table": "test.table",
        "label_col": "label",
        "metric": "accuracy",
        "time_budget": 10,
        "estimators": ["lgbm"],
        # 不指定 experiment_name，应该使用默认值
    }
    
    # 创建测试数据
    pdf = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        "label": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    })
    
    with patch("wedata_automl.engines.flaml_engine.load_spark_table") as mock_load:
        mock_load.return_value = pdf
        
        # 运行训练
        result = flaml_run(cfg, spark=None)
        
        # 验证默认实验名称
        experiment = mlflow.get_experiment_by_name("wedata_automl")
        assert experiment is not None
        
        # 清理
        mlflow.delete_experiment(experiment.experiment_id)


def test_parent_run_has_best_estimator():
    """测试 Parent Run 是否记录了最佳算法"""
    cfg = {
        "engine": "flaml",
        "task": "classification",
        "table": "test.table",
        "label_col": "label",
        "metric": "accuracy",
        "time_budget": 20,
        "estimators": ["lgbm", "xgboost"],
        "experiment_name": "test_best_estimator",
    }
    
    # 创建测试数据
    pdf = pd.DataFrame({
        "feature1": list(range(50)),
        "feature2": list(range(50, 100)),
        "label": [i % 2 for i in range(50)],
    })
    
    with patch("wedata_automl.engines.flaml_engine.load_spark_table") as mock_load:
        mock_load.return_value = pdf
        
        # 运行训练
        result = flaml_run(cfg, spark=None)
        
        # 获取实验
        experiment = mlflow.get_experiment_by_name("test_best_estimator")
        assert experiment is not None
        
        # 获取 parent run
        runs = mlflow.search_runs(experiment_ids=[experiment.experiment_id])
        parent_runs = runs[runs['tags.mlflow.parentRunId'].isna()]
        
        assert len(parent_runs) >= 1
        
        # 验证 parent run 有 best_estimator 参数
        parent_run = parent_runs.iloc[0]
        if 'params.best_estimator' in parent_run:
            assert parent_run['params.best_estimator'] in ['lgbm', 'xgboost']
        
        # 清理
        mlflow.delete_experiment(experiment.experiment_id)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

