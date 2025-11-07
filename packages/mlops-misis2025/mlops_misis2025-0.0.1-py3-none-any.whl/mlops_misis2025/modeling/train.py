from pathlib import Path

import pandas as pd
from loguru import logger
from tqdm import tqdm
import typer
from sklearn.linear_model import LogisticRegression
import pickle

from mlops_misis2025.config import MODELS_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR, CONFIG_DIR, load_config
from mlops_misis2025.utils import get_sql_connection

app = typer.Typer()


@app.command()
def main(
    features_path: Path = PROCESSED_DATA_DIR / "features.csv",
    labels_path: Path = PROCESSED_DATA_DIR / "labels.csv",
    model_path: Path = MODELS_DIR / "model.pkl",
    config_path: Path = CONFIG_DIR / "config.yaml",
):
    config = load_config(config_path)
    conn = get_sql_connection(config.sql_params)
    X_train = pd.read_sql_table("X_train", conn)
    y_train = pd.read_sql_table("y_train", conn)
    logger.info("loaded train data")

    if config.model_params.model_type == "LogisticRegression":
        model = LogisticRegression(C=0.1)
        model.fit(X_train, y_train.values.ravel())
        logger.info("fit model")
    else:
        raise NotImplementedError

    with open(model_path, 'wb') as fin:
        pickle.dump(model, fin)
    logger.info(f"saved model to {model_path}")


if __name__ == "__main__":
    app()
