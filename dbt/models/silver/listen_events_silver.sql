{{
  config(
    materialized = 'table',
    file_format = 'parquet',
    partition_by = ['year', 'month', 'day'],
    location_root = 'hdfs://namenode:9000/user/events/silver'
  )
}}

WITH source_data AS (
  SELECT
    artist,
    song,
    duration,
    ts,
    sessionId,
    auth,
    level,
    itemInSession,
    city,
    zip,
    state,
    userAgent,
    lon,
    lat,
    userId,
    lastName,
    firstName,
    gender,
    registration,
    event_time,
    year,
    month,
    day,
    hour
  FROM {{ source('bronze', 'listen_events') }}
  WHERE artist IS NOT NULL
    AND song IS NOT NULL
    AND ts IS NOT NULL
)

SELECT
    -- Create a unique event ID by combining fields
    CONCAT(CAST(sessionId AS STRING), '-', CAST(ts AS STRING)) AS event_id,
    artist,
    song,
    COALESCE(duration, 0) AS duration,
    ts AS timestamp,
  FROM_UNIXTIME(ts / 1000) AS event_timestamp,
  sessionId,
  CASE
    WHEN auth IN ('Logged In', 'Logged Out') THEN auth
    ELSE 'Unknown'
END AS auth_status,
  level,
  itemInSession,
  COALESCE(city, 'Unknown') AS city,
  COALESCE(state, 'Unknown') AS state,
  COALESCE(userAgent, 'Unknown') AS user_agent,
  COALESCE(lon, 0) AS longitude,
  COALESCE(lat, 0) AS latitude,
  COALESCE(userId, -1) AS user_id,
  COALESCE(CONCAT(firstName, ' ', lastName), 'Anonymous') AS user_name,
  COALESCE(gender, 'Unknown') AS gender,
  registration,
  year,
  month,
  day,
  hour
FROM source_data