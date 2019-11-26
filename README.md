# Egress service

[![License](https://img.shields.io/badge/license-APACHE2-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0.html)

Data egress service is intended to export data from Amazon RDS to Data Hub on regular schedule and in a structured way.

## Process Overview

1. Input data are expected to be located in a Amazon RDS, presumably PostgreSQL.
2. OpenShift `CronJob` on the application cluster side snapshots the database into Amazon S3 as CSV dumps.
3. OpenShift `CronJob` on the target network side synchronizes S3 to Ceph.

![Data flow](../media/dataflow.png?raw=true)

## Prerequisites

Outward facing intermediate storage in the project is a necessity. Please set up an S3 bucket:

1. You must have the [AWS CLI](https://github.com/aws/aws-cli) installed and configured.
2. See [here](http://docs.aws.amazon.com/AmazonS3/latest/UG/CreatingaBucket.html) for instructions on how to create an S3 bucket of follow this guide. Please make sure the S3 bucket has a policy that allows writing of the data with the credentials you provide to the cron job.
3. Set a lifecycle policy, that deletes objects older than few days (default is 7 in our policy, but can be changed). This is a failsafe mechanism, that allows us to retain historical data even if a [Sync job](#sync-job) fails and gives us a few days to fix the issue.

```sh
$ aws s3api create-bucket --bucket <BUCKET_NAME>
{
    "Location": "/<BUCKET_NAME>"
}

$ aws s3api put-bucket-lifecycle-configuration  \
    --bucket <BUCKET_NAME>  \
    --lifecycle-configuration file://bucket_lifecycle.json
```

## Data dump job

This job is intended to be run on the APP side. It collects all data from given tables and stores them in a compressed CSVs in your S3 bucket.

Specification of this job is available in the `openshift-crc` folder.

### Step 1: Populate secrets for dump job

The job assumes you have a PostgreSQL secret `postgresql` available in your OpenShift project. Next you are required to have another secret available to you, called `aws`. It contains the AWS credentials the job can use:

```sh
$ oc create secret generic aws \
    --from-literal=access-key-id=<CREDENTIALS> \
    --from-literal=secret-access-key=<CREDENTIALS>

secret/aws created
```

Both these secrets are described in the `setup.yaml` as well.

### Step 2: Deploy dump cron job

```sh
$ oc process -f openshift-crc/deploy.yaml \
    -p S3_OUTPUT=<s3://bucket/path> \
    -p TABLES="<space separated list of tables to dump>" \
    -p PGHOST=<PostgreSQL hostname (default: postgresql)> \
    -p PGPORT=<PostgreSQL port (default: 5432)> \
  | oc create -f -

buildconfig.build.openshift.io/egress-bc created
imagestream.image.openshift.io/egress-is created
cronjob.batch/egress-cj created
```

As a result a cron job is defined. It is set to run daily. On each run it would collect each table from `TABLES` in your database and save it as a `<table>.csv.gz` in `s3://bucket/path/<DATE>/`.

### Run

Once the cron job is run, you should be able to query for it's logs. It should look like this:

```sh
$ oc log `oc get pods -o=name --selector=job-name | tail -1`

Table 'tally_snapshots': Data collection started.
Table 'tally_snapshots': Dump uploaded to intermediate storage.
Table 'subscription_capacity': Data collection started.
Table 'subscription_capacity': Dump uploaded to intermediate storage.
Success.
```

## Sync job

Second part of the Egress is to get the data in Amazon S3 over to Datahub's Ceph. To do so, we define a OpenShift cron job, that would sync content of your buckets using [MinIO client](https://docs.min.io/docs/minio-client-quickstart-guide.html).

Specification of this job is available in the `openshift-dh` folder.

### Step 1: Populate secrets for sync job

Follow the prescription in `openshift-dh/setup.yaml` template, or use the cli:

```sh
$ oc create secret generic egress-input \
    --from-literal=url=<S3_ENDPOINT> \
    --from-literal=path=<S3_PATH> \
    --from-literal=access-key-id=<CREDENTIALS> \
    --from-literal=secret-access-key=<CREDENTIALS>

secret/egress-input created

$ oc create secret generic egress-output \
    --from-literal=url=<S3_ENDPOINT> \
    --from-literal=path=<S3_PATH> \
    --from-literal=access-key-id=<CREDENTIALS> \
    --from-literal=secret-access-key=<CREDENTIALS>

secret/egress-output created
```

Please note the `S3_ENDPOINT` refers to the S3 host. For example:

- AWS S3 service: `https://s3.amazonaws.com`
- Google Cloud Storage: `https://storage.googleapis.com`
- etc..

The `S3_PATH` denotes the path for a bucket or its subfolder:

- It can be simply a bucket name: `my_bucket`
- It can also be a relative path to a folder within this bucket `my_bucket/folder_in_top_level/target_folder`

### Step 2: Deploy sync cron job

And finally, deploy the Kubernetes cron job. This job uses a [MinIO client](https://docs.min.io/docs/minio-client-quickstart-guide.html) and performs a `mirror` operation to sync S3 bucket to Ceph. Both input and output urls and paths are determined based on the secrets from previous step.

```sh
$ oc process -f openshift-dh/deploy.yaml | oc create -f -

cronjob.batch/egress-cj created
```

### Run

The `openshift-dh/deploy.yaml` describes a cron job. By default this job is set to run daily. Once this job is executed, you should receive log containing all the synced files:

```sh
$ oc log `oc get pods -o=name --selector=job-name | tail -1`

Added `input` successfully.
Added `output` successfully.
`input/tcoufal/2019-11-21/subscription_capacity.csv.gz` -> `output/DH-SECURE-USIR/2019-11-21/subscription_capacity.csv.gz`
`input/tcoufal/2019-11-21/tally_snapshots.csv.gz` -> `output/DH-SECURE-USIR/2019-11-21/tally_snapshots.csv.gz`
Total: 17.38 MiB, Transferred: 17.38 MiB, Speed: 18.77 MiB/s
```

## License

See [LICENSE](LICENSE)
