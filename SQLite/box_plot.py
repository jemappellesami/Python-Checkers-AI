import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px

# Run from SQLite directory
conn = sqlite3.connect("Games.db")

extended_df = pd.DataFrame(columns=[
    "p",
    "tour",
    "time"
])

results_df = pd.DataFrame(columns=[
    "p",
    "win"
])

def analyze_moves(game_df, p, ai_type='mcts') :
    global extended_df, results_df

    result = game_df.loc[game_df['AI_type'] == "END"]
    results_df = results_df.append(
        pd.DataFrame({
            "p" : [p],
            "win" : result["color"]
        })
    )
    ai_moves = game_df.loc[game_df['AI_type'] == ai_type]

    for idx, row in ai_moves.iterrows():
        relevant = pd.DataFrame({
            'p' : [p],
            'tour' : [row['turn']],
            'time' : [row['time']]
        })
        extended_df = extended_df.append(relevant)


    return


# TODO : plot time, function of turn
# TODO : plot num_turns by game, function of max_it
if __name__ == '__main__':
    for p in ['0_25', '0_50', '1', '1_50', '2'] :

        cur = conn.cursor()
        cur.execute("ATTACH \"Games_{}.db\" AS db_{}".format(p,p))
        cur.execute("SELECT name FROM db_{}.sqlite_master WHERE type='table';".format(p))
        res = cur.fetchall()
        tables = [table[0] for table in res]
        for table in tables :
            df = pd.read_sql_query("select * from {} ;".format(table), conn)
            analyze_moves(game_df=df, p=p)

    print(extended_df)
    fig = px.box(extended_df, x="p", y="time", points="all")
    fig.show()
    print(results_df)
