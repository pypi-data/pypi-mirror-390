#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as dotenv from "dotenv";
import * as fs from "fs";
import * as path from "path";
import { Jumpbox } from '../lib/JumpboxStack';
import { NibrsepFoundationStack } from '../lib/nibrsep-foundation-stack';
import { getMachineImageEbsDevice } from '../lib/aws-resources/ec2-machine-image';
import { PrefectEcsWorkerStack } from '../lib/PrefectEcsWorkerStack/PrefectEcsWorkerStack';
import { PrefectWebServerStack } from '../lib/PrefectWebServerStack/PrefectWebServerStack';
import { AuthProxyStack } from '../lib/AuthProxyStack/AuthProxyStack';
import { getDevIpAllowlist } from '../lib/aws-resources/dev-allowlist';

const app = new cdk.App();

// Load environment variables
const __dirname = path.resolve()
const stackSuffix = app.node.tryGetContext("stackSuffix")
if (!stackSuffix) {
  throw new Error("Context parameter 'stackSuffix' is required. Pass it with '-c stackSuffix=yourSuffix'.");
}
const envBaseFilePath = path.join(__dirname, "envs/.env.base");
if (!fs.existsSync(envBaseFilePath)) {
  throw new Error(`Stack Environment file ${envBaseFilePath} does not exist.`);
}

const envSuffixFilePath = path.join(__dirname, `envs/.env.${stackSuffix}`);
if (!fs.existsSync(envSuffixFilePath)) {
  throw new Error(`Stack Environment file ${envSuffixFilePath} does not exist.`);
}

dotenv.config({ path: [envSuffixFilePath, envBaseFilePath] })
console.log(`Loaded environment variables from ${envBaseFilePath} and ${envSuffixFilePath}`);

let RSRC_SUFFIX = process.env.RSRC_SUFFIX ? `-${process.env.RSRC_SUFFIX}` : ''
console.log(`Using stack suffix: ${RSRC_SUFFIX}`)


// Environment variables
const PROJECT_NUMBER = process.env['PROJECT_NUMBER']
const { AWS_ACCOUNT_ID, AWS_DEFAULT_REGION, EXTERNALS_BUCKET_NAME, ARTIFACTS_BUCKET_NAME } = process.env
if (!AWS_ACCOUNT_ID) throw new Error("AWS_ACCOUNT_ID is required")
if (!AWS_DEFAULT_REGION) throw new Error("AWS_DEFAULT_REGION is required")
const awsEnv = { account: AWS_ACCOUNT_ID, region: AWS_DEFAULT_REGION }
// set AWS_REGION for the AWS SDK
process.env['AWS_REGION'] = AWS_DEFAULT_REGION

if (!EXTERNALS_BUCKET_NAME) throw new Error("EXTERNALS_BUCKET_NAME is required")
if (!ARTIFACTS_BUCKET_NAME) throw new Error("ARTIFACTS_BUCKET_NAME is required")

const devIpAllowlist = await getDevIpAllowlist()
console.log(`Dev IP allowlist: ${devIpAllowlist}`)

// VPC, EFS, IAM, ECR, ECS
const foundationStackType = "Foundation"
const foundationStackName = `${process.env['STACK_NAME']}${foundationStackType}${RSRC_SUFFIX}`
const foundationStack = new NibrsepFoundationStack(app, foundationStackType, {
  stackName: foundationStackName,
  env: awsEnv,
  devIpAllowlist,
})

// FYI: this is passed to a rootVolume object which isn't currently used
// Fetch the machine image description so we can configure the size of its EBS root volume
const machineImageSSMParamName = process.env['MACHINE_IMAGE_SSM_PARAM_NAME']
if (!machineImageSSMParamName) throw new Error("MACHINE_IMAGE_SSM_PARAM_NAME is required")
const machineImageEbsDevice = await getMachineImageEbsDevice(machineImageSSMParamName)
if (!machineImageEbsDevice) throw new Error("Failed to get machine image EBS device name")

// Jumpbox: An EC2 instance providing two services:
// 1) SSH access to view EFS
// 2) Web access to view the Prefect UI
const jumpboxStackType = "Jumpbox"
const jumpboxStackName = `${process.env['STACK_NAME']}${jumpboxStackType}${RSRC_SUFFIX}`
const jumpboxStack = new Jumpbox(app, jumpboxStackType, {
  stackName: jumpboxStackName,
  env: awsEnv,
  foundation: foundationStack,
  machineImageSSMParamName,
  machineImageEbsDevice,
});

// Load-balanced ECS Service for Prefect Web Server
const prefectWebServerStackType = "PrefectWebServer"
const prefectWebServerStackName = `${process.env['STACK_NAME']}${prefectWebServerStackType}${RSRC_SUFFIX}`
const prefectWebServerStack = new PrefectWebServerStack(app, prefectWebServerStackType, {
  stackName: prefectWebServerStackName,
  env: awsEnv,
  foundation: foundationStack,
  devIpAllowlist,
});

// ECS Service for Prefect-ECS Worker
const prefectEcsWorkerStackType = "PrefectEcsWorker"
const prefectEcsWorkerStackName = `${process.env['STACK_NAME']}${prefectEcsWorkerStackType}${RSRC_SUFFIX}`
const prefectEcsWorkerStack = new PrefectEcsWorkerStack(app, prefectEcsWorkerStackType, {
  stackName: prefectEcsWorkerStackName,
  env: awsEnv,
  foundation: foundationStack,
});

// ECS Service for Auth Proxy
const authProxyStackType = "AuthProxy"
const authProxyStackName = `${process.env['STACK_NAME']}${authProxyStackType}${RSRC_SUFFIX}`
const authProxyStack = new AuthProxyStack(app, authProxyStackType, {
  stackName: authProxyStackName,
  env: awsEnv,
  foundation: foundationStack,
});

if (PROJECT_NUMBER) {
  cdk.Tags.of(foundationStack).add('project-number', PROJECT_NUMBER)
  cdk.Tags.of(jumpboxStack).add('project-number', PROJECT_NUMBER)
  cdk.Tags.of(prefectWebServerStack).add('project-number', PROJECT_NUMBER)
  cdk.Tags.of(prefectEcsWorkerStack).add('project-number', PROJECT_NUMBER)
  cdk.Tags.of(authProxyStack).add('project-number', PROJECT_NUMBER)
}
