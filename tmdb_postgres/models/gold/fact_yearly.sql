{{ config(materialized='table', schema='silver_mart') }}

SELECT
    m.release_year,
    m.primary_genre,
    COUNT(*) AS total_films,
    SUM(m.revenue) AS total_revenue,
    SUM(m.budget) AS total_budget,
    SUM(m.revenue - m.budget) AS total_profit,
    ROUND(AVG(m.vote_average)::numeric, 2) AS avg_rating,
    SUM(CASE WHEN m.revenue >= m.budget * 3 THEN 1 ELSE 0 END) AS mega_blockbuster_count,
    SUM(CASE WHEN m.revenue >= m.budget * 2 THEN 1 ELSE 0 END) AS blockbuster_count,
    SUM(CASE WHEN m.revenue < m.budget THEN 1 ELSE 0 END) AS loss_count
FROM {{ ref('stg_movies') }} m
WHERE m.release_year IS NOT NULL AND m.budget > 0 AND m.revenue > 0
GROUP BY m.release_year, m.primary_genre
ORDER BY m.release_year, total_revenue DESC