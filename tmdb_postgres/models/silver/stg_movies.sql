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
        WHEN release_date ~ '^\d{2}/\d{2}/\d{4}$' 
            THEN TO_DATE(release_date, 'DD/MM/YYYY')
        ELSE NULL
    END AS release_date,
    EXTRACT(YEAR FROM 
        CASE
            WHEN release_date ~ '^\d{4}-\d{2}-\d{2}$' 
                THEN TO_DATE(release_date, 'YYYY-MM-DD')
            WHEN release_date ~ '^\d{2}/\d{2}/\d{4}$' 
                THEN TO_DATE(release_date, 'DD/MM/YYYY')
            ELSE NULL
        END
    )::int AS release_year,
    budget::bigint,
    revenue::bigint,
    runtime::float,
    popularity::float,
    vote_average::float,
    vote_count::bigint,
    status,
    tagline,
    -- Parse primary genre dari JSON
    CASE 
        WHEN genres IS NOT NULL AND genres != '[]'
        THEN (regexp_match(genres, '"name":\s*"([^"]+)"'))[1]
        ELSE 'Unknown'
    END AS primary_genre,
    -- Parse primary country
    CASE 
        WHEN production_countries IS NOT NULL AND production_countries != '[]'
        THEN (regexp_match(production_countries, '"name":\s*"([^"]+)"'))[1]
        ELSE 'Unknown'
    END AS primary_country,
    -- Parse primary company
    CASE 
        WHEN production_companies IS NOT NULL AND production_companies != '[]'
        THEN (regexp_match(production_companies, '"name":\s*"([^"]+)"'))[1]
        ELSE 'Unknown'
    END AS primary_company,
    -- Parse primary language
    CASE 
        WHEN spoken_languages IS NOT NULL AND spoken_languages != '[]'
        THEN (regexp_match(spoken_languages, '"name":\s*"([^"]+)"'))[1]
        ELSE 'Unknown'
    END AS primary_language,
    -- Parse primary keyword
    CASE 
        WHEN keywords IS NOT NULL AND keywords != '[]'
        THEN (regexp_match(keywords, '"name":\s*"([^"]+)"'))[1]
        ELSE NULL
    END AS primary_keyword
FROM {{ source('public', 'merge_raw') }}
WHERE id IS NOT NULL
