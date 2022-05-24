import pandas as pd
import numpy as np
import sqlite3


# Run from SQLite directory
conn = sqlite3.connect("Games.db")


summary_df = pd.DataFrame(columns=[
    'description',
    'mean',
    'std',
    'min',
    'argmin',
    'max',
    'argmax',
])

def analyze_moves(game_df, description, ai_type='mcts') :
    ai_moves = game_df.loc[game_df['AI_type'] == ai_type]

    mean, std = np.mean(ai_moves['time']), np.std(ai_moves['time'])
    min_time, min_turn = np.min(ai_moves['time']), pd.Series.argmin(ai_moves['time'])+1
    max_time, max_turn = np.max(ai_moves['time']), pd.Series.argmax(ai_moves['time'])+1
    num_turns = int(np.max(ai_moves["turn"]))
    result_df = pd.DataFrame({
        'description' : [description],
        'mean' : [mean],
        'std' : [std],
        'min' : [min_time],
        'argmin' : [min_turn],
        'max' : [max_time],
        'argmax' : [max_turn],
        'num_turns' : [num_turns]
    })

    global summary_df
    summary_df = summary_df.append(result_df)

    return mean, std, min_time, min_turn, max_time, max_turn


# TODO : plot time, function of turn
# TODO : plot num_turns by game, function of max_it
if __name__ == '__main__':
    cur = conn.cursor()
    cur.execute("ATTACH \"Games_v3.db\" AS my_db")
    cur.execute("SELECT name FROM my_db.sqlite_master WHERE type='table';")
    res = cur.fetchall()
    tables = [table[0] for table in res]
    for table in tables :
        df = pd.read_sql_query("select * from {} ;".format(table), conn)
        analyze_moves(df, table)

    print(summary_df)
