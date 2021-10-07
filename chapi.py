from fastapi import FastAPI
from domain.repository import Repository
import uvicorn

app = FastAPI()
respository = Repository()


@app.get("/single_move/{type_name}")
async def get_single_move_by_type(type_name):
    # TODO: add validation and exception handling
    return respository.query_single_move_by_type(type_name)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")
