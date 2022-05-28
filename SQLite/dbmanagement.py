import sqlite3
from sqlite3 import Error

# https://www.sqlitetutorial.net/sqlite-python/creating-database/
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn

def close_connection(connexion):
    connexion.close()

def create_game_table(game, conn) :
    """
    Receives a connexion (already created) and a game name, creates a table and commits connexion. Careful : does not
    close connexion. If you desire to close connexion, you should do it outside the function.
    :param game: game name. While doing optimization, you may want to decide how to name your table. For example : h8_m200_[...]
    :param connexion: Connexion instance to the DB
    :return:
    """
    drop_query = """
        DROP TABLE IF EXISTS {};
    """.format(game)
    table_query = """
        CREATE TABLE {}(
            turn INT,
            color VARCHAR(10),
            AI_type VARCHAR(10),
            origin_x INT,
            origin_y INT,
            final_x INT,
            final_y INT,
            skip INT,
            time FLOAT,
            numReds INT,
            numWhites INT,
            param_n_iter INT,
            param_p FLOAT
        )
    """.format(game)
    cur = conn.cursor()
    cur.execute(drop_query)
    cur.execute(table_query)
    conn.commit()

def insert_move(table,turn, color, ai_type, origin_x, origin_y, final_x, final_y, skip, time, count_red, count_white, conn, n, p) :
    cur = conn.cursor()
    insert_query = """
        INSERT INTO {}(turn, color, AI_type, origin_x, origin_y, final_x, final_y, skip, time, numReds, numWhites, param_n_iter, param_p)
        VALUES({},
            '{}',
            '{}',
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {})
    """.format(table,turn, color, ai_type, origin_x, origin_y, final_x, final_y, skip, time, count_red, count_white, n, p)
    cur.execute(insert_query)
    conn.commit()


delete_query = """
    DROP TABLE IF EXISTS game1 
"""



if __name__ == '__main__':
    conn = create_connection("Games_v2.db")
    cur = conn.cursor()
    cur.execute(delete_query)
    create_game_table("game1", conn)
    insert_move("game1",1, 1, "mcts",2,1,3, 2,0, 666, 12, 12, conn)
    #cur.execute(insert_query)
    #conn.commit()
    conn.close()
