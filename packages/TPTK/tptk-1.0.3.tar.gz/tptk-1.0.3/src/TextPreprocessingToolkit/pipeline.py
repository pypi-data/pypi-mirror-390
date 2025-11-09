import yaml
import json
import pandas as pd
from typing import Dict, Any
from .text_preprocessor import TextPreprocessor
from .numerical_preprocessor import NumericalPreprocessor
from .categorical_preprocessor import CategoricalPreprocessor
from .utils import logger, save_report, tqdm

class PreprocessingPipeline:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.text_proc = TextPreprocessor(spell_correction=self.config.get('text', {}).get('spell', False))
        self.num_proc = NumericalPreprocessor()
        self.cat_proc = CategoricalPreprocessor(
            encoder_type=self.config.get('categorical', {}).get('type', 'label')
        )
        self.report = {"steps": [], "stats": {}}
        self.fitted = False

    def _load_config(self, path: str) -> Dict:
        with open(path, 'r') as f:
            if path.endswith('.yaml') or path.endswith('.yml'):
                return yaml.safe_load(f)
            else:
                return json.load(f)

    def fit(self, input_path: str, chunksize: int = 10000):
        first_chunk = pd.read_csv(input_path, nrows=1000)
        config = self.config

        if 'text' in config:
            col = config['text']['column']
            steps = config['text'].get('steps', ['clean', 'tokenize', 'lemmatize'])
            # Fit on sample
            self.text_proc.process_text(first_chunk[col].iloc[0], steps)

        if 'numerical' in config:
            cols = config['numerical']['columns']
            self.num_proc.fit(first_chunk, cols)

        if 'categorical' in config:
            cols = config['categorical']['columns']
            self.cat_proc.fit(first_chunk, cols)

        self.fitted = True
        logger.info("Pipeline fitted")

    def transform(self, input_path: str, output_path: str, chunksize: int = 10000):
        if not self.fitted:
            self.fit(input_path, chunksize)

        mode = 'w'
        header = True
        total_rows = sum(1 for _ in open(input_path)) - 1
        config = self.config

        with pd.read_csv(input_path, chunksize=chunksize) as reader:
            for chunk in tqdm(reader, total=(total_rows // chunksize) + 1, desc="Transforming"):
                if 'text' in config:
                    col = config['text']['column']
                    steps = config['text'].get('steps', [])
                    chunk[col] = chunk[col].astype(str).apply(
                        lambda x: self.text_proc.process_text(x, steps)
                    )

                if 'numerical' in config:
                    cols = config['numerical']['columns']
                    chunk = self.num_proc.transform(
                        chunk, cols,
                        impute=config['numerical'].get('impute'),
                        scale=config['numerical'].get('scale'),
                        remove_outliers=config['numerical'].get('outliers')
                    )

                if 'categorical' in config:
                    cols = config['categorical']['columns']
                    chunk = self.cat_proc.transform(chunk, cols)

                chunk.to_csv(output_path, mode=mode, header=header, index=False)
                mode = 'a'
                header = False

        save_report(self.report, "preprocessing_report.json")
        logger.info(f"Pipeline transform completed: {output_path}")

    def fit_transform(self, input_path: str, output_path: str, chunksize: int = 10000):
        self.fit(input_path, chunksize)
        self.transform(input_path, output_path, chunksize)