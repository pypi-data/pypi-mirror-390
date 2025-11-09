# Text Preprocessing Toolkit (TPTK)

[![PyPI version](https://badge.fury.io/py/TPTK.svg)](https://badge.fury.io/py/TPTK)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/downloads/)

TPTK is a Python package designed to automate data preprocessing tasks for machine learning and data analysis. It supports text cleaning, numerical data handling (imputation, outlier removal, scaling), and categorical encoding (label or one-hot). The package provides both a programmatic API and a command-line interface (CLI) for ease of use. It processes large datasets in chunks to handle memory efficiently and generates reports on preprocessing steps.

## Features

- **Text Preprocessing**: Clean, tokenize, remove stopwords, lemmatize, and spell-check text data.
- **Numerical Preprocessing**: Impute missing values (mean/median), remove outliers (IQR/Z-score), and scale features (standard/min-max).
- **Categorical Preprocessing**: Label encoding or one-hot encoding with support for saving/loading encoders.
- **Pipeline**: Configurable preprocessing pipeline using YAML/JSON files for batch processing CSV files.
- **Chunked Processing**: Handles large datasets by processing in chunks.
- **Reporting**: Generates JSON reports summarizing preprocessing actions.
- **CLI Support**: Run preprocessing via command-line arguments.
- **Extensible**: Modular classes for custom workflows.

## Installation

### From PyPI

Install the package using pip:

```bash
pip install TPTK
```

### From Source

Clone the repository and install:

```bash
git clone https://github.com/Gaurav-Jaiswal-1/Text-Preprocessing-Toolkit.git
cd Text-Preprocessing-Toolkit
pip install .
```

During installation, NLTK resources (e.g., stopwords, wordnet) are automatically downloaded.

### Dependencies

- `nltk >= 3.6.0`
- `pyspellchecker >= 0.7.1`
- `pandas >= 1.2.0`
- `scikit-learn` (for encoding and scaling)
- `joblib` (for saving encoders)

For development/testing:
- `pytest`, `flake8`, `mypy`, etc. (install via `pip install -r requirements_dev.txt`)

## Quick Start

### Step 1: Prepare Your Data

Assume you have a CSV file `input.csv` with columns like `review` (text), `age` (numerical), `rating` (numerical), `gender` (categorical).

Example `input.csv`:

```
review,age,rating,gender
"This is a great product!",35,4.5,Male
"Bad experience, won't buy again.",,3.0,Female
"Excellent quality.",42,,Male
```

### Step 2: Create a Configuration File (Optional but Recommended for Pipeline)

Create a YAML or JSON config file (e.g., `pipeline_example.yaml`):

```yaml
text:
  column: review
  steps: [clean, tokenize, stopwords, lemmatize]
  spell: false
numerical:
  columns: [age, rating]
  impute: median
  scale: standard
  outliers: iqr
categorical:
  columns: [gender]
  type: onehot
```

- **Text Section**: Specify the text column and steps (`clean`, `tokenize`, `stopwords`, `lemmatize`, `spell`).
- **Numerical Section**: List columns, imputation strategy, scaling, and outlier removal.
- **Categorical Section**: List columns and encoding type (`label` or `onehot`).

### Step 3: Run Preprocessing via CLI

Use the CLI to preprocess your CSV file:

```bash
dataprepkit preprocess --input input.csv --output output.csv --config pipeline_example.yaml --chunksize 5000
```

- `--input`: Path to input CSV.
- `--output`: Path to output CSV.
- `--config`: Path to YAML/JSON config (optional; if omitted, use `--text` for text-only processing).
- `--chunksize`: Process in chunks of this size (default: 10000).
- `--text`: Text column name (for text-only mode).
- `--steps`: Text processing steps (default: `clean`, `tokenize`, `lemmatize`).

This will apply the pipeline, save the processed data to `output.csv`, and generate a `preprocessing_report.json`.

Example Output (`output.csv` after processing):

```
review,age,rating,gender_Female,gender_Male
great product,35.0,4.5,0.0,1.0
bad experience wont buy,0.0,3.0,1.0,0.0
excellent quality,42.0,0.0,0.0,1.0
```

(Note: Numerical values are imputed/scaled, text is processed, categoricals are encoded.)

### Step 4: Programmatic Usage

For more control, use the API in your Python scripts.

#### Example: Full Pipeline

```python
from TPTK.pipeline import PreprocessingPipeline

# Initialize with config
pipeline = PreprocessingPipeline('pipeline_example.yaml')

# Fit and transform CSV
pipeline.fit_transform('input.csv', 'output.csv', chunksize=10000)

# Get report
report = pipeline.report
print(report)
```

#### Example: Text Preprocessing Only

```python

from TPTK.text_preprocessor import TextPreprocessor
import pandas as pd

# Download
url = "https://raw.githubusercontent.com/Ankit152/IMDB-sentiment-analysis/master/IMDB-Dataset.csv"
df = pd.read_csv(url)
df = df.head(1000)  # Small sample
df.to_csv(r"imdb_raw.csv", index=False)

# Clean
tp = TextPreprocessor(spell_correction=False)
tp.process_csv(
    input_path=r"imdb_raw.csv",
    text_column="review",
    output_path=r"imdb_clean.csv",
    steps=['clean', 'punctuation', 'lowercase', 'tokenize', 'stopwords', 'lemmatize']
)

```

#### Example: Numerical Preprocessing Only

```python
import pandas as pd
from TPTK.numerical_preprocessor import NumericalPreprocessor
import seaborn as sns
import matplotlib.pyplot as plt
import os

# If you are downlaoding the dataset
INPUT_DIR = "Input directory path"
OUTPUT_DIR = "Output directory path"

# If you haven't made a input and output dir
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Download
from sklearn.datasets import fetch_california_housing
data = fetch_california_housing(as_frame=True)
df = data.frame.sample(1000, random_state=42)
df.to_csv(f"{INPUT_DIR}/housing_raw.csv", index=False)

# Process
np_prep = NumericalPreprocessor()
df_clean = np_prep.fit_transform(
    df, columns=['MedInc', 'HouseAge', 'AveRooms', 'Population', 'AveOccup'],
    impute="median", scale="standard", remove_outliers="iqr"
)
df_clean.to_csv(f"{OUTPUT_DIR}/housing_clean.csv", index=False)

# Plot
plt.figure(figsize=(10,4))
plt.subplot(1,2,1); sns.boxplot(data=df[['MedInc']]); plt.title("Before")
plt.subplot(1,2,2); sns.boxplot(data=df_clean[['MedInc']]); plt.title("After")
plt.savefig(f"{OUTPUT_DIR}/housing_plot.png")
plt.close()

print("Housing: Done")
print(np_prep.report)
```

#### Example: Categorical Preprocessing Only

```python
from TPTK.categorical_preprocessor import CategoricalPreprocessor
import pandas as pd
import os

# If you are downlaoding the dataset

INPUT_DIR = "Input directory path"
OUTPUT_DIR = "Output directory path"
os.makedirs(INPUT_DIR, exist_ok=True); os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
df = df[['Pclass', 'Sex', 'Embarked', 'Survived']].dropna().head(500)
df.to_csv(f"{INPUT_DIR}/titanic_raw.csv", index=False)

# Label
label_enc = CategoricalPreprocessor("label", save_dir="../encoders")
label_enc.fit(df, ['Pclass', 'Sex', 'Embarked'])
df_label = label_enc.transform(df, ['Pclass', 'Sex', 'Embarked'])
df_label.to_csv(f"{OUTPUT_DIR}/titanic_label.csv", index=False)

# One-Hot
ohe_enc = CategoricalPreprocessor("onehot", save_dir="../encoders")
ohe_enc.fit(df, ['Pclass', 'Sex', 'Embarked'])
df_ohe = ohe_enc.transform(df, ['Pclass', 'Sex', 'Embarked'])
df_ohe.to_csv(f"{OUTPUT_DIR}/titanic_ohe.csv", index=False)

print("Titanic: Label →", df_label['Sex'].iloc[0], "| OHE →", df_ohe.filter(like='Sex_').columns)
```

### Step 5: View Reports

After processing, check `preprocessing_report.json` for details like imputed values, outliers removed, etc.

Example Report:

```json
{
  "steps": ["text", "numerical", "categorical"],
  "stats": {
    "numerical": {
      "age": {"imputed_with": 38.5, "outliers_removed": 0},
      "rating": {"imputed_with": 3.75, "outliers_removed": 1}
    }
  }
}
```

## Development and Testing

- **Setup**: Run `./init_setup.sh` to create a virtual environment and install dev dependencies.
- **Linting and Testing**: Use `tox` or manually:
  ```bash
  flake8 src/
  mypy src/
  pytest -v tests/unit
  pytest -v tests/integration
  ```
- **Build Package**: `python setup.py sdist bdist_wheel`

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/Gaurav-Jaiswal-1/Text-Preprocessing-Toolkit).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions, contact [Gaurav Jaiswal](mailto:jaiswalgaurav863@gmail.com).