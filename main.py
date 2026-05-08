from fastapi import FastAPI
from pydantic import BaseModel

from model_engine.run_engine import run_engine_logic

app = FastAPI()


class RunInput(BaseModel):
    answers: dict


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/run")
def run_engine(data: RunInput):
    result = run_engine_logic(data.answers)

    return {
        "ok": True,
        "result": result
    }