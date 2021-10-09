import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from domain.repository import Repository

app = FastAPI()
respository = Repository()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/single_move/{type_name}")
async def get_single_moves_by_type(type_name):
    # TODO: add validation and exception handling
    return respository.query_single_move_by_type(type_name)[0]


if __name__ == "__main__":
    uvicorn.run("chapi:app", host="127.0.0.1", port=5000, log_level="info", workers=1)
