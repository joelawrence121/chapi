import logging

import uvicorn
from fastapi import FastAPI

from domain.client_json import AggregationRequest
from service.gpt2_service import GPT2Service
from util import utils

app = FastAPI()
utils.configure_app(app)
gpt2_service = GPT2Service('checkpoint')

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('chapi_agg')


@app.post("/aggregation")
async def get_move_aggregation(request: AggregationRequest):
    try:
        return gpt2_service.aggregate_sentence(request)
    except RuntimeError as e:
        logger.warning(e)


if __name__ == "__main__":
    uvicorn.run("chapi_agg:app", host="127.0.0.1", port=5005, log_level="info", workers=1)
