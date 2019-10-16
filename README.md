# Subscriptions: Egress service

[![License](https://img.shields.io/badge/license-APACHE2-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0.html)

## Get Started

Required environment variables:

Data egress:

- `CEPH_URL` - Url to S3/Ceph storage
- `CEPH_BUCKET` - Bucket name
- `CEPH_COLLECTION_NAME` - Master collection name in said bucket
- `CEPH_ACCESS_KEY_ID` - Credentials
- `CEPH_SECRET_ACCESS_KEY` - Credentials

Data ingress:

- `DATABASE_HOST` - DB hostname
- `DATABASE_PORT` - DB port
- `DATABASE_NAME` - DB name
- `DATABASE_USER` - Credentials
- `DATABASE_PASSWORD` - Credentials
- `COLLECTIONS` - CSV list of tables to collect

Currently the database type set to PostgreSQL - Only supported DB type.

## License

See [LICENSE](LICENSE)
