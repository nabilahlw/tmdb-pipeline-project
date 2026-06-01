{{ config(materialized='table', schema='silver_mart') }}

SELECT
    release_year,
    COUNT(*) AS total_films,
    SUM(revenue) AS total_revenue,
    SUM(budget) AS total_budget,
    ROUND(AVG(vote_average)::numeric, 2) AS avg_rating,
    MODE() WITHIN GROUP (ORDER BY primary_genre) AS most_common_genre,
    MAX(title) AS top_grossing_film
FROM {{ ref('stg_movies') }}
WHERE release_year IS NOT NULL
GROUP BY release_year
ORDER BY release_year