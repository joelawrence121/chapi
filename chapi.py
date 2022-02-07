import logging
import random
import time

import uvicorn
from fastapi import FastAPI

from domain.client_json import DescriptionRequest, PlayRequest, OpeningRequest, MultiplayerCreateRequest, \
    MultiplayerJoinRequest, MultiplayerMessageRequest, MultiplayerPlayRequest, MultiplayerDrawAnswer
from service.description_service import DescriptionService
from service.multiplayer_service import MultiplayerService
from service.opening_service import OpeningService
from service.puzzle_service import PuzzleService
from service.stockfish_service import StockfishService
from util import utils

app = FastAPI()
utils.configure_app(app)
puzzle_service = PuzzleService()
description_service = DescriptionService()
stockfish_service = StockfishService()
opening_service = OpeningService()
multiplayer_service = MultiplayerService()

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


@app.get("/random_opening")
async def get_opening():
    try:
        return opening_service.get_random_opening()
    except RuntimeError as e:
        logger.warning(e)


@app.get("/opening/{id}")
async def get_opening(opening_id: int):
    try:
        return opening_service.get_opening(opening_id)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/opening")
async def get_opening_by_move_stack(request: OpeningRequest):
    try:
        return opening_service.get_opening_by_move_stack(request.move_stack)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/multiplayer/create")
async def create_new_multiplayer_game(request: MultiplayerCreateRequest):
    try:
        return multiplayer_service.create_game(request.player_name)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/multiplayer/join")
async def join_new_multiplayer_game(request: MultiplayerJoinRequest):
    try:
        return multiplayer_service.join_game(request.game_id, request.player_name)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/multiplayer/message")
async def create_new_multiplayer_message(request: MultiplayerMessageRequest):
    try:
        return multiplayer_service.post_message(request.game_id, request.player_name, request.message)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/multiplayer/poll")
async def poll_multiplayer_game(request: MultiplayerJoinRequest):
    try:
        return multiplayer_service.poll_game(request.game_id)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/multiplayer/play")
async def play_multiplayer_move(request: MultiplayerPlayRequest):
    try:
        return multiplayer_service.play(request.game_id, request.move, request.descriptions_on)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/multiplayer/offer_draw")
async def offer_multiplayer_draw(request: MultiplayerJoinRequest):
    try:
        return multiplayer_service.offer_draw(request.game_id)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/multiplayer/answer_draw")
async def answer_multiplayer_draw(request: MultiplayerDrawAnswer):
    try:
        return multiplayer_service.answer_draw(request.game_id, request.draw_accepted)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/multiplayer/reset_draw")
async def reset_multiplayer_draw(request: MultiplayerDrawAnswer):
    try:
        return multiplayer_service.reset_draw(request.game_id)
    except RuntimeError as e:
        logger.warning(e)


@app.post("/multiplayer/retire")
async def retire_from_multiplayer(request: MultiplayerJoinRequest):
    try:
        return multiplayer_service.retire(request.game_id, request.player_name)
    except RuntimeError as e:
        logger.warning(e)


if __name__ == "__main__":
    uvicorn.run("chapi:app", host="127.0.0.1", port=5000, log_level="info", workers=1)
