import os
import joblib
from typing import Dict, Any

import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

try:
    from .utils import logger
except ImportError:                    
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class CategoricalPreprocessor:
    def __init__(self, encoder_type: str = "label", save_dir: str = "encoders"):
        self.encoder_type = encoder_type
        self.save_dir = os.path.join(save_dir, encoder_type)   
        self.encoders: Dict[str, Any] = {}
        os.makedirs(self.save_dir, exist_ok=True)

    def fit(self, df: pd.DataFrame, columns: list):
        for col in columns:
            if col not in df.columns:
                continue

            if self.encoder_type == "label":
                enc = LabelEncoder()
                values_1d = df[col].astype(str).fillna("missing").values.ravel()
                enc.fit(values_1d)
                self.encoders[col] = enc
            else:   
                enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
                enc.fit(df[[col]].fillna("missing"))
                self.encoders[col] = enc

            joblib.dump(enc, os.path.join(self.save_dir, f"{col}.pkl"))

        logger.info(f"Fitted {self.encoder_type} encoders for {len(self.encoders)} columns")
        return self

    def transform(self, df: pd.DataFrame, columns: list) -> pd.DataFrame:
        df = df.copy()
        for col in columns:
            if col not in self.encoders:
                logger.warning(f"No encoder for {col}")
                continue

            enc = self.encoders[col]

            if self.encoder_type == "label":
                vals = df[col].astype(str).fillna("missing").values.reshape(-1, 1)
                df[col] = enc.transform(vals).ravel()
            else:
                onehot = enc.transform(df[[col]].fillna("missing"))
                cats = enc.categories_[0]
                ohe_cols = [f"{col}_{c}" for c in cats]
                ohe_df = pd.DataFrame(onehot, columns=ohe_cols, index=df.index)
                df = pd.concat([df.drop(col, axis=1), ohe_df], axis=1)
        return df

    def load_encoders(self, columns: list):
        self.encoders = {}
        for col in columns:
            path = os.path.join(self.save_dir, f"{col}.pkl")
            if os.path.exists(path):
                self.encoders[col] = joblib.load(path)
            else:
                logger.warning(f"Encoder for {col} not found at {path}")
        logger.info(f"Loaded {len(self.encoders)} {self.encoder_type} encoders")