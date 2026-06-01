{{ config(materialized='table', schema='silver_mart') }}

SELECT
    primary_company AS main_production_company,
    COUNT(*) AS total_films,
    SUM(revenue) AS total_revenue,
    SUM(revenue - budget) AS total_profit,
    ROUND(AVG(vote_average)::numeric, 2) AS avg_rating,
    ROUND(
        SUM(CASE WHEN revenue >= budget * 2 THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100, 2
    ) AS blockbuster_rate_pct,
    MODE() WITHIN GROUP (ORDER BY primary_genre) AS most_common_genre
FROM {{ ref('stg_movies') }}
WHERE primary_company IS NOT NULL AND primary_company != 'Unknown'
AND budget > 0 AND revenue > 0
GROUP BY primary_company
ORDER BY total_revenue DESC