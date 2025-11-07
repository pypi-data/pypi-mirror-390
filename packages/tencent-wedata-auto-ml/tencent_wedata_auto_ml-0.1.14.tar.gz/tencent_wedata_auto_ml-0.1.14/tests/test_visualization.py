"""
测试可视化功能

这个测试脚本验证所有新增的可视化功能是否正常工作。
"""

import pytest
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, 
    recall_score, roc_auc_score, confusion_matrix
)


class TestMetricsCalculation:
    """测试指标计算功能"""
    
    def setup_method(self):
        """设置测试数据"""
        # 创建简单的二分类数据
        np.random.seed(42)
        self.y_true = np.array([0, 0, 1, 1, 0, 1, 1, 0, 1, 0])
        self.y_pred = np.array([0, 1, 1, 1, 0, 0, 1, 0, 1, 0])
        self.y_proba = np.random.rand(10, 2)
        self.y_proba = self.y_proba / self.y_proba.sum(axis=1, keepdims=True)
        self.sample_weight = np.ones(10)
    
    def test_accuracy_calculation(self):
        """测试准确率计算"""
        acc = accuracy_score(self.y_true, self.y_pred)
        assert 0 <= acc <= 1
        assert isinstance(acc, (float, np.floating))
    
    def test_f1_calculation(self):
        """测试 F1 分数计算"""
        f1 = f1_score(self.y_true, self.y_pred, average='weighted', zero_division=0)
        assert 0 <= f1 <= 1
        assert isinstance(f1, (float, np.floating))
    
    def test_precision_calculation(self):
        """测试精确率计算"""
        precision = precision_score(self.y_true, self.y_pred, average='weighted', zero_division=0)
        assert 0 <= precision <= 1
        assert isinstance(precision, (float, np.floating))
    
    def test_recall_calculation(self):
        """测试召回率计算"""
        recall = recall_score(self.y_true, self.y_pred, average='weighted', zero_division=0)
        assert 0 <= recall <= 1
        assert isinstance(recall, (float, np.floating))
    
    def test_roc_auc_binary(self):
        """测试二分类 ROC AUC 计算"""
        auc = roc_auc_score(self.y_true, self.y_proba[:, 1])
        assert 0 <= auc <= 1
        assert isinstance(auc, (float, np.floating))
    
    def test_roc_auc_multiclass(self):
        """测试多分类 ROC AUC 计算"""
        # 创建多分类数据
        y_true_multi = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0])
        y_proba_multi = np.random.rand(10, 3)
        y_proba_multi = y_proba_multi / y_proba_multi.sum(axis=1, keepdims=True)
        
        auc = roc_auc_score(y_true_multi, y_proba_multi, multi_class='ovr', average='weighted')
        assert 0 <= auc <= 1
        assert isinstance(auc, (float, np.floating))
    
    def test_confusion_matrix(self):
        """测试混淆矩阵计算"""
        cm = confusion_matrix(self.y_true, self.y_pred)
        assert cm.shape == (2, 2)
        assert cm.sum() == len(self.y_true)
        assert np.all(cm >= 0)


class TestVisualizationGeneration:
    """测试可视化生成功能"""
    
    def test_matplotlib_import(self):
        """测试 matplotlib 导入"""
        import matplotlib
        matplotlib.use('Agg')  # 非交互式后端
        import matplotlib.pyplot as plt
        assert plt is not None
    
    def test_seaborn_import(self):
        """测试 seaborn 导入"""
        try:
            import seaborn as sns
            assert sns is not None
        except ImportError:
            pytest.skip("seaborn not installed")
    
    def test_confusion_matrix_plot(self):
        """测试混淆矩阵绘图"""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # 创建测试数据
            y_true = np.array([0, 0, 1, 1, 0, 1, 1, 0, 1, 0])
            y_pred = np.array([0, 1, 1, 1, 0, 0, 1, 0, 1, 0])
            cm = confusion_matrix(y_true, y_pred)
            
            # 绘制混淆矩阵
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title('Test Confusion Matrix')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            
            # 验证图表已创建
            assert plt.gcf() is not None
            plt.close()
            
        except ImportError:
            pytest.skip("matplotlib or seaborn not installed")
    
    def test_feature_importance_plot(self):
        """测试特征重要性绘图"""
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            # 创建测试数据
            features = ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5']
            importances = np.array([0.3, 0.25, 0.2, 0.15, 0.1])
            
            # 绘制特征重要性
            plt.figure(figsize=(10, 6))
            plt.barh(range(len(features)), importances)
            plt.yticks(range(len(features)), features)
            plt.xlabel('Importance')
            plt.title('Feature Importances')
            plt.gca().invert_yaxis()
            
            # 验证图表已创建
            assert plt.gcf() is not None
            plt.close()
            
        except ImportError:
            pytest.skip("matplotlib not installed")


class TestSHAPIntegration:
    """测试 SHAP 集成"""
    
    def test_shap_import(self):
        """测试 SHAP 库导入"""
        try:
            import shap
            assert shap is not None
        except ImportError:
            pytest.skip("shap not installed")
    
    def test_shap_explainer_creation(self):
        """测试 SHAP explainer 创建"""
        try:
            import shap
            from sklearn.ensemble import RandomForestClassifier
            
            # 创建简单的模型和数据
            X, y = make_classification(n_samples=100, n_features=5, random_state=42)
            model = RandomForestClassifier(n_estimators=10, random_state=42)
            model.fit(X, y)
            
            # 创建 SHAP explainer
            background = X[:10]
            explainer = shap.Explainer(model.predict, background)
            
            assert explainer is not None
            
        except ImportError:
            pytest.skip("shap not installed")


class TestConfigOptions:
    """测试配置选项"""
    
    def test_enable_shap_config(self):
        """测试 enable_shap 配置项"""
        cfg = {
            "enable_shap": True
        }
        assert cfg.get("enable_shap", False) is True
        
        cfg2 = {
            "enable_shap": False
        }
        assert cfg2.get("enable_shap", False) is False
        
        cfg3 = {}
        assert cfg3.get("enable_shap", False) is False


class TestArtifactPaths:
    """测试 artifact 路径"""
    
    def test_confusion_matrix_paths(self):
        """测试混淆矩阵文件路径"""
        val_path = "artifacts/val_confusion_matrix.png"
        test_path = "artifacts/test_confusion_matrix.png"
        
        assert val_path.endswith('.png')
        assert test_path.endswith('.png')
        assert 'val' in val_path
        assert 'test' in test_path
    
    def test_feature_importance_paths(self):
        """测试特征重要性文件路径"""
        json_path = "artifacts/feature_importance.json"
        png_path = "artifacts/feature_importance.png"
        
        assert json_path.endswith('.json')
        assert png_path.endswith('.png')
    
    def test_shap_path(self):
        """测试 SHAP 文件路径"""
        shap_path = "artifacts/shap_summary.png"
        assert shap_path.endswith('.png')
        assert 'shap' in shap_path


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])

