# Egress service

[![License](https://img.shields.io/badge/license-APACHE2-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0.html)

Data egress service is intended to export data from Amazon RDS to Data Hub on regular schedule and in a structured way.

## Process Overview

1. Input data are expected to be located in a Amazon RDS, presumably PostgreSQL.
2. An Amazon Data Pipeline is created. This pipeline snapshots the database into Amazon S3 as CSV dumps. Each synchronized table requires a separate pipeline.
3. S3 is synchronized to Ceph via CronJob.

## Data pipeline

This section explains how to deploy a [data pipeline](https://aws.amazon.com/datapipeline/) that outputs content of a table in RDS database to an S3 bucket. It provides the [pipeline definition file](http://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-writing-pipeline-definition.html) which is used to create the pipeline and the AWS CLI commands for creating and executing the pipeline.

### Prerequisites

1. You must have the [AWS CLI](https://github.com/aws/aws-cli) installed and configured.
2. Your database must be accessible from a region where AWS data pipelines [are available](https://aws.amazon.com/about-aws/whats-new/2014/02/20/aws-data-pipeline-now-available-in-four-new-regions/).

### Step 1: Create and setup S3 bucket

Before we can start with the pipeline, you need to have S3 bucket with write permissions set up. See [here](http://docs.aws.amazon.com/AmazonS3/latest/UG/CreatingaBucket.html) for instructions on how to create an S3 bucket of follow this guide. If you choose to provide your own S3 path to an existing bucket, the bucket must be in the same region as what is set for your AWS CLI configuration. Finally, please make sure the S3 bucket has a policy that allows data writes to it.

```sh
$ aws s3api create-bucket --bucket <BUCKET_NAME>
```

To limit the data stored in this bucket, you can modify the object lifecycle

```sh
$ aws s3api put-bucket-lifecycle-configuration  \
    --bucket <BUCKET_NAME>  \
    --lifecycle-configuration file:/`pwd`/aws-datapipelines/bucket_lifecycle.json
```

### Step 2: Data dump job

Choose one option from the available solutions:

- [AWS Data pipelines](aws-datapipelines/README.md)
- [AWS Batch](aws-batch/README.md)
- [OpenShift CronJob deployed on the application side](openshift-crc-side/README.md)

Follow the guidelines. As a result you should end up with a periodically invoked job, that would dump the desired data into S3.

## Sync job

Second part of the Egress is to get the data in Amazon S3 over to Datahub's Ceph. To do so, we define a OpenShift cron job, that would sync content of your buckets using [MinIO client](https://docs.min.io/docs/minio-client-quickstart-guide.html).

### Prerequisites

OpenShift's `oc` client is required to be installed and configured.

### Step 1: Set and deploy secrets

Follow the prescription in `openshift/setup.yaml` template, or use the cli:

```sh
# change setup.yaml
$ oc process -f openshift/setup.yaml | oc create -f -
```

or

```sh
$ oc create secret generic egress-input \
    --from-literal=url=<S3_ENDPOINT>
    --from-literal=path=<S3_PATH>
    --from-literal=access-key-id=<CREDENTIALS>
    --from-literal=secret-access-key=<CREDENTIALS>

$ oc create secret generic egress-output \
    --from-literal=url=<S3_ENDPOINT>
    --from-literal=path=<S3_PATH>
    --from-literal=access-key-id=<CREDENTIALS>
    --from-literal=secret-access-key=<CREDENTIALS>
```

Please note the `S3_ENDPOINT` refers to the S3 host. For example:

- AWS S3 service: `https://s3.amazonaws.com`
- Google Cloud Storage: `https://storage.googleapis.com`
- etc..

The `S3_PATH` denotes the path for a bucket or its subfolder:

- It can be simply a bucket name: `my_bucket`
- It can also be a relative path to a folder within this bucket `my_bucket/folder_in_top_level/target_folder`

### Step 2: Deploy Egress Cron job

And finally, deploy the Kubernetes cron job. This job uses a [MinIO client](https://docs.min.io/docs/minio-client-quickstart-guide.html) and performs a `mirror` operation to sync S3 bucket to Ceph. Both input and output urls and paths are determined based on the secrets from previous step.

```sh
$ oc process -f openshift/deploy.yaml | oc create -f -
```

### Run

The `openshift/deploy.yaml` describes a cron job. By default this job is set to run daily. Once this job is executed, you should receive log containing all the synced files:

```
Added `input` successfully.
Added `output` successfully.
`input/ladas-report-test/tcoufal_test/input/sample.csv` -> `output/ladas-report-test/tcoufal_test/output/sample.csv`
Total: 18 B, Transferred: 18 B, Speed: 159 B/s
```

## License

See [LICENSE](LICENSE)
