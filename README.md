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
    --lifecycle-configuration file:/`pwd`/aws/bucket_lifecycle.json
```

### Step 2: Create the data egress pipeline

First, [create](https://docs.aws.amazon.com/cli/latest/reference/datapipeline/create-pipeline.html) the pipeline object

```sh
$ aws datapipeline create-pipeline --name data_egress --unique-id <TOKEN>
```

Next, populate it from attached template

```sh
$ aws datapipeline put-pipeline-definition
    --pipeline-definition file:/`pwd`/aws/data_pipeline.json \
    --pipeline-id <PIPELINE_ID> \
    --parameter-values \
        RDS_username=<DB_USERNAME> \
        RDS_password=<DB_PASSWORD> \
        RDS_jdbc=<jdbc:postgresql://dbinstance.id.region.rds.amazonaws.com:5432/dbname> \
        RDS_table_name=<COLLECTION_NAME> \
        S3_path=<S3_BUCKET_PATH_FOR_OUTPUT_DATA> \
        S3_logs=<S3_LOGS_PATH>
```

Now activate the pipeline

```sh
$ aws datapipeline activate-pipeline --pipeline-id <PIPELINE_ID>
```

Check the status of your pipeline

```sh
$ aws datapipeline list-runs --pipeline-id <PIPELINE_ID>
```

Let the pipeline complete, then check the output S3 bucket for the output csv file. Congratulations, you have now set up your database to be exported into CSV each day.

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

### Step 2: Deploy Egress Cron job

And finally, deploy the Kubernetes cron job. This job uses a [MinIO client](https://docs.min.io/docs/minio-client-quickstart-guide.html) and performs a `mirror` operation to sync S3 bucket to Ceph. Both input and output urls and paths are determined based on the secrets from previous step.

```sh
$ oc process -f openshift/deploy.yaml | oc create -f -
```

## License

See [LICENSE](LICENSE)
