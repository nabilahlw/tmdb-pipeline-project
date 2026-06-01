{{ config(materialized='table', schema='silver_mart') }}

SELECT
    primary_genre AS genre,
    COUNT(*) AS total_films,
    SUM(revenue) AS total_revenue,
    SUM(revenue - budget) AS total_profit,
    ROUND(AVG(vote_average)::numeric, 2) AS avg_rating,
    ROUND(AVG(popularity)::numeric, 2) AS avg_popularity,
    SUM(CASE WHEN revenue >= budget * 3 THEN 1 ELSE 0 END) AS mega_blockbuster_count,
    SUM(CASE WHEN revenue < budget THEN 1 ELSE 0 END) AS loss_count,
    MAX(title) AS top_grossing_film
FROM {{ ref('stg_movies') }}
WHERE primary_genre IS NOT NULL AND budget > 0 AND revenue > 0
GROUP BY primary_genre
ORDER BY total_revenue DESC