{{ config(materialized='table', schema='silver_mart') }}

SELECT
    m.movie_id,
    m.title,
    m.original_title,
    m.original_language,
    m.overview,
    m.release_date,
    m.release_year,
    m.budget,
    m.revenue,
    m.runtime,
    m.popularity,
    m.vote_average,
    m.vote_count,
    m.status,
    m.tagline,
    m.primary_genre,
    m.primary_country,
    m.primary_company,
    m.primary_language,
    m.primary_keyword,
    c.director,
    c.lead_actor,
    c.producer,
    c.screenplay_writer,
    c.music_composer
FROM {{ ref('stg_movies') }} m
LEFT JOIN {{ ref('stg_credits') }} c ON m.movie_id = c.movie_id