from pathlib import Path

import yaml
from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel

# Load environment variables from .env file if it exists
load_dotenv()

# Configs
class ModelParams(BaseModel):
    model_type: str 

class SQLParams(BaseModel):
    username: str
    password: str
    database: str
    ip: str


class Config(BaseModel):
    random_state: int 
    model_params: ModelParams
    sql_params: SQLParams


def load_config(config_path) -> Config:
    with open(config_path) as fin:
        loaded_config_yaml = yaml.safe_load(fin)

    config = Config(**loaded_config_yaml)
    return config

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
CONFIG_DIR = PROJ_ROOT / "configs"

# If tqdm is installed, configure loguru with tqdm.write
# https://github.com/Delgan/loguru/issues/135
try:
    from tqdm import tqdm

    logger.remove(0)
    logger.add(lambda msg: tqdm.write(msg, end=""), colorize=True)
except ModuleNotFoundError:
    pass
