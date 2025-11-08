import * as cdk from 'aws-cdk-lib';
import * as s3 from "aws-cdk-lib/aws-s3";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecr from "aws-cdk-lib/aws-ecr";
import * as efs from "aws-cdk-lib/aws-efs";
import * as iam from "aws-cdk-lib/aws-iam";
import * as logs from "aws-cdk-lib/aws-logs";
import * as rds from "aws-cdk-lib/aws-rds";
import * as ssm from "aws-cdk-lib/aws-ssm";
import { getOrCreateVpc } from './aws-resources/vpc';
import { getOrCreateS3Bucket } from './aws-resources/s3';
import { getOrCreateEfs } from './aws-resources/efs';
import { getSuffix } from './util/rsrc-suffix';
import { getSsmParameterNames } from './util/crossStackSsmParameterNames';

const DEV_PORTS = { "ssh": 22, "nginx": 80 }

type StackProps = {
  devIpAllowlist: string,
} & cdk.StackProps

export class NibrsepFoundationStack extends cdk.Stack {
  public readonly vpc: ec2.IVpc;
  public readonly ecsCluster: ecs.ICluster;
  public readonly prefectDb: rds.DatabaseCluster;
  public readonly prefectDbProxy: rds.DatabaseProxy;
  public readonly nibrsEfs: efs.IFileSystem;
  public readonly ec2Role: iam.IRole;
  public readonly iamUser: iam.IUser;
  public readonly logGroup: logs.ILogGroup;
  public readonly flowRunnerRepo: ecr.IRepository;
  public readonly prefectWebServerRepo: ecr.IRepository;
  public readonly authProxyRepo: ecr.IRepository;
  public readonly bucketExternals: s3.IBucket;
  public readonly bucketArtifacts: s3.IBucket;

