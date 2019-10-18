"""Egress configuration loader from environment."""
import os
import json

os.environ['SPARK_CONF_DIR'] = os.getcwd()

CEPH_URL = os.getenv('CEPH_URL')
CEPH_SECURE_BUCKET = os.getenv('CEPH_SECURE_BUCKET')
CEPH_PUBLIC_BUCKET = os.getenv('CEPH_PUBLIC_BUCKET')
CEPH_COLLECTION_NAME = os.getenv('CEPH_COLLECTION_NAME')
CEPH_ACCESS_KEY_ID = os.getenv('CEPH_ACCESS_KEY_ID')
CEPH_SECRET_ACCESS_KEY = os.getenv('CEPH_SECRET_ACCESS_KEY')

DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_NAME = os.getenv('DATABASE_NAME')

DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

SCHEMA_JSON = os.getenv('SCHEMA_JSON')

# Guards
assert all(constant for constant in (
    CEPH_URL, CEPH_SECURE_BUCKET, CEPH_PUBLIC_BUCKET, CEPH_COLLECTION_NAME,
    CEPH_ACCESS_KEY_ID, CEPH_SECRET_ACCESS_KEY
)), 'Environment is not set properly, error in CEPH_* configuration'

assert all(constant for constant in (
    DATABASE_HOST, DATABASE_PORT,
    DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD,
)), 'Environment is not set properly, error in database configuration'

assert SCHEMA_JSON, 'Missing schema specification'
with open(SCHEMA_JSON) as f:
    SCHEMA = json.load(f)
assert SCHEMA, 'Missing schema specification'
