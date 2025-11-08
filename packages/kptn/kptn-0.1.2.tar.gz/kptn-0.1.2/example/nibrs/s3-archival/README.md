# AWS S3 Archival and Restoration

After the completion of a pipeline run, files can be moved from EFS to S3 for cheaper long-term storage. Archival with DataSync is straightforward. Restoration is more involved and can take a couple days. This document goes over steps to restore from Deep Archive, but use your best judgement on which S3 tier to use. Retrieval from Deep Archive costs more and should only be used for files that are not planned for retrieval any time soon.

**A note on S3 API**

S3 API operates on single objects. To operate on multiple objects, you must generate a list, a "manifest", which is CSV file with two columns: the bucket and the object path. This file is generated easily using the manifest-generator script in this directory, which is provided by AWS. It can also be generated from the UI with S3 Inventory, but that takes 48 hours, is intended to run on a schedule, and only allows specifying a single prefix. A prefix is what a subdirectory path is called in S3.

## Backing Up Files

Use AWS DataSync to copy files from EFS to S3. We use the bucket named `nibrsep-archive`.

### Using DataSync to move from EFS to S3 Glacier

1. Go to DataSync service in AWS UI
1. Ensure you are in the region with the EFS you want to archive data from.
1. Go to `Tasks` & click `Create task`
1. Configure source location
    * Check `Choose an existing location` to see if the EFS has already been configured as a location for archival source.
    * If not then use `Create a new location`
        * Select location type as `Amazon EFS file system`
        * Select the current region
        * Select the EFS from the filesystem list
        * Leave mount path blank
        * Select any `publicSubnet` as the subnet
        * For security group select `...nibrsFoundation-...-jumpboxSecurityGroup...`
        * Tag the resource with the project-number
1. Configure destination location
    * Check `Choose an existing location` to see if the archival bucket `nibrsep-archive` is already configured as a location for archival desination.
    * If not then use `Create a new location`
        * Select location type as `Amazon S3`
        * Select region as `us-east-1`
        * Use the `Browse S3` button to find and select `nibrsep-archive`
        * For S3 storage class depends on what type of archival this task is for (recommendations: `Standard` for testing, `Glacier Deep Archive` for data that has no plans on needing accessed again).
        * IAM role just use the default
        * Tag the resource with the project-number
1. Configure settings
    * Task mode use `Basic`
    * Give the task a name
    * Source data options
        * Most likely need to select `Specific files, objects, and folders`
        * `Using filters`
        * Add a pattern to `Includes` (example `/smoketest_1/`)
    * Transfer options
        * Transfer mode `Transfer all data`
        * Verification `Verify only transferred data`
        * Bandwidth limit -> `Use available`
    * Tag the resource with the project-number
    * Don't worry about `Schedule` or `Task Report`
    * Logging
        * Log Level -> `Basic such as transfer errors`
        * CloudWatch log group -> `/aws/datasync`
1. Review -> Just review and create task
1. Manually trigger the task
    * Select the task from the task list
    * In the top-right select `Start` and `Start with defaults`

### After DataSync

After completion, delete the files from EFS by SSHing to the EC2 instance and running a command similar to this:

```
sudo rm -fr efs/run_prodnibrs_smr2024_data2022_202406/ &
```

Where `run_prodnibrs_smr2024_data2022_202406` is the directory to be deleted and `&` tells the process to run in the background. You can then exit the SSH session. To monitor the process, use `ps -aef | grep rm`. To monitor the EFS storage, go to the EFS file system in the AWS Console and view the Monitoring tab.

## Restoring Files from Deep Archive - One File

If you are looking to restore just a few files, you can do it manually through the AWS interface.

1. Go to the AWS Console > S3
2. Find the `nibrsep-archive` bucket
3. Navigate to the file in S3 and select it
4. Click the Actions button, and then click "Initiate restore"
5. Kick off a Standard retrieval (12 hours), available for a desired number of days.
6. If you refresh the page it should say "restoration in progress." Wait 12 hours and refresh, you should be able to download the file.

