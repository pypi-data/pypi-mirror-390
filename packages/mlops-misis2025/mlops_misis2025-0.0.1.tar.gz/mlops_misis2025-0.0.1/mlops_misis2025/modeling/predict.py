from pathlib import Path

from loguru import logger
from tqdm import tqdm
import typer
import pandas as pd
from sklearn.metrics import roc_auc_score
import pickle

from mlops_misis2025.config import MODELS_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, CONFIG_DIR, load_config
from mlops_misis2025.utils import get_sql_connection

app = typer.Typer()


@app.command()
def main(
    features_path: Path = PROCESSED_DATA_DIR / "test_features.csv",
    model_path: Path = MODELS_DIR / "model.pkl",
    predictions_path: Path = PROCESSED_DATA_DIR / "test_predictions.csv",
    config_path: Path = CONFIG_DIR / "config.yaml",
):
    config = load_config(config_path)
    conn = get_sql_connection(config.sql_params)
    X_test = pd.read_sql_table("X_test", conn)
    y_test = pd.read_sql_table("y_test", conn)
    logger.info("loaded test data")

    with open(model_path, 'rb') as fin:
        model = pickle.load(fin)
    logger.info(f"loaded model from {model_path}")

    y_test_pred = model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_test_pred)
    logger.info(f"{roc_auc=}")


if __name__ == "__main__":
    app()
