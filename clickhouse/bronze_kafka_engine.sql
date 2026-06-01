-- BRONZE: Kafka Engine Tables (consume dari Kafka topics)

CREATE TABLE IF NOT EXISTS dim_movies_queue (
    movie_id Int64,
    title String,
    original_language String,
    release_year Int32,
    budget Int64,
    revenue Int64,
    popularity Float64,
    vote_average Float64,
    primary_genre String,
    director String,
    lead_actor String
) ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'tmdb_kafka:9092',
    kafka_topic_list = 'tmdb.silver_mart_silver_mart.dim_movies',
    kafka_group_name = 'clickhouse_group',
    kafka_format = 'JSONEachRow';

CREATE TABLE IF NOT EXISTS dim_revenue_queue (
    movie_id Int64,
    title String,
    budget Int64,
    revenue Int64,
    profit Int64,
    roi_pct Float64,
    performance_label String,
    popularity_tier String
) ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'tmdb_kafka:9092',
    kafka_topic_list = 'tmdb.silver_mart_silver_mart.dim_revenue',
    kafka_group_name = 'clickhouse_group',
    kafka_format = 'JSONEachRow';

CREATE TABLE IF NOT EXISTS fact_yearly_queue (
    release_year Int32,
    primary_genre String,
    total_films Int64,
    total_revenue Int64,
    total_budget Int64,
    total_profit Int64,
    avg_rating Float64,
    mega_blockbuster_count Int64,
    blockbuster_count Int64,
    loss_count Int64
) ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'tmdb_kafka:9092',
    kafka_topic_list = 'tmdb.silver_mart_silver_mart.fact_yearly',
    kafka_group_name = 'clickhouse_group',
    kafka_format = 'JSONEachRow';