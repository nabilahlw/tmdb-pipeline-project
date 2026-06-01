{{ config(materialized='table', schema='silver_mart') }}

SELECT
    primary_country,
    COUNT(*) AS total_films,
    SUM(revenue) AS total_revenue,
    ROUND(AVG(vote_average)::numeric, 2) AS avg_rating,
    MODE() WITHIN GROUP (ORDER BY primary_genre) AS most_common_genre,
    MODE() WITHIN GROUP (ORDER BY primary_language) AS most_common_language
FROM {{ ref('stg_movies') }}
WHERE primary_country IS NOT NULL AND primary_country != 'Unknown'
GROUP BY primary_country
ORDER BY total_films DESC