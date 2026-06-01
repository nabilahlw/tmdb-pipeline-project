import pandas as pd
from sqlalchemy import create_engine
from minio import Minio
import pyarrow as pa
import pyarrow.parquet as pq
import io
import os

# Koneksi PostgreSQL
engine = create_engine('postgresql://admin:adminadmin@localhost:5432/tmdb_db')

# Koneksi MinIO
client = Minio(
    "localhost:9002",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

BUCKET = "tmdb-data"

# Pastikan bucket ada
if not client.bucket_exists(BUCKET):
    client.make_bucket(BUCKET)
    print(f"✅ Bucket {BUCKET} dibuat!")

# Daftar tabel yang akan di-export
tables = [
    "dim_movies",
    "dim_directors",
    "dim_revenue",
    "dim_country",
    "dim_genres",
    "fact_vs",
    "fact_yearly"
]

schema = "silver_mart_silver_mart"

for table in tables:
    print(f"Exporting {table}...")
    
    # Baca dari PostgreSQL
    df = pd.read_sql(f'SELECT * FROM {schema}."{table}"', engine)
    
    # Convert ke Parquet
    table_pa = pa.Table.from_pandas(df)
    buf = io.BytesIO()
    pq.write_table(table_pa, buf)
    buf.seek(0)
    size = buf.getbuffer().nbytes
    
    # Upload ke MinIO
    client.put_object(
        BUCKET,
        f"mart/{table}.parquet",
        buf,
        size,
        content_type="application/octet-stream"
    )
    print(f"✅ {table}.parquet uploaded! ({len(df)} rows, {size/1024:.1f} KB)")

print("\n✅ Semua file Parquet berhasil diupload ke MinIO!")