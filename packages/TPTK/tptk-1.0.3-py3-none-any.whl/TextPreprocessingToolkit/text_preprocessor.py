import os
import re
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from spellchecker import SpellChecker
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm
import logging

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

logger = logging.getLogger("TextPreprocessor")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class TextPreprocessor:
    def __init__(self, spell_correction: bool = False, verbose: bool = False):
        self.spell = SpellChecker() if spell_correction else None
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.verbose = verbose
        if verbose:
            logger.setLevel(logging.DEBUG)

        self.report = {
            "before": {"rows": 0, "words": 0},
            "after": {"rows": 0, "words": 0}
        }
    # Step Funciton
    def _clean_text(self, text: str) -> str:
        if not isinstance(text, str) or not text.strip():
            return ""
        text = BeautifulSoup(text, "html.parser").get_text()
        text = re.sub(r'http[s]?://\S+', '', text)           # URLs
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text)  # Emojis
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _remove_punctuation(self, text: str) -> str:
        return re.sub(r'[^\w\s]', ' ', text)

    def _remove_numbers(self, text: str) -> str:
        return re.sub(r'\d+', '', text)

    def _to_lowercase(self, text: str) -> str:
        return text.lower()

    def _tokenize(self, text: str) -> List[str]:
        return word_tokenize(text)

    def _remove_stopwords(self, tokens: List[str]) -> List[str]:
        return [t for t in tokens if t not in self.stop_words]

    def _lemmatize(self, tokens: List[str]) -> List[str]:
        def get_pos(tag):
            if tag.startswith('J'): return wordnet.ADJ
            if tag.startswith('V'): return wordnet.VERB
            if tag.startswith('N'): return wordnet.NOUN
            if tag.startswith('R'): return wordnet.ADV
            return wordnet.NOUN
        tagged = nltk.pos_tag(tokens)
        return [self.lemmatizer.lemmatize(w, get_pos(t)) for w, t in tagged]

    def _correct_spelling(self, tokens: List[str]) -> List[str]:
        if not self.spell:
            return tokens
        return [self.spell.correction(w) or w for w in tokens]

    def _filter_min_length(self, tokens: List[str], min_len: int = 3) -> List[str]:
        return [t for t in tokens if len(t) >= min_len]

    def process_text(self, text: str, steps: List[str]) -> str:

        if steps is None:
            steps = [
                'clean', 'punctuation', 'numbers', 'lowercase',
                'tokenize', 'stopwords', 'lemmatize', 'min_length'
            ]

        if not isinstance(text, str):
            return ""

        tokens = None  

        for step in steps:
            if step == 'clean':
                text = self._clean_text(text)
            elif step == 'punctuation':
                text = self._remove_punctuation(text)
            elif step == 'numbers':
                text = self._remove_numbers(text)
            elif step == 'lowercase':
                text = self._to_lowercase(text)
            elif step == 'tokenize':
                tokens = self._tokenize(text)
                text = ' '
            elif step == 'stopwords' and tokens is not None:
                tokens = self._remove_stopwords(tokens)
            elif step == 'lemmatize' and tokens is not None:
                tokens = self._lemmatize(tokens)
            elif step == 'spell' and tokens is not None and self.spell:
                tokens = self._correct_spelling(tokens)
            elif step == 'min_length' and tokens is not None:
                tokens = self._filter_min_length(tokens, min_len=3)

        return " ".join(tokens) if tokens is not None else text

    def process_csv(
        self,
        input_path: str,
        text_column: str,
        output_path: str,
        steps: List[str],
        chunksize: int = 10_000,
        encoding: str = "utf-8",
    ) -> Dict[str, Any]:
   
        if steps is None:
            steps = [
                'clean', 'punctuation', 'numbers', 'lowercase',
                'tokenize', 'stopwords', 'lemmatize', 'min_length'
            ]

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"File not found: {input_path}")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Count total rows
        with open(input_path, "r", encoding=encoding) as f:
            total_rows = sum(1 for _ in f) - 1
        logger.info(f"Processing {total_rows:,} rows → {output_path}")

        first_chunk = True
        processed = 0

        for chunk in tqdm(
            pd.read_csv(input_path, chunksize=chunksize, encoding=encoding),
            total=(total_rows // chunksize) + 1,
            desc="Cleaning",
            unit="chunk"
        ):
            # Stats before
            self.report["before"]["rows"] += len(chunk)
            self.report["before"]["words"] += chunk[text_column].astype(str).str.split().str.len().sum()

            if text_column not in chunk.columns:
                logger.error(f"Column '{text_column}' not found!")
                break

            chunk[text_column] = chunk[text_column].apply(
                lambda x: self.process_text(str(x), steps)
            )

            # Stats after
            self.report["after"]["rows"] += len(chunk)
            self.report["after"]["words"] += chunk[text_column].str.split().str.len().sum()

            # Write
            chunk.to_csv(
                output_path,
                mode="a",
                header=first_chunk,
                index=False,
                encoding=encoding
            )
            first_chunk = False
            processed += len(chunk)

        logger.info(f"Done! {processed:,} rows cleaned.")
        logger.info(
            f"Words: {self.report['before']['words']:,} → {self.report['after']['words']:,} "
            f"(-{self.report['before']['words'] - self.report['after']['words']:,})"
        )
        return self.report