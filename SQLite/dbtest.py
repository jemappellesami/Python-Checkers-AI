import sqlite3
from sqlite3 import Error

# https://www.sqlitetutorial.net/sqlite-python/creating-database/
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn

def close_connection(connexion):
    connexion.close()

def create_game_table(game, connexion) :
    """
    Receives a connexion (already created) and a game name, creates a table and commits connexion. Careful : does not
    close connexion. If you desire to close connexion, you should do it outside the function.
    :param game: game name. While doing optimization, you may want to decide how to name your table. For example : h8_m200_[...]
    :param connexion: Connexion instance to the DB
    :return:
    """
    table_query = """
        CREATE TABLE {}(
            turn INT,
            color BOOLEAN,
            AI_type VARCHAR(10),
            origin_x INT,
            origin_y INT,
            final_x INT,
            final_y INT,
            skip INT,
            time FLOAT,
            numReds INT,
            numWhites INT
        )
    """.format(game)
    cur = connexion.cursor()
    cur.execute(table_query)
    connexion.commit()



delete_query = """
    DROP TABLE IF EXISTS game1 
"""


insert_query = """
    INSERT INTO game1(turn, color, AI_type, origin_x, origin_y, final_x, final_y, skip, time, numReds, numWhites)
    VALUES(1,
        1,
        'mcts',
        2,
        1,
        3,
        2,
        0,
        4.158572196960449,
        12,
        12)
"""
if __name__ == '__main__':
    conn = create_connection("Games.db")
    cur = conn.cursor()
    cur.execute(delete_query)
    cur.execute(table_query)
    cur.execute(insert_query)
    conn.commit()
    conn.close()
