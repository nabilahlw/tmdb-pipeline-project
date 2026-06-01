import requests
import pandas as pd
from sqlalchemy import create_engine

API_KEY = '5d793e8800f4bf6134a3370e3e49237f'
BASE_URL = 'https://api.themoviedb.org/3'

engine = create_engine('postgresql://admin:adminadmin@localhost:5432/tmdb_db')

all_movies = []

# Fetch 4 kategori × 20 movies = 80 rows (sesuai laporan)
categories = ['popular', 'top_rated', 'upcoming', 'now_playing']

for category in categories:
    print(f"Fetching {category}...")
    url = f"{BASE_URL}/movie/{category}?api_key={API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    data = response.json()
    
    for movie in data['results']:
        movie['category'] = category
        movie['genre_ids'] = str(movie.get('genre_ids', []))
        all_movies.append(movie)

df = pd.DataFrame(all_movies)

# Pilih kolom sesuai struktur tmdb_raw di laporan
cols = ['id', 'title', 'original_title', 'original_language', 'overview',
        'genre_ids', 'release_date', 'popularity', 'vote_average',
        'vote_count', 'adult', 'video', 'backdrop_path', 'poster_path', 'category']

df = df[cols]
df.to_sql('tmdb_raw', engine, if_exists='replace', index=False)
print(f" tmdb_raw: {len(df)} rows berhasil diload!")