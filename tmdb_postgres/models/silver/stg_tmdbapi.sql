{{ config(materialized='view', schema='silver_mart') }}

SELECT
    id::bigint AS movie_id,
    title,
    original_title,
    original_language,
    overview,
    CASE
        WHEN release_date ~ '^\d{4}-\d{2}-\d{2}$'
            THEN TO_DATE(release_date, 'YYYY-MM-DD')
        ELSE NULL
    END AS release_date,
    popularity::float,
    vote_average::float,
    vote_count::bigint,
    adult::boolean,
    backdrop_path,
    poster_path,
    category,
    -- genre_ids sebagai array
    TRANSLATE(genre_ids, '[]', '{}')::int[] AS genre_ids_array
FROM {{ source('public', 'tmdb_raw') }}
WHERE id IS NOT NULL