import json
from typing import Iterable, Mapping
import mlflow


def log_feature_list(features: Iterable[str]) -> None:
    mlflow.log_text("\n".join(features), "artifacts/feature_list.txt")


def log_engine_meta(meta: Mapping) -> None:
    mlflow.log_dict(dict(meta), "artifacts/engine_meta.json")


def log_best_config_overall(cfg: Mapping) -> None:
    mlflow.log_dict(dict(cfg), "artifacts/fl_best_config_overall.json")


def log_best_config_per_estimator(cfgs: Mapping[str, Mapping]) -> None:
    if cfgs:
        mlflow.log_dict({k: dict(v) for k, v in cfgs.items()}, "artifacts/fl_best_config_per_estimator.json")

