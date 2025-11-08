import 'dotenv/config' // Load environment variables from .env file
import { addIngressRuleToSecurityGroup } from "./util/db-security-group";
import { getStackOutputValue } from './util/stack-output-value';

// This script assumes these env vars are set:
// STACK_NAME
// DB_SECURITY_GROUP_ID
// DB_SECURITY_GROUP_REGION


// Get the public subnet IP address for the newly deployed stack
const publicSubnetEip = await getStackOutputValue(
  process.env.AWS_DEFAULT_REGION!,
  process.env.STACK_NAME!,
  "publicSubnetEip"
);

// Add an ingress rule to the DB security group to allow ingress from that IP address
addIngressRuleToSecurityGroup(
  process.env.DB_SECURITY_GROUP_REGION!,
  publicSubnetEip!,
  process.env.DB_SECURITY_GROUP_ID!
)
