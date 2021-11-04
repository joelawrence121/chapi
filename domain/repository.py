import configparser

import sqlalchemy as db
from sqlalchemy.orm import Session

from domain.objects import SingleMove, Opening, MateInN


class Repository(object):
    connection_string = "mysql://{user}:{password}@{host}/chess_db"
    get_statistics_query = "select type, count(*) as count from Single_Move group by type order by count asc;"

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
        single_move_puzzles = self.session.query(SingleMove).filter(SingleMove.type == type_name)
        return [ob.as_dict() for ob in single_move_puzzles]

    def query_opening_by_move_stack(self, move_stack: list):
        openings = self.session.query(Opening).filter(Opening.move_stack == ' '.join(move_stack))
        return [opening.as_dict() for opening in openings]

    def get_type_statistics(self):
        statistics = self.session.execute(self.get_statistics_query)
        return [statistic for statistic in statistics]

    def query_mate_in_n_by_n(self, n: int):
        mate_puzzles = self.session.query(MateInN).filter(MateInN.moves_to_mate == n)
        return [ob.as_dict() for ob in mate_puzzles]
