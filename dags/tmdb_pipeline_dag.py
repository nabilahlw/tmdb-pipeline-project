"""
DAG: tmdb_pipeline_dag
======================
TMDB End-to-End Pipeline
Schedule: Setiap Senin tengah malam (0 0 * * 1)
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

import pandas as pd
import requests
import pyarrow as pa
import pyarrow.parquet as pq
import io
from sqlalchemy import create_engine
from google.cloud import bigquery
from google.oauth2 import service_account

# ─── KONFIGURASI ──────────────────────────────────────────────────────────────

DB_CONN        = "postgresql://admin:adminadmin@tmdb_postgres:5432/tmdb_db"
TMDB_API_KEY   = "5d793e8800f4bf6134a3370e3e49237f"
MINIO_ENDPOINT = "172.18.0.2:9000"
MINIO_ACCESS   = "minioadmin"
MINIO_SECRET   = "minioadmin"
MINIO_BUCKET   = "tmdb-data"
GCP_PROJECT    = "latihan-dsarea"
BQ_DATASET     = "tmdb_gold"
GCP_KEY_PATH   = "/opt/airflow/dags/gcp_key.json"

TABLES = [
    "dim_movies", "dim_directors", "dim_revenue",
    "dim_country", "dim_genres", "fact_vs", "fact_yearly",
]

# ─── HELPER ───────────────────────────────────────────────────────────────────

def get_s3_client():
    import boto3
    from botocore.client import Config
    return boto3.client(
        "s3",
        endpoint_url=f"http://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS,
        aws_secret_access_key=MINIO_SECRET,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

# ─── DEFAULT ARGS ─────────────────────────────────────────────────────────────

default_args = {
    "owner": "nabila",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# ─── TASKS ────────────────────────────────────────────────────────────────────

def task_fetch_tmdb_api():
    engine = create_engine(DB_CONN)
    all_movies = []
    for page in range(1, 5):
        url = "https://api.themoviedb.org/3/movie/popular"
        res = requests.get(url, params={"api_key": TMDB_API_KEY, "page": page}, timeout=10)
        res.raise_for_status()
        all_movies.extend(res.json().get("results", []))
    df = pd.DataFrame(all_movies)
    df["category"] = "popular"
    df.to_sql("tmdb_raw", engine, if_exists="replace", index=False, schema="public")
    print(f"✅ fetch_tmdb_api: {len(df)} rows")


def task_load_kaggle_csv():
    engine = create_engine(DB_CONN)
    df_movies  = pd.read_csv("/opt/airflow/dags/data/tmdb_5000_movies.csv")
    df_credits = pd.read_csv("/opt/airflow/dags/data/tmdb_5000_credits.csv")
    df_movies.to_sql("csv_movies_raw",   engine, if_exists="replace", index=False, schema="public")
    df_credits.to_sql("csv_credits_raw", engine, if_exists="replace", index=False, schema="public")
    print(f"✅ load_kaggle_csv: {len(df_movies)} + {len(df_credits)} rows")


def task_merge_raw():
    engine = create_engine(DB_CONN)
    df_movies  = pd.read_sql("SELECT * FROM public.csv_movies_raw",  engine)
    df_credits = pd.read_sql("SELECT * FROM public.csv_credits_raw", engine)
    df_credits = df_credits.rename(columns={"title": "title_credits"})
    df_merged  = pd.merge(df_movies, df_credits, left_on="id", right_on="movie_id", how="outer")
    df_merged  = df_merged.drop(columns=["title_credits", "movie_id"], errors="ignore")
    df_merged.to_sql("merge_raw", engine, if_exists="replace", index=False, schema="public")
    print(f"✅ merge_raw: {len(df_merged)} rows")


def task_export_to_minio():
    engine = create_engine(DB_CONN)
    s3 = get_s3_client()

    # Buat bucket kalau belum ada
    try:
        s3.head_bucket(Bucket=MINIO_BUCKET)
        print(f"✅ Bucket {MINIO_BUCKET} sudah ada")
    except Exception:
        s3.create_bucket(Bucket=MINIO_BUCKET)
        print(f"✅ Bucket {MINIO_BUCKET} dibuat")

    schema = "silver_mart_silver_mart"
    for table in TABLES:
        df       = pd.read_sql(f'SELECT * FROM {schema}."{table}"', engine)
        table_pa = pa.Table.from_pandas(df)
        buf      = io.BytesIO()
        pq.write_table(table_pa, buf)
        buf.seek(0)

        s3.put_object(
            Bucket=MINIO_BUCKET,
            Key=f"mart/{table}.parquet",
            Body=buf.getvalue(),
        )
        print(f"  ✅ {table}.parquet → MinIO ({len(df):,} rows)")

    print("✅ export_to_minio selesai")


def task_export_to_bigquery():
    s3 = get_s3_client()

    credentials = service_account.Credentials.from_service_account_file(
        GCP_KEY_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    bq_client = bigquery.Client(project=GCP_PROJECT, credentials=credentials)

    dataset_ref = bigquery.Dataset(f"{GCP_PROJECT}.{BQ_DATASET}")
    dataset_ref.location = "US"
    bq_client.create_dataset(dataset_ref, exists_ok=True)

    failed = []
    for table in TABLES:
        try:
            obj = s3.get_object(Bucket=MINIO_BUCKET, Key=f"mart/{table}.parquet")
            buf = io.BytesIO(obj["Body"].read())
            df  = pq.read_table(buf).to_pandas()

            table_id   = f"{GCP_PROJECT}.{BQ_DATASET}.{table}"
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
                autodetect=True,
            )
            job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()

            rows = bq_client.get_table(table_id).num_rows
            print(f"  ✅ {table:<25} → BigQuery ({rows:,} rows)")
        except Exception as e:
            print(f"  ❌ {table} GAGAL: {e}")
            failed.append(table)

    if failed:
        raise Exception(f"Gagal: {failed}")
    print("✅ export_to_bigquery selesai")


# ─── DAG ──────────────────────────────────────────────────────────────────────

with DAG(
    dag_id="tmdb_pipeline_dag",
    description="TMDB End-to-End Pipeline",
    default_args=default_args,
    schedule_interval="0 0 * * 1",
    start_date=days_ago(1),
    catchup=False,
    tags=["tmdb", "etl", "bigquery"],
) as dag:

    t1 = PythonOperator(task_id="fetch_tmdb_api",     python_callable=task_fetch_tmdb_api)
    t2 = PythonOperator(task_id="load_kaggle_csv",    python_callable=task_load_kaggle_csv)
    t3 = PythonOperator(task_id="merge_raw",          python_callable=task_merge_raw)
    t4 = PythonOperator(task_id="export_to_minio",    python_callable=task_export_to_minio)
    t5 = PythonOperator(task_id="export_to_bigquery", python_callable=task_export_to_bigquery)

    t1 >> t2 >> t3 >> t4 >> t5