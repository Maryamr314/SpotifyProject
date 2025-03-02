{{
  config(
    materialized = 'table',
    file_format = 'parquet',
    location_root = 'hdfs://namenode:9000/user/events/silver/dimensions'
  )
}}

SELECT DISTINCT
    CONCAT(artist, ' - ', song) AS song_key,
    artist,
    song AS song_name,
    COALESCE(duration, 0) AS duration_seconds
FROM {{ source('bronze', 'listen_events') }}
WHERE artist IS NOT NULL
  AND song IS NOT NULL