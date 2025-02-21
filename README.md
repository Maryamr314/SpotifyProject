# Spotify Event Processing Pipeline

A scalable, real-time data processing pipeline that handles music listening events using Apache Kafka, Apache Spark, and Hadoop. The system processes streaming music event data, storing it in a structured format for further analysis.

## Architecture Overview

![Architecture Diagram]

### Components:
- **Apache Kafka**: Message broker for real-time event streaming
- **Schema Registry**: Manages data schemas
- **Kafka Connect**: Data integration tool
- **Eventsim**: Generates simulated Spotify-like events
- **Apache Spark**: Real-time stream processing
- **Apache Hadoop (HDFS)**: Distributed storage
- **Redpanda Console**: Kafka monitoring UI

## Prerequisites

- Docker and Docker Compose
- Minimum 8GB RAM
- 20GB free disk space

## Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd <project-directory>
```

2. **Start the services**
```bash
docker-compose up -d
```

3. **Create necessary HDFS directories**
```bash
docker exec -it namenode hdfs dfs -mkdir -p /user/events/bronze
docker exec -it namenode hdfs dfs -mkdir -p /user/checkpoints/events
docker exec -it namenode hdfs dfs -chmod -R 777 /user
```

4. **Submit the Spark streaming job**
```bash
docker exec spark-master spark-submit \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    --master spark://spark-master:7077 \
    /opt/bitnami/spark/apps/kafka_consumer.py
```

## Data Flow

1. **Event Generation**: Eventsim generates simulated music listening events
2. **Event Ingestion**: Events are published to Kafka
3. **Stream Processing**: Spark processes the events in real-time
4. **Storage**: Processed data is stored in HDFS with Hive partitioning

## Data Structure

The data is stored in the following structure:
```
/user/events/bronze/
    ├── year=YYYY/
        ├── month=MM/
            ├── day=DD/
                ├── hour=HH/
                    ├── part-XXXXX.parquet
```

## Monitoring

- **Kafka UI**: http://localhost:8082
- **Spark Master**: http://localhost:8080
- **HDFS NameNode**: http://localhost:9870

## Development

### Project Structure
```
project/
├── docker-compose.yml
├── spark/
│   └── apps/
│       └── kafka_consumer.py
└── README.md
```

### Event Schema
```python
{
    "artist": string,
    "song": string,
    "duration": double,
    "ts": long,
    "sessionId": integer,
    "auth": string,
    "level": string,
    "itemInSession": integer,
    "city": string,
    "zip": string,
    "state": string,
    "userAgent": string,
    "lon": double,
    "lat": double,
    "userId": integer,
    "lastName": string,
    "firstName": string,
    "gender": string,
    "registration": long
}
```

## Maintenance

### Cleaning Up
```bash
# Stop all services and remove volumes
docker-compose down -v

# Remove stopped containers
docker rm $(docker ps -a -q)

# Clean up volumes
docker volume prune -f
```

### Checking Data
```bash
# List bronze layer contents
docker exec -it namenode hdfs dfs -ls -R /user/events/bronze

# Check data size
docker exec -it namenode hdfs dfs -du -h /user/events/bronze
```

## Troubleshooting

1. **If Kafka is not receiving events**:
    - Check Eventsim logs: `docker logs eventsim`
    - Verify topic in Redpanda Console

2. **If Spark job fails**:
    - Check Spark logs: `docker logs spark-master`
    - Verify all dependencies are available

3. **If HDFS is not accessible**:
    - Check NameNode status: `docker logs namenode`
    - Verify network connectivity between containers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License.