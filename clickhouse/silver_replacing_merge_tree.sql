-- SILVER: ReplacingMergeTree Tables

CREATE TABLE IF NOT EXISTS dim_movies (
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
    lead_actor String,
    insert_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(insert_time)
ORDER BY movie_id;

CREATE TABLE IF NOT EXISTS dim_revenue (
    movie_id Int64,
    title String,
    budget Int64,
    revenue Int64,
    profit Int64,
    roi_pct Float64,
    performance_label String,
    popularity_tier String,
    insert_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(insert_time)
ORDER BY movie_id;

CREATE TABLE IF NOT EXISTS fact_yearly (
    release_year Int32,
    primary_genre String,
    total_films Int64,
    total_revenue Int64,
    total_budget Int64,
    total_profit Int64,
    avg_rating Float64,
    mega_blockbuster_count Int64,
    blockbuster_count Int64,
    loss_count Int64,
    insert_time DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(insert_time)
ORDER BY (release_year, primary_genre);