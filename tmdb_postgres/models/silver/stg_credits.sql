{{ config(materialized='view', schema='silver_mart') }}

SELECT
    id::bigint AS movie_id,
    title,
    (regexp_match("cast", '"name":\s*"([^"]+)"'))[1] AS lead_actor,
    (regexp_match("cast", '"name":\s*"([^"]+)"'))[1] AS cast_1,
    (regexp_match(crew, '"job":\s*"Director"[^}]*"name":\s*"([^"]+)"'))[1] AS director,
    (regexp_match(crew, '"job":\s*"Producer"[^}]*"name":\s*"([^"]+)"'))[1] AS producer,
    (regexp_match(crew, '"job":\s*"Screenplay"[^}]*"name":\s*"([^"]+)"'))[1] AS screenplay_writer,
    (regexp_match(crew, '"job":\s*"Original Music Composer"[^}]*"name":\s*"([^"]+)"'))[1] AS music_composer
FROM {{ source('public', 'merge_raw') }}
WHERE id IS NOT NULL