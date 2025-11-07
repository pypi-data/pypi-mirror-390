from pathlib import Path

from loguru import logger
import pandas as pd
from tqdm import tqdm
import typer
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split


from mlops_misis2025.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, CONFIG_DIR, load_config
from mlops_misis2025.utils import get_sql_connection

app = typer.Typer()


@app.command()
def main(
    new_arg: int = 5,
    input_path: Path = RAW_DATA_DIR / "dataset.csv",
    output_path: Path = PROCESSED_DATA_DIR / "dataset.csv",
    config_path: Path = CONFIG_DIR / "config.yaml",
):
    config = load_config(config_path)
    logger.info(f"{config=}")
    X, y = make_classification(n_samples=1000, n_features=4, random_state=config.random_state)
    X = pd.DataFrame(X, columns=[f"feature_{i+1}" for i in range(X.shape[1])])
    y = pd.DataFrame(y, columns=['target'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=config.random_state)

    conn = get_sql_connection(config.sql_params)
    X_train.to_sql(con=conn, name="X_train", if_exists='replace', index=False)
    X_test.to_sql(con=conn, name="X_test", if_exists='replace', index=False)
    y_train.to_sql(con=conn, name="y_train", if_exists='replace', index=False)
    y_test.to_sql(con=conn, name="y_test", if_exists='replace', index=False)

    y_test.to_csv(RAW_DATA_DIR / "y_test.csv", index=False)


if __name__ == "__main__":
    app()
