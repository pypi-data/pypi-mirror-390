
import { SSMClient, GetParameterCommand } from "@aws-sdk/client-ssm"; 

/**
 * Fetch the list of IP addresses that are allowed to connect to the development environment.
 */
export async function getDevIpAllowlist() {
  const ssmClient = new SSMClient({ region: process.env.DB_SECURITY_GROUP_REGION! })
  const command = new GetParameterCommand({
    Name: "/nibrsep/dev-ip-allowlist",
  })
  const response = await ssmClient.send(command)
  return response.Parameter?.Value || ""
}