import configparser

import sqlalchemy as db
from sqlalchemy.orm import Session

from domain.objects import SingleMove, Opening


class Repository(object):
    connection_string = "mysql://{user}:{password}@{host}/chess_db"

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        credentials = config['DB_CREDENTIALS']
        engine = db.create_engine(
            self.connection_string.format(user=credentials['user'],
                                          password=credentials['password'],
                                          host=credentials['host'])
        )
        self.session = Session(bind=engine)

    def query_single_move_by_type(self, type_name: str):
        single_moves = self.session.query(SingleMove).filter(SingleMove.type == type_name)
        return [ob.as_dict() for ob in single_moves]

    def query_opening_by_fen(self, fen: str):
        openings = self.session.query(Opening).filter(Opening.epd == fen)
        return [opening.as_dict() for opening in openings]

    def query_opening_by_move_stack(self, move_stack: list):
        openings = self.session.query(Opening).filter(Opening.move_stack == ' '.join(move_stack))
        return [opening.as_dict() for opening in openings]

