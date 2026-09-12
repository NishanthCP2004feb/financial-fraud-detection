"""
Custom sklearn transformers for the Financial Fraud Detection pipeline.

This module provides the DateFeatureEngineer transformer that is used
inside the serialized model pipeline. It MUST be importable for
joblib.load() to deserialize the pipeline outside of the notebook.

Usage:
    from src.transformers import DateFeatureEngineer
"""

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class DateFeatureEngineer(BaseEstimator, TransformerMixin):
    """
    Sklearn-compatible transformer for date feature engineering.

    Converts the raw 'Date' string column into four numeric features:
    Year, Month, Day, Day_of_Week (Monday=0, Sunday=6).

    Also drops identifier columns (Transaction_ID, User_ID) and the
    raw Date column so the downstream ColumnTransformer receives only
    modelling features.
    """

    def __init__(self, date_col="Date", date_format="%d %B %Y",
                 drop_cols=None):
        self.date_col = date_col
        self.date_format = date_format
        self.drop_cols = drop_cols if drop_cols is not None else [
            "Transaction_ID", "User_ID"
        ]

    def fit(self, X, y=None):
        """Nothing to learn — stateless transformation."""
        return self

    def transform(self, X, y=None):
        """Apply date feature engineering and column cleanup."""
        df = X.copy()

        # Parse date
        df[self.date_col] = pd.to_datetime(
            df[self.date_col], format=self.date_format, errors="coerce"
        )

        # Extract date components
        df["Year"] = df[self.date_col].dt.year
        df["Month"] = df[self.date_col].dt.month
        df["Day"] = df[self.date_col].dt.day
        df["Day_of_Week"] = df[self.date_col].dt.dayofweek

        # Drop identifier and raw date columns
        cols_to_drop = [c for c in self.drop_cols + [self.date_col]
                        if c in df.columns]
        df = df.drop(columns=cols_to_drop)

        return df

    def get_feature_names_out(self, input_features=None):
        """Return output feature names (informational)."""
        # Will be determined dynamically by ColumnTransformer
        return None
