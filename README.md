# 🎬 TMDB Movie Pipeline
### Pipeline Data End-to-End | Bronze → Silver → Gold → Dashboard

> **Final Project — Bootcamp Data Engineering rubythalib.ai**  
> By: **Nabila Hulwana Z.**

---

## 📖 Tentang Proyek

Proyek ini membangun **pipeline data end-to-end** untuk menganalisis industri film global menggunakan **Medallion Architecture** (Bronze → Silver → Gold). Data bersumber dari Kaggle (CSV) dan TMDB API, lalu diproses melalui stack data engineering modern: dbt, PySpark, Kafka + Debezium, ClickHouse, MinIO, dan Streamlit.

---

## 🏗️ Arsitektur

```
TMDB API + Kaggle CSV
        │
        ▼
  ┌─────────────┐
  │   BRONZE    │  PostgreSQL — tmdb_raw, merge_raw, csv_movies_raw
  └──────┬──────┘
         │  ingestion/ scripts
         ▼
  ┌─────────────┐
  │   SILVER    │  dbt — stg_movies, stg_credits, stg_tmdbapi (Views)
  └──────┬──────┘
         │  tmdb_postgres/models/silver/
         ▼
  ┌─────────────┐
  │    GOLD     │  dbt — 11 Mart Models (dim_*, fact_*)
  └──────┬──────┘
         │  tmdb_postgres/models/gold/
    ┌────┴──────────┐
    ▼               ▼
PySpark ETL     Kafka + Debezium CDC
spark/          kafka/
    │               │
    ▼               ▼
MinIO (Parquet)  ClickHouse (OLAP)
minio/           clickhouse/
                     │
                     ▼
             Streamlit Dashboard
             dashboard/app.py
```

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
| **Kontainerisasi** | Docker + Docker Compose |
| **Admin DB** | pgAdmin 4 |

---

## 📁 Struktur Folder

```
tmdb-pipeline-project/
├── docker-compose.yml
├── .env                          # Tidak di-commit (lihat .env.example)
├── .gitignore
├── README_EN.md
├── README_ID.md
│
├── ingestion/                    # Step 1 — Ingesti data
│   ├── fetch_tmdb_api.py         # Ambil data dari TMDB API
│   ├── load_kaggle_csv.py        # Load CSV ke PostgreSQL
│   ├── merge_raw.py              # Merge sumber data mentah
│   └── data/
│       ├── tmdb_5000_movies.csv
│       └── tmdb_5000_credits.csv
│
├── tmdb_postgres/                # Step 2 — dbt project (Silver + Gold)
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── silver/               # Staging views
│   │   │   ├── sources.yml
│   │   │   ├── stg_movies.sql
│   │   │   ├── stg_credits.sql
│   │   │   └── stg_tmdbapi.sql
│   │   └── gold/                 # Mart models
│   │       ├── dim_movies.sql
│   │       ├── dim_revenue.sql
│   │       ├── dim_genres.sql
│   │       ├── dim_directors.sql
│   │       ├── dim_actors.sql
│   │       ├── dim_country.sql
│   │       ├── dim_language.sql
│   │       ├── dim_company.sql
│   │       ├── dim_yearlysum.sql
│   │       ├── fact_vs.sql
│   │       └── fact_yearly.sql
│   ├── macros/
│   ├── seeds/
│   ├── tests/
│   └── snapshots/
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
│   └── export_mart_to_parquet.py
│
├── dags/                         # Airflow DAGs
│   └── tmdb_pipeline_dag.py
│
├── dashboard/                    # Step 8 — Streamlit Dashboard
│   ├── app.py
│   ├── components/
│   └── pages/
│
├── docs/                         # Dokumentasi & diagram arsitektur
└── logs/
    └── dbt.log
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
| Step 3 | Query Optimization — 7 index, partisi, 4 MV, trigger | ✅ Selesai |
| Step 4 | PySpark ETL | ✅ Selesai |
| Step 5 | Kafka + Debezium CDC | ✅ Selesai |
| Step 6 | ClickHouse OLAP — 9 objek | ✅ Selesai |
| Step 7 | MinIO Object Storage — 7 file Parquet (2.7 MiB) | ✅ Selesai |
| Step 8 | Streamlit Dashboard | ✅ Selesai |

---

## 🌐 Akses Services (Container Docker harus jalan)

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

## 📊 Dataset

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
