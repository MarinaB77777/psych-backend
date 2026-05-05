from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class RunInput(BaseModel):
    answers: dict


@app.get("/")
def root():
    return {"status": "ok"}


def run_engine_logic(answers: dict):
    return {
        "state": "test_state",
        "engine_location": "backend",
        "confidence": "low"
    }


@app.post("/run")
def run_engine(data: RunInput):
    result = run_engine_logic(data.answers)

    return {
        "ok": True,
        "result": result
    }