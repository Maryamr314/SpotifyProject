from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, from_unixtime, year, month,
    dayofmonth, hour, date_format
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType,
    LongType, IntegerType
)

def create_spark_session():
    return SparkSession.builder \
        .appName("KafkaListenEventsConsumer") \
        .config("spark.sql.sources.partitionOverwriteMode", "dynamic") \
        .config("hive.exec.dynamic.partition", "true") \
        .config("hive.exec.dynamic.partition.mode", "nonstrict") \
        .getOrCreate()

def create_event_schema():
    return StructType([
        StructField("artist", StringType(), True),
        StructField("song", StringType(), True),
        StructField("duration", DoubleType(), True),
        StructField("ts", LongType(), True),
        StructField("sessionId", IntegerType(), True),
        StructField("auth", StringType(), True),
        StructField("level", StringType(), True),
        StructField("itemInSession", IntegerType(), True),
        StructField("city", StringType(), True),
        StructField("zip", StringType(), True),
        StructField("state", StringType(), True),
        StructField("userAgent", StringType(), True),
        StructField("lon", DoubleType(), True),
        StructField("lat", DoubleType(), True),
        StructField("userId", IntegerType(), True),
        StructField("lastName", StringType(), True),
        StructField("firstName", StringType(), True),
        StructField("gender", StringType(), True),
        StructField("registration", LongType(), True)
    ])

def process_batch(df, batch_id):
    """Process each batch of streaming data"""
    if df.isEmpty():
        return

    # Write to HDFS in Parquet format with partitioning
    (df.write
        .mode("append")
        .partitionBy("year", "month", "day", "hour")
        .format("parquet")
        .save("hdfs://namenode:9000/user/events/bronze"))

def main():
    # Create Spark Session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    # Kafka configuration
    kafka_bootstrap_servers = "broker:9092"
    kafka_topic = "listen_events"

    # Create schema
    schema = create_event_schema()

    # Read from Kafka
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", "earliest") \
        .option("maxOffsetsPerTrigger", 10) \
        .load()

    # Parse JSON and add timestamp columns
    parsed_df = kafka_df \
        .selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    # Add timestamp columns for partitioning
    processed_df = parsed_df \
        .withColumn("event_time", from_unixtime(col("ts") / 1000)) \
        .withColumn("year", year("event_time")) \
        .withColumn("month", month("event_time")) \
        .withColumn("day", dayofmonth("event_time")) \
        .withColumn("hour", hour("event_time"))

    # Write to HDFS
    query = processed_df.writeStream \
        .foreachBatch(process_batch) \
        .outputMode("append") \
        .option("checkpointLocation", "hdfs://namenode:9000/user/checkpoints/events") \
        .trigger(processingTime="1 minute") \
        .start()

    # Wait for termination
    query.awaitTermination()

if __name__ == "__main__":
    main()