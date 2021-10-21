from client.json import OpeningRequest
from domain.repository import Repository


class DescriptionService(object):

    def __init__(self):
        self.repository = Repository()

    def get_description(self, request: OpeningRequest) -> str:
        return ""
