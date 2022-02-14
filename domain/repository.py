import configparser

import sqlalchemy as db
from sqlalchemy.orm import Session

from domain.entities import SingleMove, Opening, MateInN


class Repository(object):
    connection_string = "mysql://{user}:{password}@{host}/chess_db"
    get_statistics_query = "select type, count(*) as count from Single_Move group by type order by count asc;"
    get_following_openings_by_move_stack_query = "select * from Opening where move_stack like '{move_stack}%' " \
                                                 "and LENGTH(move_stack) between LENGTH('{move_stack}') + 1 " \
                                                 "and LENGTH('{move_stack}') + 6;"
    get_opening_variations_query = "select * from Opening where move_stack like '{move_stack}%' " \
                                   "and LENGTH(move_stack) > LENGTH('{move_stack}') + 1 " \
                                   "and LENGTH(move_stack) < LENGTH('{move_stack}') + 10;"
    get_random_opening_query = "SELECT * FROM Opening ORDER BY RAND() LIMIT 1;"
    get_opening_by_id_query = "SELECT * FROM Opening WHERE id={id};"
    get_opening_by_move_stack_query = "SELECT * FROM Opening WHERE move_stack='{move_stack}';"

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

    def get_opening(self, id: int):
        openings = self.session.execute(self.get_opening_by_id_query.format(id=id))
        return [dict(opening) for opening in openings]

    def get_random_opening_id(self):
        return [id for id in self.session.execute(self.get_random_opening_query)][0][0]

    def query_opening_by_move_stack(self, move_stack: list):
        openings = self.session.query(Opening).filter(Opening.move_stack == ' '.join(move_stack))
        return [opening.as_dict() for opening in openings]

    def get_opening_id_by_move_stack(self, move_stack: str):
        openings = [opening for opening in
                    self.session.execute(self.get_opening_by_move_stack_query.format(move_stack=move_stack))]
        if len(openings) == 0:
            return None
        return openings[0][0]

    def get_one_move_following_openings(self, move_stack):
        openings = self.session.execute(
            self.get_following_openings_by_move_stack_query.format(move_stack=move_stack))
        return [dict(opening) for opening in openings]

    def get_opening_variations(self, move_stack):
        openings = self.session.execute(
            self.get_opening_variations_query.format(move_stack=move_stack))
        return [dict(opening) for opening in openings]

    def get_type_statistics(self):
        statistics = self.session.execute(self.get_statistics_query)
        return [statistic for statistic in statistics]

    def query_mate_in_n_by_n(self, n: int):
        mate_puzzles = self.session.query(MateInN).filter(MateInN.moves_to_mate == n)
        return [ob.as_dict() for ob in mate_puzzles]
