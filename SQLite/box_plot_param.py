import pandas as pd
import sqlite3
import plotly.express as px

# Run from SQLite directory
conn = sqlite3.connect("Games.db")

if __name__ == '__main__':
    df = px.data.tips()
    print(df)
    fig = px.box(df, x="time", y="total_bill", points="all")
    fig.show()