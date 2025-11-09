# src/TextPreprocessingToolkit/numerical_preprocessor.py
from __future__ import annotations

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Literal, Optional
from sklearn.preprocessing import StandardScaler, MinMaxScaler


try:
    from .utils import logger
except ImportError:                     
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)


class NumericalPreprocessor:
    """
    Scikit-learn-style transformer for numeric columns.

    * Imputation (median / mean) – optional
    * Outlier removal (IQR / Z-score) – optional
    * Scaling (standard / minmax) – optional
    """

    def __init__(self) -> None:
        # will be created only when scaling is requested
        self.scaler: Optional[StandardScaler | MinMaxScaler] = None

        # medians / means learned during fit (used when the user asks for imputation without providing a value)
        self.impute_values: Dict[str, float] = {}

        self._fitted_columns: List[str] = []
        self.report: Dict[str, Any] = {"numerical": {}}

    def _detect_outliers_zscore(self, series: pd.Series, threshold: float = 3.0) -> pd.Series:
        """Return boolean mask where True = outlier (Z-score)."""
        if series.std() == 0:
            return pd.Series(False, index=series.index)
        z = np.abs((series - series.mean()) / series.std())
        return pd.Series(z > threshold, index=series.index, dtype=bool)

    def _detect_outliers_iqr(self, series: pd.Series) -> pd.Series:
        """Return boolean mask where True = outlier (IQR)."""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return pd.Series((series < lower) | (series > upper), index=series.index, dtype=bool)

    def fit(
        self,
        df: pd.DataFrame,
        columns: List[str],
        *,
        impute: Literal["median", "mean"] | None = None,
    ) -> "NumericalPreprocessor":
 
        num_df = df[columns].select_dtypes(include=[np.number]).copy()
        self._fitted_columns = num_df.columns.tolist()

        if impute:
            for col in num_df.columns:
                if impute == "median":
                    self.impute_values[col] = float(num_df[col].median())
                else:  
                    self.impute_values[col] = float(num_df[col].mean())

        logger.info(
            f"NumericalPreprocessor fitted on {len(self._fitted_columns)} columns "
            f"(impute={impute})"
        )
        return self

    def transform(
        self,
        df: pd.DataFrame,
        columns: List[str] | None = None,
        *,
        impute: Literal["median", "mean"] | None = None,
        scale: Literal["standard", "minmax"] | None = None,
        remove_outliers: Literal["iqr", "zscore"] | None = None,
    ) -> pd.DataFrame:
    
        df = df.copy()
        cols = columns or self._fitted_columns
        import pandas.api.types as pd_types
        num_cols = [c for c in cols if c in df.columns and pd_types.is_numeric_dtype(df[c])]

        for col in num_cols:
            series = df[col].copy()

            # Imputation
            impute_val: Optional[float] = None
            if impute and series.isna().any():
                if impute == "median":
                    impute_val = series.median()
                else:  
                    impute_val = series.mean()

                # fallback if the column is still all-NaN after the above
                if pd.isna(impute_val):
                    impute_val = self.impute_values.get(col, 0.0)

                series.fillna(impute_val, inplace=True)
                self.report["numerical"].setdefault(col, {})["imputed_with"] = float(impute_val)

            if remove_outliers and series.notna().any():
                mask = (
                    self._detect_outliers_iqr(series)
                    if remove_outliers == "iqr"
                    else self._detect_outliers_zscore(series)
                )
                n_out = int(mask.sum())
                if n_out:
                    series[mask] = np.nan
                    # re-impute the holes we just created
                    if impute:
                        fill = impute_val if impute_val is not None else 0.0
                        if impute == "median":
                            fill = series.median() if pd.isna(fill) else fill
                        else:
                            fill = series.mean() if pd.isna(fill) else fill
                        if pd.isna(fill):
                            fill = 0.0
                        series.fillna(fill, inplace=True)
                    self.report["numerical"].setdefault(col, {})["outliers_removed"] = n_out

            df[col] = series

        if scale and num_cols:
            to_scale = df[num_cols]

            if scale == "standard":
                if self.scaler is None:                 
                    self.scaler = StandardScaler()
                    self.scaler.fit(to_scale)
                df[num_cols] = self.scaler.transform(to_scale)

            elif scale == "minmax":
                mm = MinMaxScaler()
                df[num_cols] = mm.fit_transform(to_scale)

        return df

    def fit_transform(
        self,
        df: pd.DataFrame,
        columns: List[str],
        *,
        impute: Literal["median", "mean"] | None = None,
        scale: Literal["standard", "minmax"] | None = None,
        remove_outliers: Literal["iqr", "zscore"] | None = None,
    ) -> pd.DataFrame:
        """
        Convenience method: learn statistics **and** apply the pipeline in one call.
        """
        return (
            self.fit(df, columns, impute=impute)
            .transform(df, columns, impute=impute, scale=scale, remove_outliers=remove_outliers)
        )

    def get_report(self) -> Dict[str, Any]:
        """Return a summary of what was done."""
        return self.report