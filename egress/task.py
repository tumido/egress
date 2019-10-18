"""Egress coordinator module."""
from datetime import datetime

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import sha2
from py4j.protocol import Py4JJavaError

from .logging import get_logger
from .config import (
    CEPH_URL, CEPH_SECURE_BUCKET, CEPH_PUBLIC_BUCKET, CEPH_COLLECTION_NAME,
    CEPH_ACCESS_KEY_ID, CEPH_SECRET_ACCESS_KEY,
    DATABASE_HOST, DATABASE_PORT, DATABASE_NAME,
    DATABASE_USER, DATABASE_PASSWORD,
    SCHEMA
)

JDBC_URL = \
    f'jdbc:postgresql://{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

JDBC_OPTIONS = dict(
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    driver='org.postgresql.Driver'
)

logger = get_logger(__name__)


def get_local_spark_context() -> SparkSession:
    """
    Configure and create local Spark SQL context.

    Use Session builder to spin up a local spark, configure it to use S3
    credentials and point it to proper JDBC driver lib file.

    Returns:
        SparkSession: Local Spark context.

    Raises:
        Py4JJavaError: Propagates Py4J error when Java fails to create context
    """

    try:
        return SparkSession.builder \
            .master('local') \
            .appName('Subscription Egress service') \
            .config('spark.hadoop.fs.s3a.access.key', CEPH_ACCESS_KEY_ID) \
            .config('spark.hadoop.fs.s3a.secret.key', CEPH_SECRET_ACCESS_KEY) \
            .config('spark.hadoop.fs.s3a.endpoint', CEPH_URL) \
            .config('spark.jars', '/usr/share/java/postgresql-jdbc.jar') \
            .getOrCreate()
    except Py4JJavaError as e:
        logger.error('Failed to create SparkSession: %s', e, exc_info=True)
        raise


def fetch_postgres_data(spark_context: SparkSession, table: str) -> DataFrame:
    """
    Fetch data from internal DB.

    Uses `spark_context` to access database. Then it pulls data from table
    `table`. This data is retuned as a plain DataFrame.

    Arguments:
        spark_context (SparkSession): Java Spark session executor
        table (str): Name of the table which should be read

    Returns:
        DataFrame: Contains data of `table`

    Raises:
        Py4JJavaError: Propagates Py4J error when JDBC fails read data from DB

    """
    try:
        return spark_context.read.jdbc(
            JDBC_URL, table, properties=JDBC_OPTIONS
        )
    except Py4JJavaError as e:
        logger.error(
            'Failed to read data from "%s" table "%s": %s',
            JDBC_URL, table, e, exc_info=True
        )
        raise


def anonymize_data_frame(df: DataFrame, columns: list) -> DataFrame:
    """
    Replaces sensitive columns data with hashed values.

    Takes `data_frame` and replaces each value in each of `columns` with a
    hashed value, making the original value unreadable, yet maintains
    consistency.

    Arguments:
        df (DataFrame): Data view to be anonymized
        columns (list): Columns containing sensitive data

    Returns:
        DataFrame: Modified original dataframe
    """
    for column in columns:
        df = df.withColumn(column, sha2(df[column], 256))

    return df


def push_to_ceph(df: DataFrame, bucket: str):
    """
    Convert data to a DataFrame and push it to Ceph storage.

    Arguments:
        df (DataFrame): Data table meant to be saved on Ceph
        bucket (str): Bucket name

    Returns:
        None

    Raises:
        Py4JJavaError: Propagates Py4J error when push fails
    """
    day = datetime.now().date().day
    uri = f's3a://{bucket}/{day}/{CEPH_COLLECTION_NAME}'

    try:
        return df.write.mode('overwrite').parquet(uri)
    except Py4JJavaError as e:
        logger.error('Failed to push to Data Hub: %s', e, exc_info=True)
        raise


def run_task():
    """Egress coordinator."""
    logger.info('Job initiated', extra=dict(url=JDBC_URL, schema=SCHEMA))

    # Create local spark session to simplify the Parquet works
    spark_context = get_local_spark_context()

    for table, sensitive_cols in SCHEMA.items():
        # Fetch data from PostgreSQL
        df = fetch_postgres_data(spark_context, table)

        logger.info(
            'Table collected',
            extra=dict(
                table=table,
                table_schema=df.schema.json(),
                table_rows=df.count()
            )
        )

        # Push to Data Hub's Ceph - with sensitive data
        push_to_ceph(df, CEPH_SECURE_BUCKET)

        # Anonymize
        df = anonymize_data_frame(df, sensitive_cols)

        # Push to Data Hub's Ceph - anonymized
        push_to_ceph(df, CEPH_PUBLIC_BUCKET)

        logger.info(
            'Table processed',
            extra=dict(
                table=table,
                table_schema=df.schema.json(),
                table_rows=df.count()
            )
        )

    logger.info('Success', extra=dict(url=JDBC_URL, schema=SCHEMA))
