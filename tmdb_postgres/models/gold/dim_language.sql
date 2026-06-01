{{ config(materialized='table', schema='silver_mart') }}

SELECT
    original_language,
    COUNT(*) AS total_films,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(vote_average)::numeric, 2) AS avg_rating,
    MODE() WITHIN GROUP (ORDER BY primary_country) AS dominant_country,
    MODE() WITHIN GROUP (ORDER BY primary_genre) AS top_revenue_genre
FROM {{ ref('stg_movies') }}
WHERE original_language IS NOT NULL
GROUP BY original_language
ORDER BY total_films DESC