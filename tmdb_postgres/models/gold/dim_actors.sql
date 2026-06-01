{{ config(materialized='table', schema='silver_mart') }}

SELECT
    c.lead_actor AS actor_name,
    COUNT(*) AS total_films,
    SUM(m.revenue) AS total_revenue,
    ROUND(AVG(m.vote_average)::numeric, 2) AS avg_rating,
    ROUND(AVG(m.popularity)::numeric, 2) AS avg_popularity,
    STRING_AGG(DISTINCT c.director, ', ') AS frequent_director,
    MAX(m.title) AS best_performing_film
FROM {{ ref('stg_credits') }} c
JOIN {{ ref('stg_movies') }} m ON c.movie_id = m.movie_id
WHERE c.lead_actor IS NOT NULL
GROUP BY c.lead_actor
ORDER BY total_revenue DESC