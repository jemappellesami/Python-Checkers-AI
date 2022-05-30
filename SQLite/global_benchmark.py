from cProfile import label
import pandas as pd
import sqlite3
import plotly.express as px
from plotly.graph_objs import *


DROP_QUERY_FINAL_RESULTS = """
    DROP TABLE IF EXISTS finalresults ;
"""
DROP_QUERY_P = """
    DROP TABLE IF EXISTS box_plot_p_results ;
"""
DROP_QUERY_N = """
    DROP TABLE IF EXISTS box_plot_n_results ;
"""

CREATE_QUERY_FINAL_RESULTS = """
    CREATE TABLE finalresults(p INT, n INT, winner VARCHAR(10)) ; 
"""
CREATE_QUERY_P = """
    CREATE TABLE box_plot_p_results(p INT, time FLOAT) ;   
"""
CREATE_QUERY_N = """    
    CREATE TABLE box_plot_n_results(n INT, time FLOAT) ;    
"""

INITIAL_QUERIES = [DROP_QUERY_FINAL_RESULTS,
                   DROP_QUERY_P,
                   DROP_QUERY_N,
                   CREATE_QUERY_FINAL_RESULTS,
                   CREATE_QUERY_P,
                   CREATE_QUERY_N]


def insert_result(table, cur, conn):
    insert_result_query = """
                INSERT INTO finalresults(p, n, winner)
                    SELECT param_p, param_n_iter, color 
                    FROM {} 
                    WHERE AI_type == 'END';
            """.format(table)
    cur.execute(insert_result_query)
    conn.commit()


def insert_time_n_box_plot(table, cur, conn) :
    insert_query = """
        INSERT INTO box_plot_n_results(n, time)
            SELECT param_n_iter, time
            FROM {}
            WHERE AI_type == 'mcts' ;
    """.format(table)
    cur.execute(insert_query)
    conn.commit()

def insert_time_p_box_plot(table, cur, conn) :
    insert_query = """
        INSERT INTO box_plot_p_results(p, time)
            SELECT param_p, time
            FROM {}
            WHERE AI_type == 'mcts' ;
    """.format(table)
    cur.execute(insert_query)
    conn.commit()


def initialize_tables(conn) :
    # Creation of the benchmark tables
    cur = conn.cursor()
    for query in INITIAL_QUERIES :
        cur.execute(query)
        conn.commit()
    cur.close()

    return cur

def fill_tables(conn) :
    # Iteration over the tables, and filling the benchmark tables
    cur = conn.cursor()
    cur.execute("ATTACH \"GLOBAL.db\" AS my_db")
    cur.execute("SELECT name FROM my_db.sqlite_master WHERE type='table';")
    res = cur.fetchall()
    tables = [table[0] for table in res]
    for table in tables:
        # Insert end of games in a combined table
        if "_h" in table:
            insert_result(table, cur, conn)

            # Build the n-box plot
            if "_h400" in table:
                insert_time_n_box_plot(table, cur, conn)
            # Build the p-box plot
            if "m15000" in table:
                insert_time_p_box_plot(table, cur, conn)
    cur.close()
    return cur

if __name__ == '__main__':
    # Run from SQLite directory
    conn = sqlite3.connect("GLOBAL.db")
    # initialize_tables(conn)
    # fill_tables(conn)

    # Begin to plot
    layout = Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    n_bp_df = pd.read_sql_query("SELECT * FROM box_plot_n_results ;", conn)
    # fig = px.box(n_bp_df, x="n", y="time", points="all")
    # fig.update_layout(layout)
    # fig.show()

    p_bp_df = pd.read_sql_query("SELECT * FROM box_plot_p_results ;", conn)
    p_bp_df["p"] = p_bp_df["p"]/100


    # fig = px.box(p_bp_df,
    #     x="p",
    #     y="time",
    #     points="all",
    #     labels=dict(
    #         time="Execution time (s)",
    #         p="Trade-off parameter p"
    #     )
    #     )
    fig = px.box(n_bp_df,
        x="n",
        y="time",
        points="all",
        labels=dict(
            time="Execution time (s)",
            n="Number of iterations n"
        )
        )
    
    fig.update_yaxes( # the y-axis is in dollars
        ticksuffix=""
    )

    fig.update_layout( # customize font and legend orientation & position
        font_family="Palatino",
        font_size=24,
        legend=dict(
            title="", orientation="h", y=1, yanchor="bottom", x=0.5, xanchor="center"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_xaxes(showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        showgrid=True,
        gridwidth=0.05,
        gridcolor='Gray')
    fig.update_yaxes(showline=True,
        linewidth=2,
        linecolor='black',
        mirror=True,
        showgrid=True,
        gridwidth=0.05,
        gridcolor='Gray')
    fig.show()