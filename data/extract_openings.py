"""
 Extract data in the opening tsv files from
    https://github.com/niklasf/chess-openings.git
 into chess_db database with their Wikipedia pages
 and Master statistics from Lichess https://lichess.org/api#tag/Opening-Explorer attached.
"""

import configparser
import csv
import logging
import os

import requests
import sqlalchemy as db
import wikipedia
from chess import Board
from sqlalchemy.orm import Session

from domain.entities import Opening


def create_db_session():
    try:
        config = configparser.ConfigParser()
        config.read('../config.ini')
        credentials = config['DB_CREDENTIALS']
        connection_string = "mysql://{user}:{password}@{host}/chess_db".format(
            user=credentials['user'],
            password=credentials['password'],
            host=credentials['host'])
        engine = db.create_engine(connection_string)
        return Session(bind=engine)
    except Exception as e:
        logging.warning("An exception occurred configuring the database connection... " + str(e))


def extract_data(src_path: str, session):
    config = configparser.ConfigParser()
    config.read('../config.ini')
    credentials = config['DB_CREDENTIALS']
    lichess_token = credentials['lichess_token']

    for file_name in os.listdir(src_path):
        with open(os.path.join(src_path, file_name), 'r') as file:
            tsv_read = csv.reader(file, delimiter='\t')
            next(tsv_read)

            for row in tsv_read:
                white, draws, black = get_opening_data(get_fen(row[4]), lichess_token)
                opening = Opening(name=row[1],
                                  move_stack=row[3],
                                  pgn=row[2],
                                  wiki_link=get_wikipedia_link(row[1]),
                                  epd=get_fen(row[4]),
                                  eco=row[0],
                                  white=white,
                                  draws=draws,
                                  black=black)
                session.add(opening)
                session.commit()
            file.close()
    session.close()


def get_opening_data(fen: str, lichess_token: str):
    try:
        response = requests.get(
            url="https://explorer.lichess.ovh/masters",
            headers={"Authorization": "Bearer " + lichess_token},
            params={"fen": fen}
        ).json()
        return response['white'], response['draws'], response['black']

    except Exception as e:
        print("Exception occurred calling Lichess {}: {}".format(fen, str(e)))
        return None, None, None


def get_fen(fen: str):
    board = Board(fen)
    return board.fen()


def get_wikipedia_link(opening: str):
    try:
        return wikipedia.page(opening, auto_suggest=True).url
    except Exception as e:
        print("Exception occurred querying {}: {}".format(opening, str(e)))
        return None


def main():
    session = create_db_session()
    extract_data('./openings', session)


if __name__ == '__main__':
    main()