  constructor(scope: cdk.App, id: string, props: StackProps) {
    super(scope, id, props);

    const stack = cdk.Stack.of(this)
    let vpc = getOrCreateVpc(this, stack.stackName, process.env.VPC_ID)

    let stackSuffix = getSuffix(process.env.RSRC_SUFFIX)
    let ssmIPS = getSsmParameterNames(process.env.STACK_NAME, process.env.RSRC_SUFFIX)

    // Amazon S3 gateway endpoint
    const s3Endpoint = vpc.addGatewayEndpoint('S3Endpoint', {
      service: ec2.GatewayVpcEndpointAwsService.S3,
      subnets: [{ subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS }],
    });
    vpc.addInterfaceEndpoint('EcrDockerEndpoint', {
      service: ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
    });
    vpc.addInterfaceEndpoint('EcrApiEndpoint', {
      service: ec2.InterfaceVpcEndpointAwsService.ECR,
    });

    // EFS for parallel task shared workspace
    const nibrsEfs = getOrCreateEfs(this, vpc, process.env.NIBRS_EFS_ID!)

    // Create s3 buckets
    const bucketExternals = getOrCreateS3Bucket(this, "s3ExternalBucket", process.env.EXTERNALS_BUCKET_NAME!, stackSuffix)
    const bucketArtifacts = getOrCreateS3Bucket(this, "s3ArtifactBucket", process.env.ARTIFACTS_BUCKET_NAME!, stackSuffix)

    // Use the same logging setup for all tasks -- log with the AWS driver, which
    // propagates logs to CloudWatch
    const ecs_log_group = new logs.LogGroup(this, "ECSLogGroup", {
      retention: logs.RetentionDays.SIX_MONTHS,
    })

    const createEcrRepo = (name: string, cdkId: string) => {
      const repo = new ecr.Repository(this, cdkId, {
        repositoryName: name,
        removalPolicy: cdk.RemovalPolicy.DESTROY,
        emptyOnDelete: true,
      })
      repo.addLifecycleRule({ maxImageCount: 30 })
      return repo
    }

    const flowRunnerRepo = createEcrRepo(`prefect-flow-runner${stackSuffix}`, "FlowRunnerRepo")
    const prefectWebServerRepo = createEcrRepo(`prefect-web-server${stackSuffix}`, "PrefectWebServerRepo")
    const authProxyRepo = createEcrRepo(`auth-proxy${stackSuffix}`, "AuthProxyRepo")

    const prefectDb = new rds.DatabaseCluster(this, "PrefectRDS", {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_13_13,
      }),
      serverlessV2MinCapacity: 1,
      serverlessV2MaxCapacity: 16,
      writer: rds.ClusterInstance.serverlessV2('writer'),
      credentials: { username: "prefect" },
      defaultDatabaseName: "prefect",
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
    })
    // FYI: RDS Proxy doesn't work with Prefect 2
    this.prefectDbProxy = prefectDb.addProxy('PrefectRdsProxy', {
      secrets: [prefectDb.secret!],
      vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
      },
      debugLogging: true,
    })

    const eip = new ec2.CfnEIP(this, "EIP", {
      domain: "vpc",
    })
    cdk.Tags.of(eip).add("Name", `${stack.stackName}-EIP`)
    new ssm.StringParameter(this, "EIPParameter", {
      parameterName: ssmIPS["EC2_PUBLIC_IP"],
      stringValue: eip.ref,
    })
    const ec2instanceType = new ec2.InstanceType(process.env['JUMPBOX_INSTANCE_TYPE']!)
    const vpcSubnetType = process.env['PUBLIC_IP'] === 'true' ? ec2.SubnetType.PUBLIC : ec2.SubnetType.PRIVATE_ISOLATED
    // Describe cluster for ECS tasks with Fargate and EC2 capacity providers
    const ecsClusterName = `nibrsep${stackSuffix}`
    const ecsCluster = new ecs.Cluster(this, "ECSCluster", {
      vpc,
      clusterName: ecsClusterName,
      enableFargateCapacityProviders: true,
      containerInsights: true,
    })
    ecsCluster.connections.allowToDefaultPort(prefectDb)
    ecsCluster.connections.allowTo(this.prefectDbProxy, ec2.Port.tcp(5432))
    ecsCluster.addCapacity("DefaultAutoScalingGroup", {
      instanceType: ec2instanceType,
      vpcSubnets: { subnetType: vpcSubnetType },
      minCapacity: 0
    })

    const jumpboxSecurityGroup = new ec2.SecurityGroup(this, "jumpboxSecurityGroup", {
      vpc,
      allowAllOutbound: true
    })
    new ssm.StringParameter(this, "JumpboxSecurityGroupId", {
      parameterName: ssmIPS["JUMPBOX_SG_ID"],
      stringValue: jumpboxSecurityGroup.securityGroupId,
    })
    jumpboxSecurityGroup.connections.allowFrom(nibrsEfs, ec2.Port.tcp(efs.FileSystem.DEFAULT_PORT))
    jumpboxSecurityGroup.connections.allowTo(nibrsEfs, ec2.Port.tcp(efs.FileSystem.DEFAULT_PORT))
    jumpboxSecurityGroup.connections.allowInternally(ec2.Port.allTraffic())
    jumpboxSecurityGroup.addIngressRule(
      jumpboxSecurityGroup, ec2.Port.tcpRange(0, 65535), "Security Group"
    )

    if (process.env.PUBLIC_IP === 'true') {
      // Open ports for the name-IP allowlist
      const allowlist = props.devIpAllowlist ? props.devIpAllowlist.split(",") : []
      if (allowlist.length > 0) {
        console.log("Allowing IPs for users:", allowlist)
        for (const nameIpPair of allowlist) {
          const [name, ip] = nameIpPair.split(":")
          for (const port of Object.values(DEV_PORTS)) {
            jumpboxSecurityGroup.addIngressRule(
              ec2.Peer.ipv4(`${ip}/32`), ec2.Port.tcp(port), name
            )
          }
        }
      }
    }

    const prefectWebServerSecurityGroup = new ec2.SecurityGroup(this, "PrefectWebServerSecurityGroup", {
      vpc,
      allowAllOutbound: true,
    })
    new ssm.StringParameter(this, "PrefectWebServerSecurityGroupId", {
      parameterName: ssmIPS["PREFECT_SERVER_SG_ID"],
      stringValue: prefectWebServerSecurityGroup.securityGroupId,
    })
    // Allow any inbound to prefectWebServerSecurityGroup
    prefectWebServerSecurityGroup.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(80), "Allow HTTP traffic")
    prefectDb.connections.allowFrom(prefectWebServerSecurityGroup, ec2.Port.tcp(5432), "From Prefect Web Server")
    prefectDb.connections.allowFrom(jumpboxSecurityGroup, ec2.Port.tcp(5432), "From Jumpbox")
    this.prefectDbProxy.connections.allowFrom(prefectWebServerSecurityGroup, ec2.Port.tcp(5432), "Allow access to RDS Proxy")
    this.prefectDbProxy.connections.allowFrom(this.prefectDbProxy, ec2.Port.tcp(5432), "Self-referencing Rule.")
    this.prefectDbProxy.connections.allowFrom(jumpboxSecurityGroup, ec2.Port.tcp(5432), "From Jumpbox")


    this.vpc = vpc
    this.ecsCluster = ecsCluster
    this.prefectDb = prefectDb
    this.nibrsEfs = nibrsEfs
    this.logGroup = ecs_log_group
    this.flowRunnerRepo = flowRunnerRepo
    this.prefectWebServerRepo = prefectWebServerRepo
    this.authProxyRepo = authProxyRepo
    this.bucketExternals = bucketExternals
    this.bucketArtifacts = bucketArtifacts

    new cdk.CfnOutput(this, "flowRunnerRepo", {
      value: flowRunnerRepo.repositoryUri,
      description: "flowRunnerRepo",
    })
    new cdk.CfnOutput(this, "prefectWebServerRepo", {
      value: prefectWebServerRepo.repositoryUri,
      description: "prefectWebServerRepo",
    })
    new cdk.CfnOutput(this, "authProxyRepo", {
      value: authProxyRepo.repositoryUri,
      description: "authProxyRepo",
    })
    new cdk.CfnOutput(this, "ec2publicIp", {
      value: eip.ref,
      description: "AWS_EC2_EIP",
    })
  }
}
