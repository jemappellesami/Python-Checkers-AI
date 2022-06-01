import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px


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


def set_default_layout(fig):
    fig.update_layout({
        'font': {'family': "serif", 'size': 18},
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'xaxis': {
            'showgrid': True,
            'linecolor': 'black',
            'linewidth': 1,
            'mirror': True,
            'gridcolor': 'grey',
            'gridwidth': 0.1,
        },
        'yaxis': {
            'linecolor': 'black',
            'linewidth': 1,
            'gridcolor': 'grey',
            'gridwidth': 0.1,
            'mirror': True,
            'exponentformat': 'power',
        },
    })


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


def nb_turns_in_time_t(tables):
    df_full = pd.DataFrame(columns=['game_id', 'turn', 'time', 'AI_type'])
    for idx, table in enumerate(tables):
        df = pd.read_sql_query(f'select turn, time, AI_type from {table} where AI_type <> "END";', conn)
        df['game_id'] = idx
        df_full = pd.concat([df_full, df], ignore_index=True)
    fig = px.histogram(df_full, x="time", color="AI_type", nbins=20)
    set_default_layout(fig)
    fig.show()


# TODO : plot num_turns by game, function of max_it
def analyze_avg_time(tables):
    df_full = pd.DataFrame(columns=['game_id', 'turn', 'time', 'AI_type'])
    for idx, table in enumerate(tables):
        df = pd.read_sql_query(f'select turn, time, AI_type from {table} where AI_type <> "END";', conn)
        df['game_id'] = idx
        df_full = pd.concat([df_full, df], ignore_index=True)
    # Compute the avg time for each turn
    avg_time = df_full.groupby(['turn', 'AI_type'])['time'].mean().to_frame().reset_index()
    fig = px.line(
        data_frame=avg_time,
        x='turn', y='time',
        color='AI_type'
    )
    set_default_layout(fig)
    fig.show()


if __name__ == '__main__':
    cur = conn.cursor()
    cur.execute("ATTACH \"Games_v3.db\" AS my_db")
    cur.execute("SELECT name FROM my_db.sqlite_master WHERE type='table';")
    res = cur.fetchall()
    tables = [table[0] for table in res]
    analyze_avg_time(tables)
    nb_turns_in_time_t(tables)
    #for table in tables:
        #df = pd.read_sql_query("select * from {} ;".format(table), conn)
        #analyze_moves(df, table)

    #print(summary_df)
