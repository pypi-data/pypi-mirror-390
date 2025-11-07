from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
import pickle

import os
import pandas as pd
import sklearn
from loguru import logger
from typing import List
from tqdm import tqdm

from mlops_misis2025.utils import get_sql_connection


class InputResponse(BaseModel):
    data: List[List[float]]
    features: List[str]
    
class PredictResponse(BaseModel):
    output: float
    
    
def make_predict(data: InputResponse, model):
    data = pd.DataFrame(data.data, columns=data.features)
    pred = model.predict_proba(data)[:, 1]
    return PredictResponse(output=pred)


ml_models = {}
model_path = os.getenv("MODEL_PATH")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global params
    with open(model_path, 'rb') as fin:
        ml_models["model"] = pickle.load(fin)
    yield
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def main():
    return "Entry Point"
    
        
@app.get("/predict/", response_model=PredictResponse)
def predict(request: InputResponse):
    return make_predict(request, ml_models['model'])
