# Create the data egress pipeline using AWS Data Pipelines

[Create](https://docs.aws.amazon.com/cli/latest/reference/datapipeline/create-pipeline.html) the pipeline object

```sh
$ aws datapipeline create-pipeline --name data_egress --unique-id <TOKEN>
```

Next, populate it from attached template (and [yes](https://docs.aws.amazon.com/datapipeline/latest/DeveloperGuide/dp-custom-templates.html#add-pipeline-variables), AWS Data pipelines requires the variable names to start with `my`)

```sh
$ aws datapipeline put-pipeline-definition
    --pipeline-definition file:/`pwd`/aws-datapipelines/data_pipeline.json \
    --pipeline-id <PIPELINE_ID> \
    --parameter-values \
        my_RDS_username=<DB_USERNAME> \
        my_RDS_password=<DB_PASSWORD> \
        my_RDS_jdbc=<jdbc:postgresql://dbinstance.id.region.rds.amazonaws.com:5432/dbname> \
        my_RDS_table_name=<COLLECTION_NAME> \
        my_S3_path=<S3_BUCKET_PATH_FOR_OUTPUT_DATA> \
        my_S3_logs=<S3_LOGS_PATH>
```

Now activate the pipeline

```sh
$ aws datapipeline activate-pipeline --pipeline-id <PIPELINE_ID>
```

Check the status of your pipeline

```sh
$ aws datapipeline list-runs --pipeline-id <PIPELINE_ID>
```

Let the pipeline complete, then check the output S3 bucket for the output csv file.
