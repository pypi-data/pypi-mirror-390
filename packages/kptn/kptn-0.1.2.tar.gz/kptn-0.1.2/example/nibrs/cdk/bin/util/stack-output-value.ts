import { CloudFormationClient, DescribeStacksCommand, ListStacksCommand, Stack } from "@aws-sdk/client-cloudformation";

// Get the output value of a CloudFormation stack
export async function getStackOutputValue(region:string, stackName: string, outputKey: string) {
  const cfnClient = new CloudFormationClient({ region });
  const describeStacksCommand = new DescribeStacksCommand({ StackName: stackName });
  let stack: Stack | undefined;
  try {
    stack = await cfnClient.send(describeStacksCommand).then((data) => {
      return data.Stacks?.[0];
    });
  } catch (err: unknown) {
    // If the stack doesn't exist, throw a more helpful error message
    const error = err as Error;
    if (error.name === "ValidationError") {
      if (error.message.includes("does not exist")) {
        const listStacksCommand = new ListStacksCommand({});
        const stacks = await cfnClient.send(listStacksCommand).then((data) => {
          return data.StackSummaries;
        });
        if (!stacks) {
          throw new Error(`No stacks found in region ${region}`);
        } else {
          console.log(`Found stacks: ${stacks.map((stack) => stack.StackName).join(", ")}`);
        }
        throw new Error(`Stack ${stackName} not found. Verify it exists in region ${region} and that your AWS environment variables are configured correctly.`);
      }
    } else {
      throw error;
    }
  }
  stack = stack!;
  const output = stack.Outputs?.find((output) => {
    return output.OutputKey === outputKey;
  });
  if (!output) {
    throw new Error(`Output ${outputKey} not found in stack ${stackName}`);
  }
  console.log(`Found ${outputKey}=${output.OutputValue} in stack ${stackName}`)
  return output.OutputValue;
}