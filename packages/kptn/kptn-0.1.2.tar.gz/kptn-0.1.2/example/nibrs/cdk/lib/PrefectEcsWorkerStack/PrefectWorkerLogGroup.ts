import { Construct } from "constructs"
import { LogGroup, RetentionDays } from "aws-cdk-lib/aws-logs"


export function PrefectWorkerLogGroup(scope: Construct) {
  const prefectWorkerLogGroup = new LogGroup(scope, "PrefectWorkerLogGroup", {
    retention: RetentionDays.ONE_MONTH,
  })

  return prefectWorkerLogGroup
}