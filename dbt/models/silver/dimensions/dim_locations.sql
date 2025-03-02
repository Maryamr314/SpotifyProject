{{
  config(
    materialized = 'table',
    file_format = 'parquet',
    location_root = 'hdfs://namenode:9000/user/events/silver/dimensions'
  )
}}

SELECT DISTINCT
    CONCAT(COALESCE(city, 'Unknown'), '-', COALESCE(state, 'Unknown')) AS location_key,
    COALESCE(city, 'Unknown') AS city,
    COALESCE(state, 'Unknown') AS state,
    COALESCE(zip, 'Unknown') AS zip_code,
    COALESCE(lon, 0) AS longitude,
    COALESCE(lat, 0) AS latitude
FROM {{ source('bronze', 'listen_events') }}