from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = 'postgresql://admin:adminadmin@postgres/tmdb_db'
API_KEY = '5d793e8800f4bf6134a3370e3e49237f'

default_args = {
    'owner': 'nabila',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def fetch_tmdb_api():
    engine = create_engine(DB_URL)
    engine.execute(text("DROP TABLE IF EXISTS tmdb_raw CASCADE"))
    all_movies = []
    for category in ['popular', 'top_rated', 'upcoming', 'now_playing']:
        url = f"https://api.themoviedb.org/3/movie/{category}?api_key={API_KEY}&language=en-US&page=1"
        data = requests.get(url).json()
        for movie in data['results']:
            movie['category'] = category
            movie['genre_ids'] = str(movie.get('genre_ids', []))
            all_movies.append(movie)
    df = pd.DataFrame(all_movies)
    cols = ['id','title','original_title','original_language','overview',
            'genre_ids','release_date','popularity','vote_average',
            'vote_count','adult','video','backdrop_path','poster_path','category']
    df[cols].to_sql('tmdb_raw', engine, if_exists='replace', index=False)
    print(f"✅ tmdb_raw: {len(df)} rows")

def load_kaggle_csv():
    engine = create_engine(DB_URL)
    engine.execute(text("DROP TABLE IF EXISTS csv_movies_raw CASCADE"))
    engine.execute(text("DROP TABLE IF EXISTS csv_credits_raw CASCADE"))
    df_movies = pd.read_csv('/opt/airflow/ingestion/data/tmdb_5000_movies.csv')
    df_credits = pd.read_csv('/opt/airflow/ingestion/data/tmdb_5000_credits.csv')
    df_movies.to_sql('csv_movies_raw', engine, if_exists='replace', index=False)
    df_credits.to_sql('csv_credits_raw', engine, if_exists='replace', index=False)
    print("✅ csv loaded")

def merge_raw():
    engine = create_engine(DB_URL)
    engine.execute(text("DROP TABLE IF EXISTS merge_raw CASCADE"))
    df_movies = pd.read_sql('SELECT * FROM csv_movies_raw', engine)
    df_credits = pd.read_sql('SELECT * FROM csv_credits_raw', engine)
    df_credits = df_credits.rename(columns={'movie_id': 'id'})
    df_merge = pd.merge(df_movies, df_credits[['id','cast','crew']], on='id', how='left')
    df_merge.to_sql('merge_raw', engine, if_exists='replace', index=False)
    print(f"✅ merge_raw: {len(df_merge)} rows")

def export_to_minio():
    from minio import Minio
    import pyarrow as pa
    import pyarrow.parquet as pq
    import io
    engine = create_engine(DB_URL)
    client = Minio("minio:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)
    if not client.bucket_exists("tmdb-data"):
        client.make_bucket("tmdb-data")
    for table in ['dim_movies','dim_directors','dim_revenue','dim_country','dim_genres','fact_vs','fact_yearly']:
        df = pd.read_sql(f'SELECT * FROM silver_mart_silver_mart."{table}"', engine)
        buf = io.BytesIO()
        pq.write_table(pa.Table.from_pandas(df), buf)
        buf.seek(0)
        client.put_object("tmdb-data", f"mart/{table}.parquet", buf, buf.getbuffer().nbytes)
        print(f"✅ {table}.parquet uploaded")

with DAG(
    dag_id='tmdb_pipeline_dag',
    default_args=default_args,
    description='TMDB End-to-End Pipeline',
    schedule='0 0 * * 1',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['tmdb', 'pipeline']
) as dag:

    t1 = PythonOperator(task_id='fetch_tmdb_api', python_callable=fetch_tmdb_api)
    t2 = PythonOperator(task_id='load_kaggle_csv', python_callable=load_kaggle_csv)
    t3 = PythonOperator(task_id='merge_raw', python_callable=merge_raw)
    t4 = PythonOperator(task_id='export_to_minio', python_callable=export_to_minio)

    t1 >> t2 >> t3 >> t4