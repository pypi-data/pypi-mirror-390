from typing import Mapping, Any
import io
import yaml
import mlflow


def log_feature_spec(spec: Mapping[str, Any]) -> None:
    """Optional: record feature spec/lineage placeholder into artifacts."""
    buf = io.StringIO()
    yaml.safe_dump(dict(spec), buf, allow_unicode=True, sort_keys=False)
    mlflow.log_text(buf.getvalue(), "artifacts/feature_store/feature_spec.yaml")



