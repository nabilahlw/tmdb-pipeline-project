{{ config(materialized='table', schema='silver_mart') }}

SELECT
    c.director,
    COUNT(*) AS total_films,
    SUM(m.revenue) AS total_revenue,
    SUM(m.revenue - m.budget) AS total_profit,
    ROUND(AVG(m.vote_average)::numeric, 2) AS avg_rating,
    ROUND(
        CASE WHEN SUM(m.budget) > 0 
        THEN (SUM(m.revenue - m.budget)::numeric / SUM(m.budget) * 100)
        ELSE NULL END, 2
    ) AS director_roi_pct,
    MIN(m.release_year) AS career_start,
    MAX(m.release_year) AS career_end,
    STRING_AGG(DISTINCT m.title, ', ' ORDER BY m.title) AS filmography
FROM {{ ref('stg_credits') }} c
JOIN {{ ref('stg_movies') }} m ON c.movie_id = m.movie_id
WHERE c.director IS NOT NULL AND m.budget > 0 AND m.revenue > 0
GROUP BY c.director
ORDER BY total_revenue DESC