import logging
import random
import time

import uvicorn
from fastapi import FastAPI

from domain.client_json import DescriptionRequest, PlayRequest
from service.description_service import DescriptionService
from service.puzzle_service import PuzzleService
from service.stockfish_service import StockfishService
from util import utils

app = FastAPI()
utils.configure_app(app)
puzzle_service = PuzzleService()
description_service = DescriptionService()
stockfish_service = StockfishService()

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('chapi')


@app.get("/single_move/{type_name}")
async def get_random_single_move_puzzle(type_name):
    try:
        return puzzle_service.get_single_move_puzzle(type_name)
    except RuntimeError as e:
        logger.warning(e)


@app.get("/mate_in/{n}")
async def get_mate_in_n_puzzle(n):
    try:
        return puzzle_service.get_mate_in_n_puzzle(int(n))
    except RuntimeError as e:
        logger.warning(e)


@app.get("/statistics")
async def get_statistics():
    try:
        return puzzle_service.get_type_statistics()
    except RuntimeError as e:
        logger.warning(e)


@app.post("/description")
async def get_move_description(request: DescriptionRequest):
    try:
        return description_service.get_description(request)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/play")
async def play_stockfish(request: PlayRequest):
    try:
        result = stockfish_service.get_stockfish_play_result(request)
        if request.wait is not None and request.wait:
            time.sleep(random.randrange(0, 15) // 10)
        return result
    except RuntimeError as e:
        logger.warning(e)


if __name__ == "__main__":
    uvicorn.run("chapi:app", host="127.0.0.1", port=5000, log_level="info", workers=1)
