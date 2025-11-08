import * as path from 'path';
import * as cdk from 'aws-cdk-lib';
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as iam from "aws-cdk-lib/aws-iam";
import * as ssm from "aws-cdk-lib/aws-ssm";
import { type NibrsepFoundationStack } from './nibrsep-foundation-stack';
import { type BlockDeviceMapping } from '@aws-sdk/client-ec2';
import { __dirname } from './util/node';
import { getSuffix } from './util/rsrc-suffix';
import { getSsmParameterNames } from './util/crossStackSsmParameterNames';
import fs from 'fs';

const EFS_EC2_MOUNT = "/home/ec2-user/efs/"

type StackProps = {
  foundation: NibrsepFoundationStack,
  machineImageSSMParamName: string,
  machineImageEbsDevice: BlockDeviceMapping,
} & cdk.StackProps

export class Jumpbox extends cdk.Stack {
  public readonly securityGroup: ec2.ISecurityGroup;
  public readonly ecsCluster: ecs.ICluster;
  public readonly ec2Server: ec2.Instance;

  constructor(scope: cdk.App, id: string, props: StackProps) {
    super(scope, id, props);

    const { nibrsEfs, vpc } = props.foundation
    const { KEY_PAIR_NAME, PUBLIC_IP } = process.env

    let ssmParams = getSsmParameterNames(process.env.STACK_NAME, process.env.RSRC_SUFFIX)

    const jumpboxSecurityGroupId = ssm.StringParameter.valueForStringParameter(
      this,
      ssmParams["JUMPBOX_SG_ID"]
    )
    const jumpboxSecurityGroup = ec2.SecurityGroup.fromSecurityGroupId(
      this,
      "jumpboxSecurityGroup",
      jumpboxSecurityGroupId
    )

    const cwAgentConfig = fs.readFileSync(
      path.resolve(__dirname(import.meta), "aws-resources/amazon-cloudwatch-agent.json"), "utf8")
    
    // Upload amazon-cloudwatch-agent.json to SSM if it doesn't exist
    if (!ssm.StringParameter.fromSecureStringParameterAttributes(this, "CWAgentConfig", {
      parameterName: "/amazon-cloudwatch-agent.json",
    })) {
      new ssm.StringParameter(this, "CWAgentConfig", {
        parameterName: "/amazon-cloudwatch-agent.json",
        stringValue: cwAgentConfig,
      })
    }

    // Override the default root volume size of 8GB with a 512GB volume
    const rootVolume: ec2.BlockDevice = {
      deviceName: props.machineImageEbsDevice.DeviceName!,
      volume: ec2.BlockDeviceVolume.ebsFromSnapshot(props.machineImageEbsDevice.Ebs!.SnapshotId!, {
        volumeSize: 512,
        volumeType: ec2.EbsDeviceVolumeType.GP2,
        deleteOnTermination: true,
      }),
    }

    const jumpboxRole = new iam.Role(this, "ec2JumpboxRole", {
      assumedBy: new iam.ServicePrincipal("ec2.amazonaws.com"),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName("service-role/AmazonEC2ContainerServiceforEC2Role"),
        iam.ManagedPolicy.fromAwsManagedPolicyName("CloudWatchAgentServerPolicy"),
        iam.ManagedPolicy.fromAwsManagedPolicyName("AmazonSSMManagedInstanceCore"),
      ],
    });

    const stack = cdk.Stack.of(this)
    const ec2instanceType = new ec2.InstanceType(process.env['JUMPBOX_INSTANCE_TYPE']!)
    const ec2VpcSubnetType = PUBLIC_IP === 'true' ? ec2.SubnetType.PUBLIC : ec2.SubnetType.PRIVATE_ISOLATED
    const ec2Server = new ec2.Instance(this, "EC2Instance", {
      vpc,
      securityGroup: jumpboxSecurityGroup,
      instanceType: ec2instanceType,
      instanceName: `${stack.stackName}-EC2`,
      vpcSubnets: { subnetType: ec2VpcSubnetType },
      allowAllOutbound: true,
      machineImage: ec2.MachineImage.fromSsmParameter(
        "/aws/service/ecs/optimized-ami/amazon-linux-2023/recommended/image_id",
      ),
      role: jumpboxRole,
      userDataCausesReplacement: true
    })
    // Allow both the ec2 server to access the EFS
    ec2Server.connections.allowToDefaultPort(nibrsEfs)

    if (PUBLIC_IP === 'true') {
      // Add SSH Key Pair
      if (KEY_PAIR_NAME) {
        ec2Server.instance.addPropertyOverride(
          "KeyName", KEY_PAIR_NAME
        )
      }
    }

    const stackSuffix = getSuffix(process.env.RSRC_SUFFIX)
    const ecsClusterName = `nibrsep${stackSuffix}`
    const ecsConfigUserData = "#!/bin/bash \n" +
      "cat <<'EOF' >> /etc/ecs/ecs.config \n" +
      `ECS_CLUSTER=${ecsClusterName} \n` +
      "ECS_ENABLE_CONTAINER_METADATA=true \n" +
      "EOF"
    ec2Server.userData.addCommands(ecsConfigUserData)
    ec2Server.userData.addCommands(
      "yum check-update -y",
      "yum upgrade -y",
      "yum install -y collectd",
      "yum install -y amazon-cloudwatch-agent",
      "yum install -y amazon-efs-utils",
      "yum install -y nfs-utils",
      "yum install -y rsync",
      "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c ssm:amazon-cloudwatch-agent.json -s",
      "file_system_id_1=" + nibrsEfs.fileSystemId,
      "efs_mount_point_1=" + EFS_EC2_MOUNT,
      "mkdir -p \"${efs_mount_point_1}\"",
      "test -f \"/sbin/mount.efs\" && echo \"${file_system_id_1}:/ ${efs_mount_point_1} efs defaults,_netdev\" >> /etc/fstab || " +
      "echo \"${file_system_id_1}.efs." + stack.region + ".amazonaws.com:/ ${efs_mount_point_1} nfs4 nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport,_netdev 0 0\" >> /etc/fstab",
      "mount -a -t efs,nfs4 defaults"
    )
    ec2Server.userData.addCommands(
      "yum check-update -y",
      "yum upgrade -y",
      "yum install -y python3-pip",
      "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a start"
    )
    
    const ec2publicIp = ssm.StringParameter.valueForStringParameter(
      this,
      ssmParams["EC2_PUBLIC_IP"]
    )
    new ec2.CfnEIPAssociation(this, "EC2EIPAssociation", {
      eip: ec2publicIp,
      instanceId: ec2Server.instanceId,
    })

    new ssm.StringParameter(this, "EC2PrivateIp", {
      parameterName: ssmParams["EC2_PRIVATE_IP"],
      stringValue: ec2Server.instancePrivateIp,
    })
  }
}
