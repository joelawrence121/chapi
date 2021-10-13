import configparser

import sqlalchemy as db
from sqlalchemy.orm import Session

from domain.objects import SingleMove


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

    def query_single_move_by_type(self, type_name):
        single_moves = self.session.query(SingleMove).filter(SingleMove.type == type_name)
        return [ob.as_dict() for ob in single_moves]
