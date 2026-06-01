import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://admin:adminadmin@localhost:5432/tmdb_db')

print("Loading CSV...")
df_movies = pd.read_csv('ingestion/data/tmdb_5000_movies.csv')
df_credits = pd.read_csv('ingestion/data/tmdb_5000_credits.csv')

# Rename kolom di credits supaya bisa di-merge
df_credits = df_credits.rename(columns={'movie_id': 'id'})

# Merge berdasarkan id
print("Merging...")
df_merge = pd.merge(df_movies, df_credits[['id', 'cast', 'crew']], on='id', how='left')

print(f"Shape: {df_merge.shape}")

# Load ke PostgreSQL
df_merge.to_sql('merge_raw', engine, if_exists='replace', index=False)
print(f"✅ merge_raw: {len(df_merge)} rows berhasil diload!")