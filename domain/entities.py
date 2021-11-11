from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    white_level = Column(Integer)
    black_level = Column(Integer)
    outcome = Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SingleMove(Base):
    __tablename__ = 'single_move'

    id = Column(Integer, primary_key=True)
    gain = Column(Float)
    starting_fen = Column(String)
    ending_fen = Column(String)
    type = Column(String)
    move = Column(String)
    to_move = Column(String)
    follow_move = Column(String)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MateInN(Base):
    __tablename__ = 'mate_in_n'

    id = Column(Integer, primary_key=True)
    starting_fen = Column(String)
    to_move = Column(String)
    moves_to_mate = Column(Integer)
    game_id = Column(Integer)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Opening(Base):
    __tablename__ = 'opening'

    eco_classification = Column(String, primary_key=True)
    name = Column(String)
    move_stack = Column(String)
    explorer_link = Column(String)
    wiki_link = Column(String)
    epd = Column(String)

    def __init__(self, name, move_stack, explorer_link, wiki_link, epd, eco):
        self.name = name
        self.move_stack = move_stack
        self.explorer_link = explorer_link
        self.wiki_link = wiki_link
        self.epd = epd
        self.eco_classification = eco

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class StockfishResult:

    def __init__(self, fen: str, move: str, winner):
        self.fen = fen
        self.move = move
        self.winner = winner
