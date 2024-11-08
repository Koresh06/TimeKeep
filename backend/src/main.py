import uvicorn
from fastapi import FastAPI
from core.config import settings



app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(
        app=app,
        host=settings.api.host,
        port=settings.api.port,
    )