For more info, see the [AWS documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects.html#restore-archived-objects).

## Restoring Files from Deep Archive - Many Files

If you are looking to restore multiple files, you will likely want to us the batch option.

1. Generate a manifest of files to restore
2. Upload manifest
3. Create the S3 Batch job to restore
4. Run the S3 Batch job
5. Wait for the files to be restored
6. Run the DataSync task to copy the files to EFS

### 1. Generate a manifest

In this step, we'll use an aws-sdk and NodeJS script to fetch the list of files in a bucket at a given prefix, generating an output file called the manifest.

Install:

```
cd manifest-generator
npm install
```

Use:

```
AWS_PROFILE=nibrs node index.js source_bucket bucket_prefix output_file
```

Example:

```
node index.js nibrsep-archive run_prodnibrs_smr2024_data2023_202406/flow_runall/indicator_table_estimates_after_variance manifest-indicators.csv
```

**NOTE:** You will most likely get a large red warning saying `(node:1098) NOTE: We are formalizing our plans to enter AWS SDK for JavaScript (v2) into maintenance mode in 2023.` when running the script. It can safely be ignored, just verify the manifest file was created.

Combine multiple manifests into a single manifest:

```
cat manifest-indicators.csv manifest-momentum.csv > manifest.csv
```

### 2. Upload manifest

1. Go AWS > S3 > nibrs-archive bucket > nibrs-archive directory ([link](https://us-east-1.console.aws.amazon.com/s3/buckets/nibrsep-archive?prefix=nibrsep-archive/&region=us-east-1&bucketType=general&tab=objects))
2. Upload file > Upload `manifest.csv`

### 3. Restore the files listed in the manifest

1. Go to AWS > S3 > Batch Operations ([link](https://us-east-1.console.aws.amazon.com/s3/jobs?region=us-east-1))
2. Create job
3. Manifest > CSV: select the S3 filepath to the manifest you uploaded, e.g. `s3://nibrs-archive/nibrs-archive/manifest.csv`
4. Next
5. Operation > Restore: Select number of days and retrieval tier, e.g. 2 days, Bulk retrieval
6. Next
7. Additional Options > Completion Report, e.g. `s3://nibrs-archive/nibrs-archive/`; can be useful for debugging
8. Additional Options > Permissions: `nibrs-archive-s3-batch-restore` IAM role
9. Next
10. Create Job

### 4. Run the S3 Batch job

Run the job you've just created. It may prompt for confirmation.

### 5. Wait for the files to be restored

The batch job only requests for the files to be restored. Depending on the retrieval tier, the files may take a day or two to be restored.

**NOTE:** This process will generate a success/failure percentage and be marked as complete in a short amount of time. Neither the complete status, nor the status of success/failures appear to reflect actual status of restoration. Instead you must manually check on items and verify the restoration banner says `Restoration complete`.

### 6. Run the DataSync task to copy the files to EFS

Once the restoration time has elapsed, go to AWS DataSync and run a task to copy from S3 to EFS.

### Using DataSync to move from S3 restored state to EFS

1. Go to DataSync service in AWS UI
1. Ensure you are in the region with the EFS you want to archive data from.
1. Go to `Tasks` & click `Create task`
1. Configure source location
    * Check `Choose an existing location` to see if the archival bucket `nibrsep-archive` with the designated archive path is already configured as a location for archival desination.
    * If not then use `Create a new location`
        * Select location type as `Amazon S3`
        * Select region as `us-east-1`
        * Use the `Browse S3` button to find and find `nibrsep-archive` and then select the folder that you want to restore.
        * IAM role just use the default
        * Tag the resource with the project-number
1. Configure destination location
    * Check `Choose an existing location` to see if the EFS with the designated restore path is already configured as a location for archival source.
    * If not then use `Create a new location`
        * Select location type as `Amazon EFS file system`
        * Select the EFS from the filesystem list
        * Mount path -> set to the path you want to restore in the EFS
            * **NOTE:** If you deleted the directory you are trying to restore to, then you will need to manually recreate the directory in the EFS by ssh'ing into the jumpbox and creating it manually.
        * Select any `publicSubnet` as the subnet
        * For security group select `...nibrsFoundation-...-jumpboxSecurityGroup...`
        * Tag the resource with the project-number
1. Configure settings
    * Task mode use `Basic`
    * Give the task a name
    * Source data options
        * Most likely need to select `Everything` since in the configure source location, you should have specified the path you want to restore already.
    * Transfer options
        * Transfer mode `Transfer all data`
        * Verification `Verify only transferred data`
        * Bandwidth limit -> `Use available`
    * Tag the resource with the project-number
    * Don't worry about `Schedule` or `Task Report`
    * Logging
        * Log Level -> `Basic such as transfer errors`
        * CloudWatch log group -> `/aws/datasync`
1. Review -> Just review and create task
1. Manually trigger the task
    * Select the task from the task list
    * In the top-right select `Start` and `Start with defaults`
