# wedata-automl

AutoML SDK for Tencent Cloud WeData, powered by FLAML and integrated with MLflow for experiment tracking and model registry.

## Features
- FLAML-based AutoML with graceful fallback to RandomForest
- MLflow integration: experiment tracking, model logging, and Model Registry registration
- Quiet, production-friendly logging helpers
- Simple pipeline API and CLI demo

## Installation

```bash
pip install wedata-automl
# Optional extras
pip install "wedata-automl[xgboost]"
pip install "wedata-automl[lightgbm]"
```

## Quickstart (Python API)

```python
from wedata_automl import run_pipeline

# Uses a demo dataset by default, and creates/uses the specified MLflow experiment
result = run_pipeline(experiment_name="blueszzhang-test-automl")
print(result)
```

## Quickstart (CLI)

```bash
wedata-automl-demo
```

## Notes
- Ensure MLflow Tracking/Registry is configured in your environment (MLFLOW_TRACKING_URI, credentials, etc.)
- XGBoost/LightGBM are optional; install via extras if you want those estimators considered
- Python >= 3.8

## License
MIT
