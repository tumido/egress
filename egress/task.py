"""Egress coordinator module."""
from datetime import datetime

from pyspark.sql import SparkSession, DataFrame

from .config import (
    CEPH_URL, CEPH_BUCKET, CEPH_COLLECTION_NAME,
    CEPH_ACCESS_KEY_ID, CEPH_SECRET_ACCESS_KEY,
    DATABASE_HOST, DATABASE_PORT, DATABASE_NAME,
    DATABASE_USER, DATABASE_PASSWORD,
    COLLECTIONS
)

JDBC_URL = \
    f'jdbc:postgresql://{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

JDBC_OPTIONS = dict(
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    driver='org.postgresql.Driver'
)


def get_local_spark_context():
    """Configure and create local Spark SQL context."""

    return SparkSession.builder \
        .master('local') \
        .appName('Subscription Egress service') \
        .config('spark.hadoop.fs.s3a.access.key', CEPH_ACCESS_KEY_ID) \
        .config('spark.hadoop.fs.s3a.secret.key', CEPH_SECRET_ACCESS_KEY) \
        .config('spark.hadoop.fs.s3a.endpoint', CEPH_URL) \
        .config('spark.jars', '/usr/share/java/postgresql-jdbc.jar') \
        .getOrCreate()


def fetch_postgres_data(spark_context: SparkSession, table: str) -> DataFrame:
    """Fetch data from internal DB. This data will be pushed to DH."""
    return spark_context.read.jdbc(
        JDBC_URL, table, properties=JDBC_OPTIONS
    )


def push_to_ceph(spark_context: SparkSession, data: DataFrame):
    """Convert data to a DataFrame and push it to Ceph storage."""
    day = datetime.now().date().day
    uri = f's3a://{CEPH_BUCKET}/{day}/{CEPH_COLLECTION_NAME}'

    data_frame = spark_context.createDataFrame(data)

    return data_frame.write.mode('overwrite').parquet(uri)


def run_task():
    """Egress coordinator."""

    # Create local spark session to simplify the Parquet works
    spark_context = get_local_spark_context()
    # Fetch data from Postgres
    for table in COLLECTIONS:
        data = fetch_postgres_data(spark_context, table)
        data.show()
    # Push to Data Hub's Ceph
    # push_to_ceph(spark_context, data)
