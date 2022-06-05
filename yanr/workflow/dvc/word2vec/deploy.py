import mlflow
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

m = mlflow.pyfunc.load_model('models:/recommender/production')

app = FastAPI()


@app.post("/predict")
async def predict(text: str, n: int = 300, top: int = 10):
    return m.predict({'text': text, 'n': n, 'top': top})
