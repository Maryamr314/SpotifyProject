{{
  config(
    materialized = 'table',
    file_format = 'parquet',
    location_root = 'hdfs://namenode:9000/user/events/silver/dimensions'
  )
}}

SELECT DISTINCT
    userId AS user_id,
    firstName AS first_name,
    lastName AS last_name,
    gender,
    CONCAT(firstName, ' ', lastName) AS full_name,
    registration AS registration_timestamp,
    FROM_UNIXTIME(registration / 1000) AS registration_date,
    level AS subscription_level
FROM {{ source('bronze', 'listen_events') }}
WHERE userId IS NOT NULL
