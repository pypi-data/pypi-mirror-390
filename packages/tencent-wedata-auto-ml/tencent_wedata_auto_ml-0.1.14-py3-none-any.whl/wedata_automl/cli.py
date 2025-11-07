import argparse
import json
import sys
from typing import Any, Dict

from wedata_automl.utils.mlflow_utils import ensure_mlflow
from wedata_automl.engines.flaml_engine import run as run_flaml
try:
    from wedata_automl.engines.sparktrials_engine import run as run_sparktrials
except Exception:
    run_sparktrials = None  # optional


def _load_config(path: str) -> Dict[str, Any]:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg


def main(argv=None):
    argv = argv or sys.argv[1:]
    ap = argparse.ArgumentParser(description="WeData AutoML CLI")
    ap.add_argument("--config", required=True, help="Path to YAML config file")
    args = ap.parse_args(argv)

    cfg = _load_config(args.config)
    ensure_mlflow(cfg.get("tracking",{}).get("uri"), cfg.get("experiment_name","we_automl"))

    # Spark may be provided by notebook environment
    spark = None
    try:
        from pyspark.sql import SparkSession  # noqa
        from pyspark import __version__ as _  # noqa
        spark = SparkSession.builder.getOrCreate()
    except Exception:
        spark = None

    engine = cfg.get("engine", "flaml").lower()
    if engine == "flaml":
        run_flaml(cfg, spark, None)
    elif engine in ("hyperopt_sparktrials", "sparktrials"):
        if run_sparktrials is None:
            raise RuntimeError("hyperopt/sparktrials engine not available. Please install hyperopt and use a Spark runtime.")
        run_sparktrials(cfg, spark, None)
    else:
        raise ValueError(f"Unknown engine: {engine}")


if __name__ == "__main__":
    main()

