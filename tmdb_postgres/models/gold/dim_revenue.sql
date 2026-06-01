{{ config(materialized='table', schema='silver_mart') }}

SELECT
    m.movie_id,
    m.title,
    m.budget,
    m.revenue,
    m.revenue - m.budget AS profit,
    CASE 
        WHEN m.budget > 0 
        THEN ROUND(((m.revenue - m.budget)::numeric / m.budget * 100), 2)
        ELSE NULL 
    END AS roi_pct,
    CASE
        WHEN m.budget = 0 THEN 'No Budget Data'
        WHEN m.revenue >= m.budget * 3 THEN 'Mega Blockbuster'
        WHEN m.revenue >= m.budget * 2 THEN 'Blockbuster'
        WHEN m.revenue > m.budget THEN 'Profitable'
        WHEN m.revenue = m.budget THEN 'Break Even'
        WHEN m.revenue < m.budget THEN 'Loss'
        ELSE 'Unknown'
    END AS performance_label,
    CASE
        WHEN m.popularity > 100 THEN 'Viral'
        WHEN m.popularity > 50 THEN 'Popular'
        WHEN m.popularity > 20 THEN 'Known'
        ELSE 'Niche'
    END AS popularity_tier,
    m.popularity,
    m.vote_average,
    m.release_year
FROM {{ ref('stg_movies') }} m
WHERE m.budget > 0 AND m.revenue > 0