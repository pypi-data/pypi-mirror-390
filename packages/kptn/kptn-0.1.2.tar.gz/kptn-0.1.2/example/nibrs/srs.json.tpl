{
  "Comment": "kptn generated state machine for srs",
  "StartAt": "Lane0Parallel",
  "States": {
    "Lane0Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "external_config_Decide",
          "States": {
            "external_config_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "external_config",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "external_config_Choice"
            },
            "external_config_Choice": {
              "Type": "Choice",
              "Default": "external_config_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "external_config_RunEcs"
                }
              ]
            },
            "external_config_Skip": {
              "Type": "Pass",
              "End": true
            },
            "external_config_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "external_config"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "external_config"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "states_in_database_Decide",
          "States": {
            "states_in_database_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "states_in_database",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "states_in_database_Choice"
            },
            "states_in_database_Choice": {
              "Type": "Choice",
              "Default": "states_in_database_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "states_in_database_RunEcs"
                }
              ]
            },
            "states_in_database_Skip": {
              "Type": "Pass",
              "End": true
            },
            "states_in_database_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "states_in_database"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "states_in_database"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "year_list_Decide",
          "States": {
            "year_list_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "year_list",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "year_list_Choice"
            },
            "year_list_Choice": {
              "Type": "Choice",
              "Default": "year_list_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "year_list_RunEcs"
                }
              ]
            },
            "year_list_Skip": {
              "Type": "Pass",
              "End": true
            },
            "year_list_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "year_list"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "year_list"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_tables_Decide",
          "States": {
            "srs_tables_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_tables",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_tables_Choice"
            },
            "srs_tables_Choice": {
              "Type": "Choice",
              "Default": "srs_tables_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_tables_RunEcs"
                }
              ]
            },
            "srs_tables_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_tables_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_tables"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_tables"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_estimate_combos_Decide",
          "States": {
            "srs_estimate_combos_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_estimate_combos",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_estimate_combos_Choice"
            },
            "srs_estimate_combos_Choice": {
              "Type": "Choice",
              "Default": "srs_estimate_combos_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_estimate_combos_RunEcs"
                }
              ]
            },
            "srs_estimate_combos_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_estimate_combos_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_estimate_combos"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_estimate_combos"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_copula_imputation_step1_tables_Decide",
          "States": {
            "srs_copula_imputation_step1_tables_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_copula_imputation_step1_tables",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_copula_imputation_step1_tables_Choice"
            },
            "srs_copula_imputation_step1_tables_Choice": {
              "Type": "Choice",
              "Default": "srs_copula_imputation_step1_tables_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_copula_imputation_step1_tables_RunEcs"
                }
              ]
            },
            "srs_copula_imputation_step1_tables_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_copula_imputation_step1_tables_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_copula_imputation_step1_tables"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_copula_imputation_step1_tables"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane1Parallel"
    },
    "Lane1Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "external_dir_Decide",
          "States": {
            "external_dir_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "external_dir",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "external_dir_Choice"
            },
            "external_dir_Choice": {
              "Type": "Choice",
              "Default": "external_dir_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "external_dir_RunEcs"
                }
              ]
            },
            "external_dir_Skip": {
              "Type": "Pass",
              "End": true
            },
            "external_dir_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "external_dir"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "external_dir"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_bystate_converted_Decide",
          "States": {
            "srs_bystate_converted_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_bystate_converted",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_bystate_converted_Choice"
            },
            "srs_bystate_converted_Choice": {
              "Type": "Choice",
              "Default": "srs_bystate_converted_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Variable": "$.last_decision.Payload.execution_mode",
                      "StringEquals": "batch_array"
                    },
                    {
                      "Variable": "$.last_decision.Payload.array_size",
                      "NumericGreaterThan": 0
                    }
                  ],
                  "Next": "srs_bystate_converted_RunBatch"
                }
              ]
            },
            "srs_bystate_converted_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_bystate_converted_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('srs-srs_bystate_converted-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "srs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "srs_bystate_converted"
                    },
                    {
                      "Name": "DYNAMODB_TABLE_NAME",
                      "Value": "${dynamodb_table_name}"
                    },
                    {
                      "Name": "ARRAY_SIZE",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
                    },
                    {
                      "Name": "KAPTEN_DECISION_REASON",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                    }
                  ]
                },
                "Tags": {
                  "KaptenPipeline": "srs",
                  "KaptenTask": "srs_bystate_converted"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane2Parallel"
    },
    "Lane2Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "universe_created_Decide",
          "States": {
            "universe_created_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "universe_created",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "universe_created_Choice"
            },
            "universe_created_Choice": {
              "Type": "Choice",
              "Default": "universe_created_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Variable": "$.last_decision.Payload.execution_mode",
                      "StringEquals": "batch_array"
                    },
                    {
                      "Variable": "$.last_decision.Payload.array_size",
                      "NumericGreaterThan": 0
                    }
                  ],
                  "Next": "universe_created_RunBatch"
                }
              ]
            },
            "universe_created_Skip": {
              "Type": "Pass",
              "End": true
            },
            "universe_created_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('srs-universe_created-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "srs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "universe_created"
                    },
                    {
                      "Name": "DYNAMODB_TABLE_NAME",
                      "Value": "${dynamodb_table_name}"
                    },
                    {
                      "Name": "ARRAY_SIZE",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
                    },
                    {
                      "Name": "KAPTEN_DECISION_REASON",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                    }
                  ]
                },
                "Tags": {
                  "KaptenPipeline": "srs",
                  "KaptenTask": "universe_created"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "year_queried_Decide",
          "States": {
            "year_queried_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "year_queried",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "year_queried_Choice"
            },
            "year_queried_Choice": {
              "Type": "Choice",
              "Default": "year_queried_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "year_queried_RunEcs"
                }
              ]
            },
            "year_queried_Skip": {
              "Type": "Pass",
              "End": true
            },
            "year_queried_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "year_queried"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "year_queried"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_final_permutations_list_Decide",
          "States": {
            "srs_final_permutations_list_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_final_permutations_list",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_final_permutations_list_Choice"
            },
            "srs_final_permutations_list_Choice": {
              "Type": "Choice",
              "Default": "srs_final_permutations_list_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_final_permutations_list_RunEcs"
                }
              ]
            },
            "srs_final_permutations_list_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_final_permutations_list_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_final_permutations_list"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_final_permutations_list"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_qc_converted_Decide",
          "States": {
            "srs_qc_converted_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_qc_converted",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_qc_converted_Choice"
            },
            "srs_qc_converted_Choice": {
              "Type": "Choice",
              "Default": "srs_qc_converted_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Variable": "$.last_decision.Payload.execution_mode",
                      "StringEquals": "batch_array"
                    },
                    {
                      "Variable": "$.last_decision.Payload.array_size",
                      "NumericGreaterThan": 0
                    }
                  ],
                  "Next": "srs_qc_converted_RunBatch"
                }
              ]
            },
            "srs_qc_converted_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_qc_converted_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('srs-srs_qc_converted-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "srs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "srs_qc_converted"
                    },
                    {
                      "Name": "DYNAMODB_TABLE_NAME",
                      "Value": "${dynamodb_table_name}"
                    },
                    {
                      "Name": "ARRAY_SIZE",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
                    },
                    {
                      "Name": "KAPTEN_DECISION_REASON",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                    }
                  ]
                },
                "Tags": {
                  "KaptenPipeline": "srs",
                  "KaptenTask": "srs_qc_converted"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane3Parallel"
    },
    "Lane3Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "srs_retamm_created_Decide",
          "States": {
            "srs_retamm_created_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_retamm_created",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_retamm_created_Choice"
            },
            "srs_retamm_created_Choice": {
              "Type": "Choice",
              "Default": "srs_retamm_created_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_retamm_created_RunEcs"
                }
              ]
            },
            "srs_retamm_created_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_retamm_created_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_retamm_created"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_retamm_created"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_final_estimates_Decide",
          "States": {
            "srs_final_estimates_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_final_estimates",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_final_estimates_Choice"
            },
            "srs_final_estimates_Choice": {
              "Type": "Choice",
              "Default": "srs_final_estimates_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Variable": "$.last_decision.Payload.execution_mode",
                      "StringEquals": "batch_array"
                    },
                    {
                      "Variable": "$.last_decision.Payload.array_size",
                      "NumericGreaterThan": 0
                    }
                  ],
                  "Next": "srs_final_estimates_RunBatch"
                }
              ]
            },
            "srs_final_estimates_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_final_estimates_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('srs-srs_final_estimates-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "srs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "srs_final_estimates"
                    },
                    {
                      "Name": "DYNAMODB_TABLE_NAME",
                      "Value": "${dynamodb_table_name}"
                    },
                    {
                      "Name": "ARRAY_SIZE",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
                    },
                    {
                      "Name": "KAPTEN_DECISION_REASON",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                    }
                  ]
                },
                "Tags": {
                  "KaptenPipeline": "srs",
                  "KaptenTask": "srs_final_estimates"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane4Parallel"
    },
    "Lane4Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "officers_imputed_Decide",
          "States": {
            "officers_imputed_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "officers_imputed",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "officers_imputed_Choice"
            },
            "officers_imputed_Choice": {
              "Type": "Choice",
              "Default": "officers_imputed_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "officers_imputed_RunEcs"
                }
              ]
            },
            "officers_imputed_Skip": {
              "Type": "Pass",
              "End": true
            },
            "officers_imputed_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "officers_imputed"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "officers_imputed"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_final_estimates_merged_Decide",
          "States": {
            "srs_final_estimates_merged_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_final_estimates_merged",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_final_estimates_merged_Choice"
            },
            "srs_final_estimates_merged_Choice": {
              "Type": "Choice",
              "Default": "srs_final_estimates_merged_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_final_estimates_merged_RunEcs"
                }
              ]
            },
            "srs_final_estimates_merged_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_final_estimates_merged_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_final_estimates_merged"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_final_estimates_merged"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "universe_updated_Decide"
    },
    "universe_updated_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "universe_updated",
          "execution_mode": "ecs",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "universe_updated_Choice"
    },
    "universe_updated_Choice": {
      "Type": "Choice",
      "Default": "universe_updated_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Or": [
                {
                  "Variable": "$.last_decision.Payload.execution_mode",
                  "StringEquals": "ecs"
                },
                {
                  "Not": {
                    "Variable": "$.last_decision.Payload.execution_mode",
                    "IsPresent": true
                  }
                }
              ]
            }
          ],
          "Next": "universe_updated_RunEcs"
        }
      ]
    },
    "universe_updated_Skip": {
      "Type": "Pass",
      "Next": "Lane6Parallel"
    },
    "universe_updated_RunEcs": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "Cluster": "${ecs_cluster_arn}",
        "TaskDefinition": "${ecs_task_definition_arn}",
        "LaunchType": "${launch_type}",
        "NetworkConfiguration": {
          "AwsvpcConfiguration": {
            "AssignPublicIp": "${assign_public_ip}",
            "Subnets": ${subnet_ids},
            "SecurityGroups": ${security_group_ids}
          }
        },
        "Overrides": {
          "ContainerOverrides": [
            {
              "Name": "${container_name}",
              "Environment": [
                {
                  "Name": "KAPTEN_PIPELINE",
                  "Value": "srs"
                },
                {
                  "Name": "KAPTEN_TASK",
                  "Value": "universe_updated"
                },
                {
                  "Name": "DYNAMODB_TABLE_NAME",
                  "Value": "${dynamodb_table_name}"
                },
                {
                  "Name": "KAPTEN_DECISION_REASON",
                  "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                }
              ]
            }
          ]
        },
        "EnableExecuteCommand": true,
        "Tags": [
          {
            "Key": "KaptenPipeline",
            "Value": "srs"
          },
          {
            "Key": "KaptenTask",
            "Value": "universe_updated"
          }
        ]
      },
      "ResultPath": null,
      "Next": "Lane6Parallel"
    },
    "Lane6Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "pop_totals_updated_srs_Decide",
          "States": {
            "pop_totals_updated_srs_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "pop_totals_updated_srs",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "pop_totals_updated_srs_Choice"
            },
            "pop_totals_updated_srs_Choice": {
              "Type": "Choice",
              "Default": "pop_totals_updated_srs_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "pop_totals_updated_srs_RunEcs"
                }
              ]
            },
            "pop_totals_updated_srs_Skip": {
              "Type": "Pass",
              "End": true
            },
            "pop_totals_updated_srs_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "pop_totals_updated_srs"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "pop_totals_updated_srs"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "missing_months_Decide",
          "States": {
            "missing_months_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "missing_months",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "missing_months_Choice"
            },
            "missing_months_Choice": {
              "Type": "Choice",
              "Default": "missing_months_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Variable": "$.last_decision.Payload.execution_mode",
                      "StringEquals": "batch_array"
                    },
                    {
                      "Variable": "$.last_decision.Payload.array_size",
                      "NumericGreaterThan": 0
                    }
                  ],
                  "Next": "missing_months_RunBatch"
                }
              ]
            },
            "missing_months_Skip": {
              "Type": "Pass",
              "End": true
            },
            "missing_months_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('srs-missing_months-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "srs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "missing_months"
                    },
                    {
                      "Name": "DYNAMODB_TABLE_NAME",
                      "Value": "${dynamodb_table_name}"
                    },
                    {
                      "Name": "ARRAY_SIZE",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
                    },
                    {
                      "Name": "KAPTEN_DECISION_REASON",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                    }
                  ]
                },
                "Tags": {
                  "KaptenPipeline": "srs",
                  "KaptenTask": "missing_months"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "partial_reporters_Decide"
    },
    "partial_reporters_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "partial_reporters",
          "execution_mode": "ecs",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "partial_reporters_Choice"
    },
    "partial_reporters_Choice": {
      "Type": "Choice",
      "Default": "partial_reporters_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Or": [
                {
                  "Variable": "$.last_decision.Payload.execution_mode",
                  "StringEquals": "ecs"
                },
                {
                  "Not": {
                    "Variable": "$.last_decision.Payload.execution_mode",
                    "IsPresent": true
                  }
                }
              ]
            }
          ],
          "Next": "partial_reporters_RunEcs"
        }
      ]
    },
    "partial_reporters_Skip": {
      "Type": "Pass",
      "Next": "outliers_detected_Decide"
    },
    "partial_reporters_RunEcs": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "Cluster": "${ecs_cluster_arn}",
        "TaskDefinition": "${ecs_task_definition_arn}",
        "LaunchType": "${launch_type}",
        "NetworkConfiguration": {
          "AwsvpcConfiguration": {
            "AssignPublicIp": "${assign_public_ip}",
            "Subnets": ${subnet_ids},
            "SecurityGroups": ${security_group_ids}
          }
        },
        "Overrides": {
          "ContainerOverrides": [
            {
              "Name": "${container_name}",
              "Environment": [
                {
                  "Name": "KAPTEN_PIPELINE",
                  "Value": "srs"
                },
                {
                  "Name": "KAPTEN_TASK",
                  "Value": "partial_reporters"
                },
                {
                  "Name": "DYNAMODB_TABLE_NAME",
                  "Value": "${dynamodb_table_name}"
                },
                {
                  "Name": "KAPTEN_DECISION_REASON",
                  "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                }
              ]
            }
          ]
        },
        "EnableExecuteCommand": true,
        "Tags": [
          {
            "Key": "KaptenPipeline",
            "Value": "srs"
          },
          {
            "Key": "KaptenTask",
            "Value": "partial_reporters"
          }
        ]
      },
      "ResultPath": null,
      "Next": "outliers_detected_Decide"
    },
    "outliers_detected_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "outliers_detected",
          "execution_mode": "ecs",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "outliers_detected_Choice"
    },
    "outliers_detected_Choice": {
      "Type": "Choice",
      "Default": "outliers_detected_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Or": [
                {
                  "Variable": "$.last_decision.Payload.execution_mode",
                  "StringEquals": "ecs"
                },
                {
                  "Not": {
                    "Variable": "$.last_decision.Payload.execution_mode",
                    "IsPresent": true
                  }
                }
              ]
            }
          ],
          "Next": "outliers_detected_RunEcs"
        }
      ]
    },
    "outliers_detected_Skip": {
      "Type": "Pass",
      "Next": "Lane9Parallel"
    },
    "outliers_detected_RunEcs": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "Cluster": "${ecs_cluster_arn}",
        "TaskDefinition": "${ecs_task_definition_arn}",
        "LaunchType": "${launch_type}",
        "NetworkConfiguration": {
          "AwsvpcConfiguration": {
            "AssignPublicIp": "${assign_public_ip}",
            "Subnets": ${subnet_ids},
            "SecurityGroups": ${security_group_ids}
          }
        },
        "Overrides": {
          "ContainerOverrides": [
            {
              "Name": "${container_name}",
              "Environment": [
                {
                  "Name": "KAPTEN_PIPELINE",
                  "Value": "srs"
                },
                {
                  "Name": "KAPTEN_TASK",
                  "Value": "outliers_detected"
                },
                {
                  "Name": "DYNAMODB_TABLE_NAME",
                  "Value": "${dynamodb_table_name}"
                },
                {
                  "Name": "KAPTEN_DECISION_REASON",
                  "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                }
              ]
            }
          ]
        },
        "EnableExecuteCommand": true,
        "Tags": [
          {
            "Key": "KaptenPipeline",
            "Value": "srs"
          },
          {
            "Key": "KaptenTask",
            "Value": "outliers_detected"
          }
        ]
      },
      "ResultPath": null,
      "Next": "Lane9Parallel"
    },
    "Lane9Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "srs_weights_created_Decide",
          "States": {
            "srs_weights_created_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_weights_created",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_weights_created_Choice"
            },
            "srs_weights_created_Choice": {
              "Type": "Choice",
              "Default": "srs_weights_created_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_weights_created_RunEcs"
                }
              ]
            },
            "srs_weights_created_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_weights_created_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_weights_created"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_weights_created"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "blocks_imputed_Decide",
          "States": {
            "blocks_imputed_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "blocks_imputed",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "blocks_imputed_Choice"
            },
            "blocks_imputed_Choice": {
              "Type": "Choice",
              "Default": "blocks_imputed_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "blocks_imputed_RunEcs"
                }
              ]
            },
            "blocks_imputed_Skip": {
              "Type": "Pass",
              "End": true
            },
            "blocks_imputed_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "blocks_imputed"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "blocks_imputed"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane10Parallel"
    },
    "Lane10Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "srs_weights_setup_Decide",
          "States": {
            "srs_weights_setup_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_weights_setup",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_weights_setup_Choice"
            },
            "srs_weights_setup_Choice": {
              "Type": "Choice",
              "Default": "srs_weights_setup_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_weights_setup_RunEcs"
                }
              ]
            },
            "srs_weights_setup_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_weights_setup_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_weights_setup"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_weights_setup"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_conversion_finalized_Decide",
          "States": {
            "srs_conversion_finalized_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_conversion_finalized",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_conversion_finalized_Choice"
            },
            "srs_conversion_finalized_Choice": {
              "Type": "Choice",
              "Default": "srs_conversion_finalized_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_conversion_finalized_RunEcs"
                }
              ]
            },
            "srs_conversion_finalized_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_conversion_finalized_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_conversion_finalized"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_conversion_finalized"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "srs_blocks_imputed_Decide"
    },
    "srs_blocks_imputed_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "srs_blocks_imputed",
          "execution_mode": "ecs",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "srs_blocks_imputed_Choice"
    },
    "srs_blocks_imputed_Choice": {
      "Type": "Choice",
      "Default": "srs_blocks_imputed_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Or": [
                {
                  "Variable": "$.last_decision.Payload.execution_mode",
                  "StringEquals": "ecs"
                },
                {
                  "Not": {
                    "Variable": "$.last_decision.Payload.execution_mode",
                    "IsPresent": true
                  }
                }
              ]
            }
          ],
          "Next": "srs_blocks_imputed_RunEcs"
        }
      ]
    },
    "srs_blocks_imputed_Skip": {
      "Type": "Pass",
      "Next": "Lane12Parallel"
    },
    "srs_blocks_imputed_RunEcs": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "Cluster": "${ecs_cluster_arn}",
        "TaskDefinition": "${ecs_task_definition_arn}",
        "LaunchType": "${launch_type}",
        "NetworkConfiguration": {
          "AwsvpcConfiguration": {
            "AssignPublicIp": "${assign_public_ip}",
            "Subnets": ${subnet_ids},
            "SecurityGroups": ${security_group_ids}
          }
        },
        "Overrides": {
          "ContainerOverrides": [
            {
              "Name": "${container_name}",
              "Environment": [
                {
                  "Name": "KAPTEN_PIPELINE",
                  "Value": "srs"
                },
                {
                  "Name": "KAPTEN_TASK",
                  "Value": "srs_blocks_imputed"
                },
                {
                  "Name": "DYNAMODB_TABLE_NAME",
                  "Value": "${dynamodb_table_name}"
                },
                {
                  "Name": "KAPTEN_DECISION_REASON",
                  "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                }
              ]
            }
          ]
        },
        "EnableExecuteCommand": true,
        "Tags": [
          {
            "Key": "KaptenPipeline",
            "Value": "srs"
          },
          {
            "Key": "KaptenTask",
            "Value": "srs_blocks_imputed"
          }
        ]
      },
      "ResultPath": null,
      "Next": "Lane12Parallel"
    },
    "Lane12Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "srs_cleanframe_setup_Decide",
          "States": {
            "srs_cleanframe_setup_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_cleanframe_setup",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_cleanframe_setup_Choice"
            },
            "srs_cleanframe_setup_Choice": {
              "Type": "Choice",
              "Default": "srs_cleanframe_setup_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_cleanframe_setup_RunEcs"
                }
              ]
            },
            "srs_cleanframe_setup_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_cleanframe_setup_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_cleanframe_setup"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_cleanframe_setup"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_rawframe_setup_Decide",
          "States": {
            "srs_rawframe_setup_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_rawframe_setup",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_rawframe_setup_Choice"
            },
            "srs_rawframe_setup_Choice": {
              "Type": "Choice",
              "Default": "srs_rawframe_setup_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_rawframe_setup_RunEcs"
                }
              ]
            },
            "srs_rawframe_setup_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_rawframe_setup_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_rawframe_setup"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_rawframe_setup"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "srs_indicators_estimated_tables_part1_preprocessing_Decide"
    },
    "srs_indicators_estimated_tables_part1_preprocessing_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "srs_indicators_estimated_tables_part1_preprocessing",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "srs_indicators_estimated_tables_part1_preprocessing_Choice"
    },
    "srs_indicators_estimated_tables_part1_preprocessing_Choice": {
      "Type": "Choice",
      "Default": "srs_indicators_estimated_tables_part1_preprocessing_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Variable": "$.last_decision.Payload.execution_mode",
              "StringEquals": "batch_array"
            },
            {
              "Variable": "$.last_decision.Payload.array_size",
              "NumericGreaterThan": 0
            }
          ],
          "Next": "srs_indicators_estimated_tables_part1_preprocessing_RunBatch"
        }
      ]
    },
    "srs_indicators_estimated_tables_part1_preprocessing_Skip": {
      "Type": "Pass",
      "Next": "srs_indicators_estimated_tables_part2_generate_est_Decide"
    },
    "srs_indicators_estimated_tables_part1_preprocessing_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('srs-srs_indicators_estimated_tables_part1_preprocessing-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "srs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "srs_indicators_estimated_tables_part1_preprocessing"
            },
            {
              "Name": "DYNAMODB_TABLE_NAME",
              "Value": "${dynamodb_table_name}"
            },
            {
              "Name": "ARRAY_SIZE",
              "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
            },
            {
              "Name": "KAPTEN_DECISION_REASON",
              "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
            }
          ]
        },
        "Tags": {
          "KaptenPipeline": "srs",
          "KaptenTask": "srs_indicators_estimated_tables_part1_preprocessing"
        }
      },
      "ResultPath": null,
      "Next": "srs_indicators_estimated_tables_part2_generate_est_Decide"
    },
    "srs_indicators_estimated_tables_part2_generate_est_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "srs_indicators_estimated_tables_part2_generate_est",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "srs_indicators_estimated_tables_part2_generate_est_Choice"
    },
    "srs_indicators_estimated_tables_part2_generate_est_Choice": {
      "Type": "Choice",
      "Default": "srs_indicators_estimated_tables_part2_generate_est_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Variable": "$.last_decision.Payload.execution_mode",
              "StringEquals": "batch_array"
            },
            {
              "Variable": "$.last_decision.Payload.array_size",
              "NumericGreaterThan": 0
            }
          ],
          "Next": "srs_indicators_estimated_tables_part2_generate_est_RunBatch"
        }
      ]
    },
    "srs_indicators_estimated_tables_part2_generate_est_Skip": {
      "Type": "Pass",
      "Next": "srs_indicators_estimated_tables_part3_finalize_Decide"
    },
    "srs_indicators_estimated_tables_part2_generate_est_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('srs-srs_indicators_estimated_tables_part2_generate_est-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "srs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "srs_indicators_estimated_tables_part2_generate_est"
            },
            {
              "Name": "DYNAMODB_TABLE_NAME",
              "Value": "${dynamodb_table_name}"
            },
            {
              "Name": "ARRAY_SIZE",
              "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
            },
            {
              "Name": "KAPTEN_DECISION_REASON",
              "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
            }
          ]
        },
        "Tags": {
          "KaptenPipeline": "srs",
          "KaptenTask": "srs_indicators_estimated_tables_part2_generate_est"
        }
      },
      "ResultPath": null,
      "Next": "srs_indicators_estimated_tables_part3_finalize_Decide"
    },
    "srs_indicators_estimated_tables_part3_finalize_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "srs_indicators_estimated_tables_part3_finalize",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "srs_indicators_estimated_tables_part3_finalize_Choice"
    },
    "srs_indicators_estimated_tables_part3_finalize_Choice": {
      "Type": "Choice",
      "Default": "srs_indicators_estimated_tables_part3_finalize_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Variable": "$.last_decision.Payload.execution_mode",
              "StringEquals": "batch_array"
            },
            {
              "Variable": "$.last_decision.Payload.array_size",
              "NumericGreaterThan": 0
            }
          ],
          "Next": "srs_indicators_estimated_tables_part3_finalize_RunBatch"
        }
      ]
    },
    "srs_indicators_estimated_tables_part3_finalize_Skip": {
      "Type": "Pass",
      "Next": "Lane16Parallel"
    },
    "srs_indicators_estimated_tables_part3_finalize_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('srs-srs_indicators_estimated_tables_part3_finalize-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "srs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "srs_indicators_estimated_tables_part3_finalize"
            },
            {
              "Name": "DYNAMODB_TABLE_NAME",
              "Value": "${dynamodb_table_name}"
            },
            {
              "Name": "ARRAY_SIZE",
              "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
            },
            {
              "Name": "KAPTEN_DECISION_REASON",
              "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
            }
          ]
        },
        "Tags": {
          "KaptenPipeline": "srs",
          "KaptenTask": "srs_indicators_estimated_tables_part3_finalize"
        }
      },
      "ResultPath": null,
      "Next": "Lane16Parallel"
    },
    "Lane16Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "srs_part1_computed_Decide",
          "States": {
            "srs_part1_computed_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_part1_computed",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_part1_computed_Choice"
            },
            "srs_part1_computed_Choice": {
              "Type": "Choice",
              "Default": "srs_part1_computed_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Variable": "$.last_decision.Payload.execution_mode",
                      "StringEquals": "batch_array"
                    },
                    {
                      "Variable": "$.last_decision.Payload.array_size",
                      "NumericGreaterThan": 0
                    }
                  ],
                  "Next": "srs_part1_computed_RunBatch"
                }
              ]
            },
            "srs_part1_computed_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_part1_computed_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('srs-srs_part1_computed-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "srs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "srs_part1_computed"
                    },
                    {
                      "Name": "DYNAMODB_TABLE_NAME",
                      "Value": "${dynamodb_table_name}"
                    },
                    {
                      "Name": "ARRAY_SIZE",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
                    },
                    {
                      "Name": "KAPTEN_DECISION_REASON",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                    }
                  ]
                },
                "Tags": {
                  "KaptenPipeline": "srs",
                  "KaptenTask": "srs_part1_computed"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_part2_groups_Decide",
          "States": {
            "srs_part2_groups_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_part2_groups",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_part2_groups_Choice"
            },
            "srs_part2_groups_Choice": {
              "Type": "Choice",
              "Default": "srs_part2_groups_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_part2_groups_RunEcs"
                }
              ]
            },
            "srs_part2_groups_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_part2_groups_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_part2_groups"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_part2_groups"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane17Parallel"
    },
    "Lane17Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "srs_part2_imputed_a_Decide",
          "States": {
            "srs_part2_imputed_a_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_part2_imputed_a",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_part2_imputed_a_Choice"
            },
            "srs_part2_imputed_a_Choice": {
              "Type": "Choice",
              "Default": "srs_part2_imputed_a_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Variable": "$.last_decision.Payload.execution_mode",
                      "StringEquals": "batch_array"
                    },
                    {
                      "Variable": "$.last_decision.Payload.array_size",
                      "NumericGreaterThan": 0
                    }
                  ],
                  "Next": "srs_part2_imputed_a_RunBatch"
                }
              ]
            },
            "srs_part2_imputed_a_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_part2_imputed_a_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('srs-srs_part2_imputed_a-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "srs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "srs_part2_imputed_a"
                    },
                    {
                      "Name": "DYNAMODB_TABLE_NAME",
                      "Value": "${dynamodb_table_name}"
                    },
                    {
                      "Name": "ARRAY_SIZE",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
                    },
                    {
                      "Name": "KAPTEN_DECISION_REASON",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                    }
                  ]
                },
                "Tags": {
                  "KaptenPipeline": "srs",
                  "KaptenTask": "srs_part2_imputed_a"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_part2_imputed_b_Decide",
          "States": {
            "srs_part2_imputed_b_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_part2_imputed_b",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_part2_imputed_b_Choice"
            },
            "srs_part2_imputed_b_Choice": {
              "Type": "Choice",
              "Default": "srs_part2_imputed_b_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Variable": "$.last_decision.Payload.execution_mode",
                      "StringEquals": "batch_array"
                    },
                    {
                      "Variable": "$.last_decision.Payload.array_size",
                      "NumericGreaterThan": 0
                    }
                  ],
                  "Next": "srs_part2_imputed_b_RunBatch"
                }
              ]
            },
            "srs_part2_imputed_b_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_part2_imputed_b_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('srs-srs_part2_imputed_b-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "srs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "srs_part2_imputed_b"
                    },
                    {
                      "Name": "DYNAMODB_TABLE_NAME",
                      "Value": "${dynamodb_table_name}"
                    },
                    {
                      "Name": "ARRAY_SIZE",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
                    },
                    {
                      "Name": "KAPTEN_DECISION_REASON",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                    }
                  ]
                },
                "Tags": {
                  "KaptenPipeline": "srs",
                  "KaptenTask": "srs_part2_imputed_b"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_part2_imputed_c_Decide",
          "States": {
            "srs_part2_imputed_c_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_part2_imputed_c",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_part2_imputed_c_Choice"
            },
            "srs_part2_imputed_c_Choice": {
              "Type": "Choice",
              "Default": "srs_part2_imputed_c_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Variable": "$.last_decision.Payload.execution_mode",
                      "StringEquals": "batch_array"
                    },
                    {
                      "Variable": "$.last_decision.Payload.array_size",
                      "NumericGreaterThan": 0
                    }
                  ],
                  "Next": "srs_part2_imputed_c_RunBatch"
                }
              ]
            },
            "srs_part2_imputed_c_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_part2_imputed_c_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('srs-srs_part2_imputed_c-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "srs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "srs_part2_imputed_c"
                    },
                    {
                      "Name": "DYNAMODB_TABLE_NAME",
                      "Value": "${dynamodb_table_name}"
                    },
                    {
                      "Name": "ARRAY_SIZE",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
                    },
                    {
                      "Name": "KAPTEN_DECISION_REASON",
                      "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                    }
                  ]
                },
                "Tags": {
                  "KaptenPipeline": "srs",
                  "KaptenTask": "srs_part2_imputed_c"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "srs_part2_stacked_Decide"
    },
    "srs_part2_stacked_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "srs_part2_stacked",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "srs_part2_stacked_Choice"
    },
    "srs_part2_stacked_Choice": {
      "Type": "Choice",
      "Default": "srs_part2_stacked_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Variable": "$.last_decision.Payload.execution_mode",
              "StringEquals": "batch_array"
            },
            {
              "Variable": "$.last_decision.Payload.array_size",
              "NumericGreaterThan": 0
            }
          ],
          "Next": "srs_part2_stacked_RunBatch"
        }
      ]
    },
    "srs_part2_stacked_Skip": {
      "Type": "Pass",
      "Next": "Lane19Parallel"
    },
    "srs_part2_stacked_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('srs-srs_part2_stacked-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "srs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "srs_part2_stacked"
            },
            {
              "Name": "DYNAMODB_TABLE_NAME",
              "Value": "${dynamodb_table_name}"
            },
            {
              "Name": "ARRAY_SIZE",
              "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
            },
            {
              "Name": "KAPTEN_DECISION_REASON",
              "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
            }
          ]
        },
        "Tags": {
          "KaptenPipeline": "srs",
          "KaptenTask": "srs_part2_stacked"
        }
      },
      "ResultPath": null,
      "Next": "Lane19Parallel"
    },
    "Lane19Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "srs_variance_table_list_Decide",
          "States": {
            "srs_variance_table_list_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_variance_table_list",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_variance_table_list_Choice"
            },
            "srs_variance_table_list_Choice": {
              "Type": "Choice",
              "Default": "srs_variance_table_list_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_variance_table_list_RunEcs"
                }
              ]
            },
            "srs_variance_table_list_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_variance_table_list_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_variance_table_list"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_variance_table_list"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "srs_copula_imputed_step3_01_Decide",
          "States": {
            "srs_copula_imputed_step3_01_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "srs_copula_imputed_step3_01",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "srs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "srs_copula_imputed_step3_01_Choice"
            },
            "srs_copula_imputed_step3_01_Choice": {
              "Type": "Choice",
              "Default": "srs_copula_imputed_step3_01_Skip",
              "Choices": [
                {
                  "And": [
                    {
                      "Variable": "$.last_decision.Payload.should_run",
                      "BooleanEquals": true
                    },
                    {
                      "Or": [
                        {
                          "Variable": "$.last_decision.Payload.execution_mode",
                          "StringEquals": "ecs"
                        },
                        {
                          "Not": {
                            "Variable": "$.last_decision.Payload.execution_mode",
                            "IsPresent": true
                          }
                        }
                      ]
                    }
                  ],
                  "Next": "srs_copula_imputed_step3_01_RunEcs"
                }
              ]
            },
            "srs_copula_imputed_step3_01_Skip": {
              "Type": "Pass",
              "End": true
            },
            "srs_copula_imputed_step3_01_RunEcs": {
              "Type": "Task",
              "Resource": "arn:aws:states:::ecs:runTask.sync",
              "Parameters": {
                "Cluster": "${ecs_cluster_arn}",
                "TaskDefinition": "${ecs_task_definition_arn}",
                "LaunchType": "${launch_type}",
                "NetworkConfiguration": {
                  "AwsvpcConfiguration": {
                    "AssignPublicIp": "${assign_public_ip}",
                    "Subnets": ${subnet_ids},
                    "SecurityGroups": ${security_group_ids}
                  }
                },
                "Overrides": {
                  "ContainerOverrides": [
                    {
                      "Name": "${container_name}",
                      "Environment": [
                        {
                          "Name": "KAPTEN_PIPELINE",
                          "Value": "srs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "srs_copula_imputed_step3_01"
                        },
                        {
                          "Name": "DYNAMODB_TABLE_NAME",
                          "Value": "${dynamodb_table_name}"
                        },
                        {
                          "Name": "KAPTEN_DECISION_REASON",
                          "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                        }
                      ]
                    }
                  ]
                },
                "EnableExecuteCommand": true,
                "Tags": [
                  {
                    "Key": "KaptenPipeline",
                    "Value": "srs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "srs_copula_imputed_step3_01"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "srs_variance_tables_prb_Decide"
    },
    "srs_variance_tables_prb_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "srs_variance_tables_prb",
          "execution_mode": "ecs",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "srs_variance_tables_prb_Choice"
    },
    "srs_variance_tables_prb_Choice": {
      "Type": "Choice",
      "Default": "srs_variance_tables_prb_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Or": [
                {
                  "Variable": "$.last_decision.Payload.execution_mode",
                  "StringEquals": "ecs"
                },
                {
                  "Not": {
                    "Variable": "$.last_decision.Payload.execution_mode",
                    "IsPresent": true
                  }
                }
              ]
            }
          ],
          "Next": "srs_variance_tables_prb_RunEcs"
        }
      ]
    },
    "srs_variance_tables_prb_Skip": {
      "Type": "Pass",
      "Next": "srs_copula_imputed_step3_02_prb_Decide"
    },
    "srs_variance_tables_prb_RunEcs": {
      "Type": "Task",
      "Resource": "arn:aws:states:::ecs:runTask.sync",
      "Parameters": {
        "Cluster": "${ecs_cluster_arn}",
        "TaskDefinition": "${ecs_task_definition_arn}",
        "LaunchType": "${launch_type}",
        "NetworkConfiguration": {
          "AwsvpcConfiguration": {
            "AssignPublicIp": "${assign_public_ip}",
            "Subnets": ${subnet_ids},
            "SecurityGroups": ${security_group_ids}
          }
        },
        "Overrides": {
          "ContainerOverrides": [
            {
              "Name": "${container_name}",
              "Environment": [
                {
                  "Name": "KAPTEN_PIPELINE",
                  "Value": "srs"
                },
                {
                  "Name": "KAPTEN_TASK",
                  "Value": "srs_variance_tables_prb"
                },
                {
                  "Name": "DYNAMODB_TABLE_NAME",
                  "Value": "${dynamodb_table_name}"
                },
                {
                  "Name": "KAPTEN_DECISION_REASON",
                  "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
                }
              ]
            }
          ]
        },
        "EnableExecuteCommand": true,
        "Tags": [
          {
            "Key": "KaptenPipeline",
            "Value": "srs"
          },
          {
            "Key": "KaptenTask",
            "Value": "srs_variance_tables_prb"
          }
        ]
      },
      "ResultPath": null,
      "Next": "srs_copula_imputed_step3_02_prb_Decide"
    },
    "srs_copula_imputed_step3_02_prb_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "srs_copula_imputed_step3_02_prb",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "srs_copula_imputed_step3_02_prb_Choice"
    },
    "srs_copula_imputed_step3_02_prb_Choice": {
      "Type": "Choice",
      "Default": "srs_copula_imputed_step3_02_prb_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Variable": "$.last_decision.Payload.execution_mode",
              "StringEquals": "batch_array"
            },
            {
              "Variable": "$.last_decision.Payload.array_size",
              "NumericGreaterThan": 0
            }
          ],
          "Next": "srs_copula_imputed_step3_02_prb_RunBatch"
        }
      ]
    },
    "srs_copula_imputed_step3_02_prb_Skip": {
      "Type": "Pass",
      "Next": "srs_copula_imputed_step3_02_variance_Decide"
    },
    "srs_copula_imputed_step3_02_prb_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('srs-srs_copula_imputed_step3_02_prb-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "srs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "srs_copula_imputed_step3_02_prb"
            },
            {
              "Name": "DYNAMODB_TABLE_NAME",
              "Value": "${dynamodb_table_name}"
            },
            {
              "Name": "ARRAY_SIZE",
              "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
            },
            {
              "Name": "KAPTEN_DECISION_REASON",
              "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
            }
          ]
        },
        "Tags": {
          "KaptenPipeline": "srs",
          "KaptenTask": "srs_copula_imputed_step3_02_prb"
        }
      },
      "ResultPath": null,
      "Next": "srs_copula_imputed_step3_02_variance_Decide"
    },
    "srs_copula_imputed_step3_02_variance_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "srs_copula_imputed_step3_02_variance",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "srs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "srs_copula_imputed_step3_02_variance_Choice"
    },
    "srs_copula_imputed_step3_02_variance_Choice": {
      "Type": "Choice",
      "Default": "srs_copula_imputed_step3_02_variance_Skip",
      "Choices": [
        {
          "And": [
            {
              "Variable": "$.last_decision.Payload.should_run",
              "BooleanEquals": true
            },
            {
              "Variable": "$.last_decision.Payload.execution_mode",
              "StringEquals": "batch_array"
            },
            {
              "Variable": "$.last_decision.Payload.array_size",
              "NumericGreaterThan": 0
            }
          ],
          "Next": "srs_copula_imputed_step3_02_variance_RunBatch"
        }
      ]
    },
    "srs_copula_imputed_step3_02_variance_Skip": {
      "Type": "Pass",
      "End": true
    },
    "srs_copula_imputed_step3_02_variance_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('srs-srs_copula_imputed_step3_02_variance-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "srs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "srs_copula_imputed_step3_02_variance"
            },
            {
              "Name": "DYNAMODB_TABLE_NAME",
              "Value": "${dynamodb_table_name}"
            },
            {
              "Name": "ARRAY_SIZE",
              "Value.$": "States.Format('{}', $.last_decision.Payload.array_size)"
            },
            {
              "Name": "KAPTEN_DECISION_REASON",
              "Value.$": "States.Format('{}', $.last_decision.Payload.reason)"
            }
          ]
        },
        "Tags": {
          "KaptenPipeline": "srs",
          "KaptenTask": "srs_copula_imputed_step3_02_variance"
        }
      },
      "ResultPath": null,
      "End": true
    }
  }
}
