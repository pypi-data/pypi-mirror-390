from typing import Any, Dict, Optional

import mlflow


def run(cfg: Dict[str, Any], spark=None, pdf=None):
    """Skeleton for hyperopt + SparkTrials engine.

    Note: This V1 skeleton purposefully avoids importing hyperopt at import time.
    Raise a clear error if user selects this engine without proper deps.
    """
    try:
        from hyperopt import hp, tpe, fmin, STATUS_OK  # noqa: F401
        from hyperopt import SparkTrials  # noqa: F401
    except Exception as e:
        raise RuntimeError(
            "hyperopt/sparktrials engine requires 'hyperopt' and a Spark runtime.\n"
            "Please install hyperopt and run in a Spark-enabled environment."
        ) from e

    raise NotImplementedError(
        "sparktrials_engine is a placeholder in V1. Use engine=flaml for now."
    )

