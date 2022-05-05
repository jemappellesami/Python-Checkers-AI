import pandas as pd
import numpy as np

# Read data
heur_100_df = pd.read_csv("NoHeuristic/m100_h0_1651786476.1179326_HEURISTICS.csv", delimiter=";")
no_heur_100_df = pd.read_csv("NoHeuristic/m100_h0_1651786797.3131018_NOHEURISTICS.csv", delimiter=";")
no_heur_150_df = pd.read_csv("NoHeuristic/m150_h0_1651788958.7052047_NOHEURISTICS.csv", delimiter=";")
no_heur_200_df = pd.read_csv("NoHeuristic/m200_h0_1651787061.2675483_NOHEURISTICS.csv", delimiter=";")


summary_df = pd.DataFrame(columns=[
    'description',
    'mean',
    'std',
    'min',
    'argmin',
    'max',
    'argmax',
])

def analyze_moves(game_df, description, ai_type=' mcts') :
    ai_moves = game_df.loc[game_df[' AI'] == ai_type]

    mean, std = np.mean(ai_moves[' Time']), np.std(ai_moves[' Time'])
    min_time, min_turn = np.min(ai_moves[' Time']), pd.Series.argmin(ai_moves[' Time'])
    max_time, max_turn = np.max(ai_moves[' Time']), pd.Series.argmax(ai_moves[' Time'])
    result_df = pd.DataFrame({
        'description' : [description],
        'mean' : [mean],
        'std' : [std],
        'min' : [min_time],
        'argmin' : [min_turn],
        'max' : [max_time],
        'argmax' : [max_turn]
    })

    global summary_df
    summary_df = summary_df.append(result_df)

    return mean, std, min_time, min_turn, max_time, max_turn

analyze_moves(heur_100_df, 'With heuristics & n=100')
analyze_moves(no_heur_100_df, 'no heuristics & n=100')
analyze_moves(no_heur_150_df, 'no heuristics & n=150')
analyze_moves(no_heur_200_df, 'no heuristics & n=200')
print(summary_df)
#analyze_moves(heur_100_df, 'With heuritics & n=100')