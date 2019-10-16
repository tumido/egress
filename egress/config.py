"""Egress configuration loader from environment."""
import os
import re

CEPH_URL = os.getenv('CEPH_URL')
CEPH_BUCKET = os.getenv('CEPH_BUCKET')
CEPH_COLLECTION_NAME = os.getenv('CEPH_COLLECTION_NAME')
CEPH_ACCESS_KEY_ID = os.getenv('CEPH_ACCESS_KEY_ID')
CEPH_SECRET_ACCESS_KEY = os.getenv('CEPH_SECRET_ACCESS_KEY')

DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_URL = \
    f'jdbc:postrgesql://{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_OPTIONS = dict(user=DATABASE_USER, password=DATABASE_PASSWORD)

COLLECTIONS = re.sub(r'\s', '', os.getenv('COLLECTIONS', '')).split(',')

# Guards
assert all(constant for constant in (
    CEPH_URL, CEPH_BUCKET, CEPH_COLLECTION_NAME,
    CEPH_ACCESS_KEY_ID, CEPH_SECRET_ACCESS_KEY
)), 'Environment is not set properly, error in CEPH_* configuration'

assert all(constant for constant in (
    DATABASE_HOST, DATABASE_PORT,
    DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD,
    COLLECTIONS
)), 'Environment is not set properly, error in database configuration'
