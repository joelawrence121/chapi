from fastapi import FastAPI

from chapi.runner import Client

app = FastAPI()

@app.get("/")
async def root():
    client = Client(10)
    return {"fen": client.get_fen()}
