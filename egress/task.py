"""Egress coordinator module."""
import os
from datetime import datetime

from pyspark.sql import SparkSession

CEPH_URL = os.getenv('CEPH_URL')
CEPH_BUCKET = os.getenv('CEPH_BUCKET')
CEPH_COLLECTION_NAME = os.getenv('CEPH_COLLECTION_NAME')
CEPH_ACCESS_KEY_ID = os.getenv('CEPH_ACCESS_KEY_ID')
CEPH_SECRET_ACCESS_KEY = os.getenv('CEPH_SECRET_ACCESS_KEY')


def get_local_spark_context():
    """Configure and create local Spark SQL context."""

    return SparkSession.builder \
        .master('local') \
        .appName('Subscription Egress service') \
        .config('spark.hadoop.fs.s3a.access.key', CEPH_ACCESS_KEY_ID) \
        .config('spark.hadoop.fs.s3a.secret.key', CEPH_SECRET_ACCESS_KEY) \
        .config('spark.hadoop.fs.s3a.endpoint', CEPH_URL) \
        .getOrCreate()


def fetch_postgres_data(spark_context):
    """Fetch data from internal DB. This data will be pushed to DH."""

    return []


def push_to_ceph(spark_context, data):
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
    data = fetch_postgres_data(spark_context)
    # Push to Data Hub's Ceph
    push_to_ceph(spark_context, data)
