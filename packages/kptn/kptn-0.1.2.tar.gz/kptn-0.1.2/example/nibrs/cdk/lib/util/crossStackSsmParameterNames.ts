// 
// This file contains the names of the SSM parameters that are used to pass values between stacks.
// 
export function getSsmParameterNames(stack_name?: string, suffix?: string) {
  if (stack_name === undefined || suffix === undefined) {
    throw new Error("Environment 'STACK_NAME' and 'RSRC_SUFFIX' are required.")
  }
  const uniqueStackName = stack_name + '-' + suffix
  return {
    "EC2_PUBLIC_IP": `/${uniqueStackName}/ec2/publicIp`,
    "EC2_PRIVATE_IP": `/${uniqueStackName}/ec2/privateIp`,
    "PREFECT_SERVER_SG_ID": `/${uniqueStackName}/ec2/prefectWebServerSecurityGroupId`,
    "JUMPBOX_SG_ID": `/${uniqueStackName}/ec2/jumpboxSecurityGroupId`,
    "ALB_DNS_NAME": `/${uniqueStackName}/ec2/albDnsName`,
    "ALB_SG_ID": `/${uniqueStackName}/ec2/albSecurityGroupId`,
  }
}
