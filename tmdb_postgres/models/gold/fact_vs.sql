{{ config(materialized='table', schema='silver_mart') }}

SELECT
    k.movie_id,
    k.title,
    k.popularity AS kaggle_popularity,
    a.popularity AS api_popularity,
    a.popularity - k.popularity AS popularity_diff,
    k.vote_average AS kaggle_vote_average,
    a.vote_average AS api_vote_average,
    CASE WHEN a.movie_id IS NOT NULL THEN TRUE ELSE FALSE END AS in_api,
    CASE WHEN k.movie_id IS NOT NULL THEN TRUE ELSE FALSE END AS in_kaggle
FROM {{ ref('stg_movies') }} k
LEFT JOIN {{ ref('stg_tmdbapi') }} a ON k.movie_id = a.movie_id