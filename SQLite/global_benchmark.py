import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px

# Run from SQLite directory
conn = sqlite3.connect("GLOBAL.db")

drop_query = """
    DROP TABLE IF EXISTS finalresults ;
"""

create_query = """
    CREATE TABLE finalresults(p INT, n INT, winner VARCHAR(10)) ;   
"""

if __name__ == '__main__':


    cur = conn.cursor()
    cur.execute(drop_query)
    cur.execute(create_query)
    cur.close()
    conn.commit()

    cur = conn.cursor()
    cur.execute("ATTACH \"GLOBAL.db\" AS my_db")
    cur.execute("SELECT name FROM my_db.sqlite_master WHERE type='table';")
    res = cur.fetchall()
    tables = [table[0] for table in res]
    for table in tables :
        if table != "finalresults" :
            insert_result_query = """
                INSERT INTO finalresults(p, n, winner)
                    SELECT param_p, param_n_iter, color 
                    FROM {} 
                    WHERE AI_type == 'END';
            """.format(table)
            print(table)
            cur.execute(insert_result_query)
            conn.commit()
    cur.close()

