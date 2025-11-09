import logging
import json
from tqdm import tqdm
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_report(report: dict, path: str):
    with open(path, 'w') as f:
        json.dump(report, f, indent=2)
    logger.info(f"Report saved to {path}")