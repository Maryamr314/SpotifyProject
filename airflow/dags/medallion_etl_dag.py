from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'medallion_etl_pipeline',
    default_args=default_args,
    description='A DAG to orchestrate the medallion architecture ETL',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2025, 3, 2),
    catchup=False,
    tags=['medallion', 'etl', 'dbt'],
)

# Task to run the Spark streaming job (bronze layer)
# This would typically be managed separately but included here for completeness
start_bronze_ingest = SparkSubmitOperator(
    task_id='start_bronze_ingest',
    application='/opt/airflow/dags/spark_scripts/start_bronze_ingest.py',
    conn_id='spark_default',
    application_args=['--bootstrap-servers', 'broker:9092'],
    verbose=True,
    dag=dag,
)

# Transform Bronze to Silver using DBT
run_dbt_silver = BashOperator(
    task_id='run_dbt_silver',
    bash_command='cd /opt/dbt && dbt run --select silver --profiles-dir profiles',
    dag=dag,
)

# Transform Silver to Gold using DBT
run_dbt_gold = BashOperator(
    task_id='run_dbt_gold',
    bash_command='cd /opt/dbt && dbt run --select gold --profiles-dir profiles',
    dag=dag,
)

# Load Gold data into ClickHouse
load_to_clickhouse = BashOperator(
    task_id='load_to_clickhouse',
    bash_command='''
    clickhouse-client --host clickhouse-server