from typing import Any, Dict, Union


def normalize_config(cfg: Union[Dict[str, Any], None]) -> Dict[str, Any]:
    """Normalize user config with safe defaults."""
    cfg = dict(cfg or {})
    cfg.setdefault("engine", "flaml")
    cfg.setdefault("task", "classification")
    cfg.setdefault("metric", "accuracy" if cfg["task"] == "classification" else "rmse")
    cfg.setdefault("time_budget", 300)
    cfg.setdefault("seed", 42)
    cfg.setdefault("disable_cols", [])
    cfg.setdefault("log_level", "INFO")
    cfg.setdefault("limit_rows", None)  # None = no limit, or set to positive integer
    cfg.setdefault("flaml_verbose", True)  # True = verbose training logs, False = silent
    cfg.setdefault("experiment_name", "wedata_automl")  # MLflow experiment name

    # split settings: train/val/test ratios and stratify flag
    split = cfg.setdefault("split", {})
    split.setdefault("train_ratio", 0.6)
    split.setdefault("val_ratio", 0.2)
    split.setdefault("test_ratio", 0.2)
    split.setdefault("stratify", cfg["task"] == "classification")

    # registration settings: prefer wedata client by default
    reg = cfg.setdefault("register", {})
    reg.setdefault("enable", False)
    reg.setdefault("backend", "wedata")  # wedata | mlflow
    reg.setdefault("model_name", "wedata_model")
    reg.setdefault("per_candidate", False)

    # feature store settings (used when backend=wedata)
    fs = cfg.setdefault("feature_store", {})
    fs.setdefault("table_name", cfg.get("table"))
    fs.setdefault("primary_keys", [])  # e.g., ["id"]
    fs.setdefault("exclude_columns", [])
    fs.setdefault("use_training_set", True)

    return cfg

