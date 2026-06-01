-- GOLD: Materialized Views (Bronze → Silver pipeline)

CREATE MATERIALIZED VIEW IF NOT EXISTS dim_movies_mv TO dim_movies AS
SELECT
    movie_id, title, original_language, release_year,
    budget, revenue, popularity, vote_average,
    primary_genre, director, lead_actor
FROM dim_movies_queue;

CREATE MATERIALIZED VIEW IF NOT EXISTS dim_revenue_mv TO dim_revenue AS
SELECT
    movie_id, title, budget, revenue, profit,
    roi_pct, performance_label, popularity_tier
FROM dim_revenue_queue;

CREATE MATERIALIZED VIEW IF NOT EXISTS fact_yearly_mv TO fact_yearly AS
SELECT
    release_year, primary_genre, total_films,
    total_revenue, total_budget, total_profit,
    avg_rating, mega_blockbuster_count, blockbuster_count, loss_count
FROM fact_yearly_queue;