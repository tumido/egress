# Create the data egress pipeline using OpenShift CronJob

## Prerequisites

This setup assumes you have a PostgreSQL secret `postgresql` available in your openShift project. Then it is required to have another secret available to you, called `aws`. It contains the AWS credentials the job can use:

```sh
$ oc create secret generic aws \
    --from-literal=access-key-id=<CREDENTIALS>
    --from-literal=secret-access-key=<CREDENTIALS>
```

Both these secrets are described in the `setup.yaml` as well.

## Deploy the job

```sh
$ oc process -f deploy.yaml \
    -p S3_OUTPUT=<s3://bucket/path> \
    -p TABLES="<space separated list of tables to dump>" \
    -p PGHOST=<PostgreSQL hostname (default: postgresql)> \
    -p PGPORT=<PostgreSQL port (default: 5432)> \
  | oc apply -f -
```

As a result a cron job is defined. It is det to run daily. On each run it would collect each table from `TABLES` in your database and save it as a `<table>.csv.gz` in `s3://bucket/path/<DATE>/`.
