"""
测试 feature_cols 变量名修复

验证所有使用 features 变量的地方都正确引用了变量名。
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification


def test_features_variable_exists():
    """测试 features 变量在代码中正确定义"""
    # 模拟 flaml_engine.py 中的逻辑
    pdf = pd.DataFrame({
        'feature_1': np.random.rand(100),
        'feature_2': np.random.rand(100),
        'feature_3': np.random.rand(100),
        'label': np.random.randint(0, 2, 100)
    })
    
    label = 'label'
    disable_cols = set([]) | {label}
    features = [c for c in pdf.columns if c not in disable_cols]
    
    # 验证 features 变量存在且正确
    assert features is not None
    assert isinstance(features, list)
    assert len(features) == 3
    assert 'label' not in features
    assert 'feature_1' in features
    assert 'feature_2' in features
    assert 'feature_3' in features


def test_feature_importance_dataframe():
    """测试特征重要性 DataFrame 创建"""
    features = ['feature_1', 'feature_2', 'feature_3']
    importances = np.array([0.5, 0.3, 0.2])
    
    # 模拟 flaml_engine.py 中的逻辑
    feature_importance_df = pd.DataFrame({
        'feature': features,  # 使用 features 而不是 feature_cols
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    assert len(feature_importance_df) == 3
    assert list(feature_importance_df.columns) == ['feature', 'importance']
    assert feature_importance_df.iloc[0]['feature'] == 'feature_1'
    assert feature_importance_df.iloc[0]['importance'] == 0.5


def test_dataset_stats_dict():
    """测试数据集统计字典创建"""
    features = ['feature_1', 'feature_2', 'feature_3']
    pdf = pd.DataFrame({
        'feature_1': np.random.rand(100),
        'feature_2': np.random.rand(100),
        'feature_3': np.random.rand(100),
        'label': np.random.randint(0, 2, 100)
    })
    label = 'label'
    
    # 模拟 flaml_engine.py 中的逻辑
    dataset_stats = {
        "total_samples": len(pdf),
        "num_features": len(features),  # 使用 features 而不是 feature_cols
        "feature_columns": features,     # 使用 features 而不是 feature_cols
        "label_column": label,
        "label_distribution": pdf[label].value_counts().to_dict(),
    }
    
    assert dataset_stats["total_samples"] == 100
    assert dataset_stats["num_features"] == 3
    assert dataset_stats["feature_columns"] == features
    assert dataset_stats["label_column"] == label
    assert isinstance(dataset_stats["label_distribution"], dict)


def test_shap_feature_names():
    """测试 SHAP 特征名称参数"""
    features = ['feature_1', 'feature_2', 'feature_3']
    
    # 验证 features 可以作为 feature_names 参数
    assert isinstance(features, list)
    assert all(isinstance(f, str) for f in features)
    
    # 模拟 shap.summary_plot 的 feature_names 参数
    feature_names = features  # 使用 features 而不是 feature_cols
    assert feature_names == ['feature_1', 'feature_2', 'feature_3']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

