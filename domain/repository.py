import sqlalchemy as db
from sqlalchemy.orm import Session

from domain.objects import SingleMove

class Repository(object):

    def __init__(self):
        engine = db.create_engine('mysql://root:password@localhost/chess_db')
        self.session = Session(bind=engine)

    def query_single_move_by_type(self, type_name):
        single_moves = self.session.query(SingleMove).filter(SingleMove.type == type_name)
        return [ob.as_dict() for ob in single_moves]