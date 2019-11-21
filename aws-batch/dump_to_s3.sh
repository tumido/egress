#!/bin/sh

# List of expected environment variables:
#   TABLES= space separated list of tables to dump
#   S3_OUTPUT= S3 location in format s3://bucket/path
#
#   PGHOST= PostgreSQL host
#   PGPORT= PostgreSQL port
#   PGUSER= PostgreSQL user
#   PGPASSWORD= PostgreSQL password
#   PGDATABASE= PostgreSQL database name

set -e

if  [ -z "$TABLES" ] || [ -z "$S3_OUTPUT" ] ||\
    [ -z "$PGHOST" ] || [ -z "$PGPORT" ] || \
    [ -z "$PGUSER" ] || [ -z "$PGPASSWORD" ] || \
    [ -z "$PGDATABASE" ]
then
    echo "Environment not set properly. Exiting." 1>&2
    exit 1
fi

date=`date -I`

for table in $TABLES; do
    echo "Copying data from $table..."

    # Stream the data as CSV through a pipe to GZIP for compression and then to S3
    psql -h $PGHOST -p $PGPORT -U $PGUSER $PGDATABASE -c "COPY $table TO STDOUT WITH CSV HEADER" |
    gzip -9 |
    aws s3 cp --storage-class STANDARD_IA --sse aws:kms - ${S3_OUTPUT}/${date}/${table}.csv.gz
done
