# 🎬 TMDB Movie Pipeline
### Pipeline Data End-to-End | Bronze → Silver → Gold → BigQuery

> **Final Project — Bootcamp Data Engineering rubythalib.ai**  
> By: **Nabila Hulwana Z.**

---

## 📖 Tentang Proyek

Proyek ini membangun **pipeline data end-to-end** untuk menganalisis industri film global menggunakan **Medallion Architecture** (Bronze → Silver → Gold). Data bersumber dari Kaggle (CSV) dan TMDB API, lalu diproses melalui stack data engineering modern: dbt, PySpark, Kafka + Debezium, ClickHouse, MinIO, Streamlit, Apache Airflow, dan Google BigQuery.

---

## 🏗️ Arsitektur

![Arsitektur Pipeline](docs/arsitektur%20-%20tmdb%20pipeline.png)

---

## 🛠️ Tech Stack

| Kategori | Teknologi |
|---|---|
| **Database** | PostgreSQL (via Docker) |
| **Transformasi** | dbt (dbt-postgres) |
| **Processing** | PySpark |
| **Streaming / CDC** | Apache Kafka + Debezium |
| **OLAP** | ClickHouse |
| **Object Storage** | MinIO (S3-compatible) |
| **Dashboard** | Streamlit |
| **Orkestrasi** | Apache Airflow |
| **Cloud Data Warehouse** | Google BigQuery |
| **Kontainerisasi** | Docker + Docker Compose |
| **Admin DB** | pgAdmin 4 |

---

## 📁 Struktur Folder

```
tmdb-pipeline-project/
├── docker-compose.yml
├── .env                          # Tidak di-commit (lihat .env.example)
├── .gitignore
├── README_ID.md
├── README_EN.md
│
├── ingestion/                    # Step 1 — Ingesti data
│   ├── fetch_tmdb_api.py
│   ├── load_kaggle_csv.py
│   ├── merge_raw.py
│   └── data/
│       ├── tmdb_5000_movies.csv
│       └── tmdb_5000_credits.csv
│
├── tmdb_postgres/                # Step 2 — dbt project (Silver + Gold)
│   ├── dbt_project.yml
│   └── models/
│       ├── silver/               # stg_movies, stg_credits, stg_tmdbapi
│       └── gold/                 # 11 mart models (dim_*, fact_*)
│
├── optimization/                 # Step 3 — Query optimization
│   ├── create_indexes.sql
│   ├── create_partitions.sql
│   └── materialized_views.sql
│
├── spark/                        # Step 4 — PySpark ETL
│   └── etl_transform.py
│
├── kafka/                        # Step 5 — Kafka + Debezium CDC
│   └── debezium_connector_config.json
│
├── clickhouse/                   # Step 6 — ClickHouse OLAP
│   ├── bronze_kafka_engine.sql
│   ├── silver_replacing_merge_tree.sql
│   └── gold_views.sql
│
├── minio/                        # Step 7 — MinIO Object Storage
│   ├── export_mart_to_parquet.py
│   └── export_to_bigquery.py     # Export Parquet → BigQuery
│
├── dags/                         # Step 9 — Airflow DAG
│   └── tmdb_pipeline_dag.py      # 5 task otomatis end-to-end
│
├── dashboard/                    # Step 8 — Streamlit Dashboard
│   ├── app.py
│   ├── components/
│   └── pages/
│
└── docs/                         # Dokumentasi & diagram arsitektur
    ├── arsitektur - tmdb pipeline.png
    ├── Laporan projek data eng - tmdb pipeline.pdf
    └── PPT-tmdb pipeline- data eng project.pdf
```

---

## ✅ Status Pipeline

| Step | Kategori | Status |
|---|---|---|
| Step 0 | Docker Compose Up | ✅ Selesai |
| Step 1 | Data Source — TMDB API + Kaggle CSV | ✅ Selesai |
| Step 2a | Bronze Layer — PostgreSQL raw tables | ✅ Selesai |
| Step 2b | Silver Layer — dbt staging views (3 model) | ✅ Selesai |
| Step 2c | Gold Layer — dbt mart models (11 model) | ✅ Selesai |
| Step 3 | Query Optimization — 7 index, 4 MV, 9 trigger, 10 partisi | ✅ Selesai |
| Step 4 | PySpark ETL | ✅ Selesai |
| Step 5 | Kafka + Debezium CDC — 16 topics | ✅ Selesai |
| Step 6 | ClickHouse OLAP — 9 objek | ✅ Selesai |
| Step 7 | MinIO Object Storage — 7 file Parquet (2.7 MiB) | ✅ Selesai |
| Step 8 | Streamlit Dashboard | ✅ Selesai |
| Step 9 | Apache Airflow — DAG 5 task otomatis | ✅ Selesai |
| Step 10 | Google BigQuery — 7 tabel (14.961 rows) | ✅ Selesai |

---

## 🌐 Akses Services

| Service | URL | Login |
|---|---|---|
| pgAdmin | http://localhost:5050 | postgres / postgres |
| Kafka UI | http://localhost:9000 | — |
| Debezium REST API | http://localhost:8083 | — |
| ClickHouse Play | http://localhost:18123/play | — |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |
| Streamlit Dashboard | http://localhost:8501 | — |
| Airflow | http://localhost:8082 | airflow / airflow |

---

## 📊 Data Source

| # | Sumber | Tipe | Rows | Deskripsi |
|---|---|---|---|---|
| 1 | TMDB API | JSON | 80 | Film populer dari endpoint `/movie/popular` |
| 2 | Kaggle `tmdb_5000_movies.csv` | CSV | 4,673 | Budget, revenue, genres, keywords |
| 3 | Kaggle `tmdb_5000_credits.csv` | CSV | 4,801 | Cast dan crew per film |

---

## ❓ Key Business Questions

1. Bagaimana **tren revenue & keuntungan** industri film dari tahun 1992–2016?
2. Genre mana yang **paling profitable** secara konsisten?
3. Sutradara mana dengan **ROI tertinggi** sepanjang karir?
4. Film mana saja yang masuk kategori **Mega Blockbuster** (revenue ≥ 3× budget)?

---

*Final Project — Bootcamp Data Engineering | rubythalib.ai*
