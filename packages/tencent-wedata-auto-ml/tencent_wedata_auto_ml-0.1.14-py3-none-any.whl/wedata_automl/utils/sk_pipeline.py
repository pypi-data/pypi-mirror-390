import pandas as pd
from sklearn.pipeline import Pipeline as SkPipe
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.impute import SimpleImputer


def _to_numeric_df(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({c: pd.to_numeric(df[c], errors="coerce") for c in df.columns})


def build_numeric_preprocessor(feature_cols):
    num_pipe = SkPipe(steps=[
        ("to_numeric", FunctionTransformer(_to_numeric_df, feature_names_out="one-to-one")),
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    return ColumnTransformer(
        transformers=[("num", num_pipe, feature_cols)],
        remainder="drop",
        sparse_threshold=0,
        verbose_feature_names_out=False,
    )

