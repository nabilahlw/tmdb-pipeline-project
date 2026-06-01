from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import re

# Init Spark
spark = SparkSession.builder \
    .appName("TMDB ETL") \
    .config("spark.jars.packages", "org.postgresql:postgresql:42.6.0") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

# ─── EXTRACT ───────────────────────────────────────────
print("Extracting from PostgreSQL...")
jdbc_url = "jdbc:postgresql://localhost:5432/tmdb_db"
props = {"user": "admin", "password": "adminadmin", "driver": "org.postgresql.Driver"}

df = spark.read.jdbc(jdbc_url, "merge_raw", properties=props)
print(f"Extracted: {df.count()} rows")

# ─── TRANSFORM 1: Extract JSON columns ─────────────────
def extract_first_name(json_str):
    if json_str is None:
        return None
    match = re.search(r'"name":\s*"([^"]+)"', json_str)
    return match.group(1) if match else None

def extract_director(crew_str):
    if crew_str is None:
        return None
    match = re.search(r'"job":\s*"Director"[^}]*"name":\s*"([^"]+)"', crew_str)
    return match.group(1) if match else None

extract_name_udf = udf(extract_first_name, StringType())
extract_director_udf = udf(extract_director, StringType())

df = df.withColumn("primary_genre", extract_name_udf(col("genres"))) \
       .withColumn("primary_keyword", extract_name_udf(col("keywords"))) \
       .withColumn("primary_company", extract_name_udf(col("production_companies"))) \
       .withColumn("primary_country", extract_name_udf(col("production_countries"))) \
       .withColumn("primary_language", extract_name_udf(col("spoken_languages"))) \
       .withColumn("primary_director", extract_director_udf(col("crew"))) \
       .withColumn("lead_actor", extract_name_udf(col("cast")))

# ─── TRANSFORM 2: Kalkulasi kolom baru ─────────────────
df = df.withColumn("profit", col("revenue") - col("budget")) \
       .withColumn("roi_pct", 
           when(col("budget") > 0, 
               round((col("revenue") - col("budget")) / col("budget") * 100, 2)
           ).otherwise(None)) \
       .withColumn("performance_label",
           when(col("budget") == 0, "No Budget Data")
           .when(col("revenue") >= col("budget") * 3, "Mega Blockbuster")
           .when(col("revenue") >= col("budget") * 2, "Blockbuster")
           .when(col("revenue") > col("budget"), "Profitable")
           .when(col("revenue") == col("budget"), "Break Even")
           .when(col("revenue") < col("budget"), "Loss")
           .otherwise("Unknown")) \
       .withColumn("popularity_tier",
           when(col("popularity") > 100, "Viral")
           .when(col("popularity") > 50, "Popular")
           .when(col("popularity") > 20, "Known")
           .otherwise("Niche"))

# Filter hanya yang punya budget & revenue
df_finance = df.filter((col("budget") > 0) & (col("revenue") > 0))
print(f"Finance rows: {df_finance.count()}")

# ─── TRANSFORM 3: Agregasi per genre ───────────────────
df_genre = df_finance.groupBy("primary_genre").agg(
    count("*").alias("total_films"),
    round(avg("vote_average"), 2).alias("avg_rating"),
    sum("revenue").alias("total_revenue"),
    sum("profit").alias("total_profit"),
    round(avg("roi_pct"), 2).alias("avg_roi_pct"),
    sum(when(col("performance_label") == "Mega Blockbuster", 1).otherwise(0)).alias("mega_blockbuster_count"),
    sum(when(col("performance_label") == "Loss", 1).otherwise(0)).alias("loss_count")
)

# ─── LOAD ───────────────────────────────────────────────
print("Loading to PostgreSQL...")

df_finance.write.jdbc(
    jdbc_url, "pyspark_tmdb_finance",
    mode="overwrite", properties=props
)
print("✅ pyspark_tmdb_finance loaded!")

df_genre.write.jdbc(
    jdbc_url, "pyspark_genre_aggregation",
    mode="overwrite", properties=props
)
print("✅ pyspark_genre_aggregation loaded!")

spark.stop()
print("✅ PySpark ETL selesai!")