
import { SSMClient, GetParameterCommand } from "@aws-sdk/client-ssm"; 
import { EC2Client, DescribeImagesCommand } from "@aws-sdk/client-ec2";

/**
 * Retrieves the device name of the EBS block device mapping for a given machine image.
 * 
 * @param machineImageSSMParamName - The name of the SSM parameter that stores the machine image ID.
 * @returns The device name of the EBS block device mapping, or undefined if not found.
 */
export async function getMachineImageEbsDevice(machineImageSSMParamName: string) {
  
  const ssmClient = new SSMClient({})
  const command = new GetParameterCommand({
    Name: machineImageSSMParamName,
  })
  const amiId = await ssmClient.send(command).then((data) => {
    return data.Parameter?.Value
  })
  const ec2Client = new EC2Client({})
  const describeImagesCommand = new DescribeImagesCommand({
    ImageIds: [amiId!],
  })
  const ami = await ec2Client.send(describeImagesCommand).then((data) => {
    return data.Images?.[0]
  })
  // Find block device mapping that has key "Ebs" and return the device
  const ebsDevice = ami?.BlockDeviceMappings?.find((bdm) => {
    return bdm.hasOwnProperty("Ebs")
  })
  return ebsDevice
}