"""
Step 8b — Export Gold Layer: MinIO Parquet → Google BigQuery
============================================================
Membaca 7 file Parquet dari MinIO lalu upload ke BigQuery
dataset: tmdb_gold di project: latihan-dsarea

Requirements:
    pip install google-cloud-bigquery google-cloud-bigquery-storage
    pip install pandas-gbq pyarrow minio

Setup sekali saja:
    1. Buat Service Account di Google Cloud Console
       IAM & Admin → Service Accounts → Create
       Role: BigQuery Data Editor + BigQuery Job User
    2. Download JSON key → simpan sebagai: gcp_key.json
    3. Taruh gcp_key.json di folder yang sama dengan file ini
"""

import pandas as pd
import pyarrow.parquet as pq
import io
from minio import Minio
from google.cloud import bigquery
from google.oauth2 import service_account

# ─── KONFIGURASI ──────────────────────────────────────────────────────────────

# MinIO
MINIO_ENDPOINT  = "localhost:9002"
MINIO_ACCESS    = "minioadmin"
MINIO_SECRET    = "minioadmin"
MINIO_BUCKET    = "tmdb-data"
MINIO_PREFIX    = "mart/"

# BigQuery
GCP_PROJECT     = "latihan-dsarea"
BQ_DATASET      = "tmdb_gold"
GCP_KEY_PATH    = "gcp_key.json"   # Path ke Service Account JSON key

# Daftar 7 tabel yang akan di-load
TABLES = [
    "dim_movies",
    "dim_directors",
    "dim_revenue",
    "dim_country",
    "dim_genres",
    "fact_vs",
    "fact_yearly",
]

# ─── KONEKSI ──────────────────────────────────────────────────────────────────

def get_minio_client():
    return Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS,
        secret_key=MINIO_SECRET,
        secure=False
    )

def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_file(
        GCP_KEY_PATH,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return bigquery.Client(project=GCP_PROJECT, credentials=credentials)

# ─── FUNGSI UTAMA ─────────────────────────────────────────────────────────────

def ensure_dataset_exists(bq_client):
    """Buat dataset tmdb_gold di BigQuery kalau belum ada."""
    dataset_ref = bigquery.Dataset(f"{GCP_PROJECT}.{BQ_DATASET}")
    dataset_ref.location = "US"
    try:
        bq_client.get_dataset(dataset_ref)
        print(f"✅ Dataset {BQ_DATASET} sudah ada.")
    except Exception:
        bq_client.create_dataset(dataset_ref, exists_ok=True)
        print(f"✅ Dataset {BQ_DATASET} berhasil dibuat!")

def read_parquet_from_minio(minio_client, table_name):
    """Baca file Parquet dari MinIO, return DataFrame."""
    object_path = f"{MINIO_PREFIX}{table_name}.parquet"
    response = minio_client.get_object(MINIO_BUCKET, object_path)
    data = response.read()
    buf = io.BytesIO(data)
    df = pq.read_table(buf).to_pandas()
    return df

def upload_to_bigquery(bq_client, df, table_name):
    """Upload DataFrame ke BigQuery dengan mode WRITE_TRUNCATE (replace)."""
    table_id = f"{GCP_PROJECT}.{BQ_DATASET}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        # WRITE_TRUNCATE = hapus data lama lalu replace dengan yang baru
        # Ganti ke WRITE_APPEND kalau mau append (tidak replace)
        autodetect=True,  # Deteksi schema otomatis dari DataFrame
    )

    job = bq_client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # Tunggu sampai selesai

    table = bq_client.get_table(table_id)
    return table.num_rows

# ─── PIPELINE ─────────────────────────────────────────────────────────────────

def run_export():
    print("=" * 55)
    print("  Export Gold Layer: MinIO → BigQuery")
    print(f"  Project  : {GCP_PROJECT}")
    print(f"  Dataset  : {BQ_DATASET}")
    print("=" * 55)

    minio_client = get_minio_client()
    bq_client    = get_bigquery_client()

    ensure_dataset_exists(bq_client)
    print()

    results = []
    failed  = []

    for table in TABLES:
        print(f"⏳ Processing {table}...")
        try:
            # 1. Baca dari MinIO
            df = read_parquet_from_minio(minio_client, table)
            print(f"   📦 MinIO → {len(df):,} rows dibaca")

            # 2. Upload ke BigQuery
            rows = upload_to_bigquery(bq_client, df, table)
            print(f"   ☁️  BigQuery → {rows:,} rows tersimpan ✅")

            results.append({
                "table": table,
                "rows": rows,
                "status": "SUCCESS"
            })

        except Exception as e:
            print(f"   ❌ Gagal: {e}")
            failed.append({"table": table, "error": str(e)})

        print()

    # ─── RINGKASAN ────────────────────────────────────────────────────────────
    print("=" * 55)
    print("  RINGKASAN HASIL EXPORT")
    print("=" * 55)
    for r in results:
        print(f"  ✅ {r['table']:<25} {r['rows']:>6,} rows")
    if failed:
        print()
        for f in failed:
            print(f"  ❌ {f['table']:<25} GAGAL: {f['error']}")
    print("=" * 55)
    print(f"  Sukses : {len(results)}/{len(TABLES)} tabel")
    if failed:
        print(f"  Gagal  : {len(failed)}/{len(TABLES)} tabel")
    print("=" * 55)

    if failed:
        raise Exception(f"{len(failed)} tabel gagal diupload ke BigQuery")

if __name__ == "__main__":
    run_export()