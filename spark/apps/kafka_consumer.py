from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, from_unixtime
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, LongType, IntegerType
)

def main():
    spark = SparkSession.builder \
        .appName("KafkaListenEventsConsumer") \
        .getOrCreate()
    

    spark.sparkContext.setLogLevel("WARN")
    

    kafka_bootstrap_servers = "broker:9092"  
    kafka_topic = "listen_events"             
    
    schema = StructType([
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
    

    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("subscribe", kafka_topic) \
        .option("startingOffsets", "earliest") \
        .option("maxOffsetsPerTrigger", 10) \
        .load()
    
    # Convert the binary 'value' column to string and parse JSON
    parsed_df = kafka_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")
    
    # Assuming 'ts' is in milliseconds since epoch
    parsed_df = parsed_df.withColumn("event_time", from_unixtime(col("ts") / 1000))
    
    # Select columns you want to display or process
    final_df = parsed_df.select(
        "event_time",
        "artist",
        "song",
        "duration",
        "sessionId",
        "auth",
        "level",
        "itemInSession",
        "city",
        "zip",
        "state",
        "userAgent",
        "lon",
        "lat",
        "userId",
        "lastName",
        "firstName",
        "gender",
        "registration"
    )
    
    # Write the output to the console with trigger once
    query = final_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "true") \
        .option("numRows", 10) \
        .start()
    
    # Await termination to complete the processing
    query.awaitTermination()

if __name__ == "__main__":
    main()