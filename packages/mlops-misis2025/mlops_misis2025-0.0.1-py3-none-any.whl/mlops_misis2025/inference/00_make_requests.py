import requests 
import random
from time import sleep
from loguru import logger


for _ in range(100):
    random_input = [[random.random() for _ in range(4)]]
    features = [f"feature_{i}" for i in range(4)]
    
    response = requests.get("http://127.0.0.1:80/predict/", 
                            json={"data": random_input, "features": features})
    logger.info(response.json())
    sleep(1)
