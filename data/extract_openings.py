"""
 Extract data in the opening tsv files from
    https://github.com/niklasf/chess-openings.git
 into chess_db database.
"""

import configparser
import csv
import logging
import os

import sqlalchemy as db
from sqlalchemy.orm import Session

from domain.objects import Opening


def create_db_session():
    try:
        config = configparser.ConfigParser()
        config.read('../config.ini')
        credentials = config['DB_CREDENTIALS']
        connection_string = "mysql://{user}:{password}@{host}/chess_db".format(user=credentials['user'],
                                                                               password=credentials['password'],
                                                                               host=credentials['host'])
        engine = db.create_engine(connection_string)
        return Session(bind=engine)
    except Exception as e:
        logging.warning("An exception occurred configuring the database connection... " + str(e))


def extract_data(src_path: str, session):
    for file_name in os.listdir(src_path):
        with open(os.path.join(src_path, file_name), 'r') as file:
            tsv_read = csv.reader(file, delimiter='\t')
            next(tsv_read)
            for row in tsv_read:
                opening = Opening(row[0], row[1], row[3], row[4])
                session.add(opening)
                session.commit()
            file.close()
    session.close()


def main():
    session = create_db_session()
    extract_data('./openings', session)


if __name__ == '__main__':
    main()
