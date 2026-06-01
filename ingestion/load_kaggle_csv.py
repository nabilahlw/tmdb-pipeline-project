import pandas as pd
from sqlalchemy import create_engine

# Koneksi ke PostgreSQL
engine = create_engine('postgresql://admin:adminadmin@localhost:5432/tmdb_db')

# Load CSV movies
print("Loading tmdb_5000_movies.csv...")
df_movies = pd.read_csv('ingestion/data/tmdb_5000_movies.csv')
df_movies.to_sql('csv_movies_raw', engine, if_exists='replace', index=False)
print(f" csv_movies_raw: {len(df_movies)} rows")

# Load CSV credits
print("Loading tmdb_5000_credits.csv...")
df_credits = pd.read_csv('ingestion/data/tmdb_5000_credits.csv')
df_credits.to_sql('csv_credits_raw', engine, if_exists='replace', index=False)
print(f" csv_credits_raw: {len(df_credits)} rows")

print(" Bronze layer CSV selesai!")