CREATE MATERIALIZED VIEW IF NOT EXISTS mv_genre_summary AS
SELECT * FROM silver_mart_silver_mart.dim_genres;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_revenue_summary AS
SELECT 
    FLOOR(release_year / 10) * 10 AS decade,
    primary_genre,
    COUNT(*) AS total_films,
    SUM(revenue) AS total_revenue,
    SUM(revenue - budget) AS total_profit,
    ROUND(AVG(vote_average)::numeric, 2) AS avg_rating
FROM silver_mart_silver_mart.dim_movies
WHERE budget > 0 AND revenue > 0
GROUP BY decade, primary_genre;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_director_performance AS
SELECT * FROM silver_mart_silver_mart.dim_directors;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_country_performance AS
SELECT * FROM silver_mart_silver_mart.dim_country;