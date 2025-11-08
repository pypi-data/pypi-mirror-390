{
  "Comment": "kptn generated state machine for nibrs",
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
                  "PIPELINE_NAME": "nibrs"
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
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
                  "PIPELINE_NAME": "nibrs"
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
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
                  "PIPELINE_NAME": "nibrs"
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
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
          "StartAt": "nibrs_extract_victim_offender_relationship_Decide",
          "States": {
            "nibrs_extract_victim_offender_relationship_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "nibrs_extract_victim_offender_relationship",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "nibrs_extract_victim_offender_relationship_Choice"
            },
            "nibrs_extract_victim_offender_relationship_Choice": {
              "Type": "Choice",
              "Default": "nibrs_extract_victim_offender_relationship_Skip",
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
                  "Next": "nibrs_extract_victim_offender_relationship_RunEcs"
                }
              ]
            },
            "nibrs_extract_victim_offender_relationship_Skip": {
              "Type": "Pass",
              "End": true
            },
            "nibrs_extract_victim_offender_relationship_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "nibrs_extract_victim_offender_relationship"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "nibrs_extract_victim_offender_relationship"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "vic_off_rel_nums_Decide",
          "States": {
            "vic_off_rel_nums_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "vic_off_rel_nums",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "vic_off_rel_nums_Choice"
            },
            "vic_off_rel_nums_Choice": {
              "Type": "Choice",
              "Default": "vic_off_rel_nums_Skip",
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
                  "Next": "vic_off_rel_nums_RunEcs"
                }
              ]
            },
            "vic_off_rel_nums_Skip": {
              "Type": "Pass",
              "End": true
            },
            "vic_off_rel_nums_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "vic_off_rel_nums"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "vic_off_rel_nums"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "setup_part_200b_datasets_Decide",
          "States": {
            "setup_part_200b_datasets_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "setup_part_200b_datasets",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "setup_part_200b_datasets_Choice"
            },
            "setup_part_200b_datasets_Choice": {
              "Type": "Choice",
              "Default": "setup_part_200b_datasets_Skip",
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
                  "Next": "setup_part_200b_datasets_RunEcs"
                }
              ]
            },
            "setup_part_200b_datasets_Skip": {
              "Type": "Pass",
              "End": true
            },
            "setup_part_200b_datasets_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "setup_part_200b_datasets"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "setup_part_200b_datasets"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "setup_clean_main_topics_Decide",
          "States": {
            "setup_clean_main_topics_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "setup_clean_main_topics",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "setup_clean_main_topics_Choice"
            },
            "setup_clean_main_topics_Choice": {
              "Type": "Choice",
              "Default": "setup_clean_main_topics_Skip",
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
                  "Next": "setup_clean_main_topics_RunEcs"
                }
              ]
            },
            "setup_clean_main_topics_Skip": {
              "Type": "Pass",
              "End": true
            },
            "setup_clean_main_topics_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "setup_clean_main_topics"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "setup_clean_main_topics"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "tables_Decide",
          "States": {
            "tables_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "tables",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "tables_Choice"
            },
            "tables_Choice": {
              "Type": "Choice",
              "Default": "tables_Skip",
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
                  "Next": "tables_RunEcs"
                }
              ]
            },
            "tables_Skip": {
              "Type": "Pass",
              "End": true
            },
            "tables_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "tables"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "tables"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "estimate_combos_Decide",
          "States": {
            "estimate_combos_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "estimate_combos",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "estimate_combos_Choice"
            },
            "estimate_combos_Choice": {
              "Type": "Choice",
              "Default": "estimate_combos_Skip",
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
                  "Next": "estimate_combos_RunEcs"
                }
              ]
            },
            "estimate_combos_Skip": {
              "Type": "Pass",
              "End": true
            },
            "estimate_combos_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "estimate_combos"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "estimate_combos"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "add_col_combos_Decide",
          "States": {
            "add_col_combos_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "add_col_combos",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "add_col_combos_Choice"
            },
            "add_col_combos_Choice": {
              "Type": "Choice",
              "Default": "add_col_combos_Skip",
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
                  "Next": "add_col_combos_RunEcs"
                }
              ]
            },
            "add_col_combos_Skip": {
              "Type": "Pass",
              "End": true
            },
            "add_col_combos_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "add_col_combos"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "add_col_combos"
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
                  "PIPELINE_NAME": "nibrs"
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
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
          "StartAt": "nibrs_extract_one_state_Decide",
          "States": {
            "nibrs_extract_one_state_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "nibrs_extract_one_state",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "nibrs_extract_one_state_Choice"
            },
            "nibrs_extract_one_state_Choice": {
              "Type": "Choice",
              "Default": "nibrs_extract_one_state_Skip",
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
                  "Next": "nibrs_extract_one_state_RunBatch"
                }
              ]
            },
            "nibrs_extract_one_state_Skip": {
              "Type": "Pass",
              "End": true
            },
            "nibrs_extract_one_state_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-nibrs_extract_one_state-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "nibrs_extract_one_state"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "nibrs_extract_one_state"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "nibrs_extract_one_state_property_Decide",
          "States": {
            "nibrs_extract_one_state_property_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "nibrs_extract_one_state_property",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "nibrs_extract_one_state_property_Choice"
            },
            "nibrs_extract_one_state_property_Choice": {
              "Type": "Choice",
              "Default": "nibrs_extract_one_state_property_Skip",
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
                  "Next": "nibrs_extract_one_state_property_RunBatch"
                }
              ]
            },
            "nibrs_extract_one_state_property_Skip": {
              "Type": "Pass",
              "End": true
            },
            "nibrs_extract_one_state_property_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-nibrs_extract_one_state_property-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "nibrs_extract_one_state_property"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "nibrs_extract_one_state_property"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "dependent_states_Decide",
          "States": {
            "dependent_states_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "dependent_states",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "dependent_states_Choice"
            },
            "dependent_states_Choice": {
              "Type": "Choice",
              "Default": "dependent_states_Skip",
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
                  "Next": "dependent_states_RunEcs"
                }
              ]
            },
            "dependent_states_Skip": {
              "Type": "Pass",
              "End": true
            },
            "dependent_states_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "dependent_states"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "dependent_states"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "independent_states_Decide",
          "States": {
            "independent_states_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "independent_states",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "independent_states_Choice"
            },
            "independent_states_Choice": {
              "Type": "Choice",
              "Default": "independent_states_Skip",
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
                  "Next": "independent_states_RunEcs"
                }
              ]
            },
            "independent_states_Skip": {
              "Type": "Pass",
              "End": true
            },
            "independent_states_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "independent_states"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "independent_states"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
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
                  "PIPELINE_NAME": "nibrs"
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
                "JobName.$": "States.Format('nibrs-universe_created-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "universe_created"
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
          "StartAt": "msa_provider_Decide",
          "States": {
            "msa_provider_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "msa_provider",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "msa_provider_Choice"
            },
            "msa_provider_Choice": {
              "Type": "Choice",
              "Default": "msa_provider_Skip",
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
                  "Next": "msa_provider_RunEcs"
                }
              ]
            },
            "msa_provider_Skip": {
              "Type": "Pass",
              "End": true
            },
            "msa_provider_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "msa_provider"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "msa_provider"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "items_imputed_part1_Decide",
          "States": {
            "items_imputed_part1_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "items_imputed_part1",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "items_imputed_part1_Choice"
            },
            "items_imputed_part1_Choice": {
              "Type": "Choice",
              "Default": "items_imputed_part1_Skip",
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
                  "Next": "items_imputed_part1_RunBatch"
                }
              ]
            },
            "items_imputed_part1_Skip": {
              "Type": "Pass",
              "End": true
            },
            "items_imputed_part1_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-items_imputed_part1-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "items_imputed_part1"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "items_imputed_part1"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "indicators_estimated_setup_Decide",
          "States": {
            "indicators_estimated_setup_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "indicators_estimated_setup",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "indicators_estimated_setup_Choice"
            },
            "indicators_estimated_setup_Choice": {
              "Type": "Choice",
              "Default": "indicators_estimated_setup_Skip",
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
                  "Next": "indicators_estimated_setup_RunBatch"
                }
              ]
            },
            "indicators_estimated_setup_Skip": {
              "Type": "Pass",
              "End": true
            },
            "indicators_estimated_setup_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-indicators_estimated_setup-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "indicators_estimated_setup"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "indicators_estimated_setup"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
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
                  "PIPELINE_NAME": "nibrs"
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
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
        }
      ],
      "Next": "Lane3Parallel"
    },
    "Lane3Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "items_imputed_part2_nonperson_Decide",
          "States": {
            "items_imputed_part2_nonperson_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "items_imputed_part2_nonperson",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "items_imputed_part2_nonperson_Choice"
            },
            "items_imputed_part2_nonperson_Choice": {
              "Type": "Choice",
              "Default": "items_imputed_part2_nonperson_Skip",
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
                  "Next": "items_imputed_part2_nonperson_RunBatch"
                }
              ]
            },
            "items_imputed_part2_nonperson_Skip": {
              "Type": "Pass",
              "End": true
            },
            "items_imputed_part2_nonperson_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-items_imputed_part2_nonperson-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "items_imputed_part2_nonperson"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "items_imputed_part2_nonperson"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "items_imputed_part2_person_Decide",
          "States": {
            "items_imputed_part2_person_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "items_imputed_part2_person",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "items_imputed_part2_person_Choice"
            },
            "items_imputed_part2_person_Choice": {
              "Type": "Choice",
              "Default": "items_imputed_part2_person_Skip",
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
                  "Next": "items_imputed_part2_person_RunBatch"
                }
              ]
            },
            "items_imputed_part2_person_Skip": {
              "Type": "Pass",
              "End": true
            },
            "items_imputed_part2_person_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-items_imputed_part2_person-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "items_imputed_part2_person"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "items_imputed_part2_person"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "indicators_estimated_setup_part2_00a_1_Decide",
          "States": {
            "indicators_estimated_setup_part2_00a_1_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "indicators_estimated_setup_part2_00a_1",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "indicators_estimated_setup_part2_00a_1_Choice"
            },
            "indicators_estimated_setup_part2_00a_1_Choice": {
              "Type": "Choice",
              "Default": "indicators_estimated_setup_part2_00a_1_Skip",
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
                  "Next": "indicators_estimated_setup_part2_00a_1_RunEcs"
                }
              ]
            },
            "indicators_estimated_setup_part2_00a_1_Skip": {
              "Type": "Pass",
              "End": true
            },
            "indicators_estimated_setup_part2_00a_1_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "indicators_estimated_setup_part2_00a_1"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "indicators_estimated_setup_part2_00a_1"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
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
                  "PIPELINE_NAME": "nibrs"
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
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
        }
      ],
      "Next": "Lane4Parallel"
    },
    "Lane4Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "items_imputed_part3_Decide",
          "States": {
            "items_imputed_part3_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "items_imputed_part3",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "items_imputed_part3_Choice"
            },
            "items_imputed_part3_Choice": {
              "Type": "Choice",
              "Default": "items_imputed_part3_Skip",
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
                  "Next": "items_imputed_part3_RunBatch"
                }
              ]
            },
            "items_imputed_part3_Skip": {
              "Type": "Pass",
              "End": true
            },
            "items_imputed_part3_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-items_imputed_part3-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "items_imputed_part3"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "items_imputed_part3"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "indicators_estimated_setup_part2_00a_2_Decide",
          "States": {
            "indicators_estimated_setup_part2_00a_2_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "indicators_estimated_setup_part2_00a_2",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "indicators_estimated_setup_part2_00a_2_Choice"
            },
            "indicators_estimated_setup_part2_00a_2_Choice": {
              "Type": "Choice",
              "Default": "indicators_estimated_setup_part2_00a_2_Skip",
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
                  "Next": "indicators_estimated_setup_part2_00a_2_RunEcs"
                }
              ]
            },
            "indicators_estimated_setup_part2_00a_2_Skip": {
              "Type": "Pass",
              "End": true
            },
            "indicators_estimated_setup_part2_00a_2_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "indicators_estimated_setup_part2_00a_2"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "indicators_estimated_setup_part2_00a_2"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "universe_updated_Decide",
          "States": {
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
                  "PIPELINE_NAME": "nibrs"
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
              "End": true
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "universe_updated"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane5Parallel"
    },
    "Lane5Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "items_imputed_part4_vor_Decide",
          "States": {
            "items_imputed_part4_vor_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "items_imputed_part4_vor",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "items_imputed_part4_vor_Choice"
            },
            "items_imputed_part4_vor_Choice": {
              "Type": "Choice",
              "Default": "items_imputed_part4_vor_Skip",
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
                  "Next": "items_imputed_part4_vor_RunBatch"
                }
              ]
            },
            "items_imputed_part4_vor_Skip": {
              "Type": "Pass",
              "End": true
            },
            "items_imputed_part4_vor_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-items_imputed_part4_vor-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "items_imputed_part4_vor"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "items_imputed_part4_vor"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "pop_totals_updated_Decide",
          "States": {
            "pop_totals_updated_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "pop_totals_updated",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "pop_totals_updated_Choice"
            },
            "pop_totals_updated_Choice": {
              "Type": "Choice",
              "Default": "pop_totals_updated_Skip",
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
                  "Next": "pop_totals_updated_RunEcs"
                }
              ]
            },
            "pop_totals_updated_Skip": {
              "Type": "Pass",
              "End": true
            },
            "pop_totals_updated_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "pop_totals_updated"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "pop_totals_updated"
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
                  "PIPELINE_NAME": "nibrs"
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
                "JobName.$": "States.Format('nibrs-missing_months-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "missing_months"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane6Parallel"
    },
    "Lane6Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "items_imputed_part4_vor_dep_Decide",
          "States": {
            "items_imputed_part4_vor_dep_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "items_imputed_part4_vor_dep",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "items_imputed_part4_vor_dep_Choice"
            },
            "items_imputed_part4_vor_dep_Choice": {
              "Type": "Choice",
              "Default": "items_imputed_part4_vor_dep_Skip",
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
                  "Next": "items_imputed_part4_vor_dep_RunBatch"
                }
              ]
            },
            "items_imputed_part4_vor_dep_Skip": {
              "Type": "Pass",
              "End": true
            },
            "items_imputed_part4_vor_dep_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-items_imputed_part4_vor_dep-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "items_imputed_part4_vor_dep"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "items_imputed_part4_vor_dep"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "partial_reporters_Decide",
          "States": {
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
                  "PIPELINE_NAME": "nibrs"
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
              "End": true
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "partial_reporters"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane7Parallel"
    },
    "Lane7Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "items_imputed_part4_vor_prop_Decide",
          "States": {
            "items_imputed_part4_vor_prop_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "items_imputed_part4_vor_prop",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "items_imputed_part4_vor_prop_Choice"
            },
            "items_imputed_part4_vor_prop_Choice": {
              "Type": "Choice",
              "Default": "items_imputed_part4_vor_prop_Skip",
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
                  "Next": "items_imputed_part4_vor_prop_RunBatch"
                }
              ]
            },
            "items_imputed_part4_vor_prop_Skip": {
              "Type": "Pass",
              "End": true
            },
            "items_imputed_part4_vor_prop_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-items_imputed_part4_vor_prop-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "items_imputed_part4_vor_prop"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "items_imputed_part4_vor_prop"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "outliers_detected_Decide",
          "States": {
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
                  "PIPELINE_NAME": "nibrs"
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
              "End": true
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "outliers_detected"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "Lane8Parallel"
    },
    "Lane8Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "weights_computed_Decide",
          "States": {
            "weights_computed_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "weights_computed",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "weights_computed_Choice"
            },
            "weights_computed_Choice": {
              "Type": "Choice",
              "Default": "weights_computed_Skip",
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
                  "Next": "weights_computed_RunEcs"
                }
              ]
            },
            "weights_computed_Skip": {
              "Type": "Pass",
              "End": true
            },
            "weights_computed_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "weights_computed"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "weights_computed"
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
                  "PIPELINE_NAME": "nibrs"
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
                          "Value": "nibrs"
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
                    "Value": "nibrs"
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
      "Next": "Lane9Parallel"
    },
    "Lane9Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "calibrate_variables_Decide",
          "States": {
            "calibrate_variables_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "calibrate_variables",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "calibrate_variables_Choice"
            },
            "calibrate_variables_Choice": {
              "Type": "Choice",
              "Default": "calibrate_variables_Skip",
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
                  "Next": "calibrate_variables_RunEcs"
                }
              ]
            },
            "calibrate_variables_Skip": {
              "Type": "Pass",
              "End": true
            },
            "calibrate_variables_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "calibrate_variables"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "calibrate_variables"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "indicators_estimated_setup_part2_00b_Decide",
          "States": {
            "indicators_estimated_setup_part2_00b_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "indicators_estimated_setup_part2_00b",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "indicators_estimated_setup_part2_00b_Choice"
            },
            "indicators_estimated_setup_part2_00b_Choice": {
              "Type": "Choice",
              "Default": "indicators_estimated_setup_part2_00b_Skip",
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
                  "Next": "indicators_estimated_setup_part2_00b_RunBatch"
                }
              ]
            },
            "indicators_estimated_setup_part2_00b_Skip": {
              "Type": "Pass",
              "End": true
            },
            "indicators_estimated_setup_part2_00b_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-indicators_estimated_setup_part2_00b-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "indicators_estimated_setup_part2_00b"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "indicators_estimated_setup_part2_00b"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "indicator_estimated_setup_part2_weights_Decide",
          "States": {
            "indicator_estimated_setup_part2_weights_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "indicator_estimated_setup_part2_weights",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "indicator_estimated_setup_part2_weights_Choice"
            },
            "indicator_estimated_setup_part2_weights_Choice": {
              "Type": "Choice",
              "Default": "indicator_estimated_setup_part2_weights_Skip",
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
                  "Next": "indicator_estimated_setup_part2_weights_RunEcs"
                }
              ]
            },
            "indicator_estimated_setup_part2_weights_Skip": {
              "Type": "Pass",
              "End": true
            },
            "indicator_estimated_setup_part2_weights_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "indicator_estimated_setup_part2_weights"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "indicator_estimated_setup_part2_weights"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "indicator_estimated_setup_part2_00c_clean_main_part1_Decide"
    },
    "indicator_estimated_setup_part2_00c_clean_main_part1_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "indicator_estimated_setup_part2_00c_clean_main_part1",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "nibrs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "indicator_estimated_setup_part2_00c_clean_main_part1_Choice"
    },
    "indicator_estimated_setup_part2_00c_clean_main_part1_Choice": {
      "Type": "Choice",
      "Default": "indicator_estimated_setup_part2_00c_clean_main_part1_Skip",
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
          "Next": "indicator_estimated_setup_part2_00c_clean_main_part1_RunBatch"
        }
      ]
    },
    "indicator_estimated_setup_part2_00c_clean_main_part1_Skip": {
      "Type": "Pass",
      "Next": "indicator_estimated_setup_part2_00c_clean_main_part2_Decide"
    },
    "indicator_estimated_setup_part2_00c_clean_main_part1_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('nibrs-indicator_estimated_setup_part2_00c_clean_main_part1-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "nibrs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "indicator_estimated_setup_part2_00c_clean_main_part1"
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
          "KaptenPipeline": "nibrs",
          "KaptenTask": "indicator_estimated_setup_part2_00c_clean_main_part1"
        }
      },
      "ResultPath": null,
      "Next": "indicator_estimated_setup_part2_00c_clean_main_part2_Decide"
    },
    "indicator_estimated_setup_part2_00c_clean_main_part2_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "indicator_estimated_setup_part2_00c_clean_main_part2",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "nibrs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "indicator_estimated_setup_part2_00c_clean_main_part2_Choice"
    },
    "indicator_estimated_setup_part2_00c_clean_main_part2_Choice": {
      "Type": "Choice",
      "Default": "indicator_estimated_setup_part2_00c_clean_main_part2_Skip",
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
          "Next": "indicator_estimated_setup_part2_00c_clean_main_part2_RunBatch"
        }
      ]
    },
    "indicator_estimated_setup_part2_00c_clean_main_part2_Skip": {
      "Type": "Pass",
      "Next": "Lane12Parallel"
    },
    "indicator_estimated_setup_part2_00c_clean_main_part2_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('nibrs-indicator_estimated_setup_part2_00c_clean_main_part2-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "nibrs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "indicator_estimated_setup_part2_00c_clean_main_part2"
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
          "KaptenPipeline": "nibrs",
          "KaptenTask": "indicator_estimated_setup_part2_00c_clean_main_part2"
        }
      },
      "ResultPath": null,
      "Next": "Lane12Parallel"
    },
    "Lane12Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "indicator_estimated_setup_part2_00d_agency_ori_Decide",
          "States": {
            "indicator_estimated_setup_part2_00d_agency_ori_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "indicator_estimated_setup_part2_00d_agency_ori",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "indicator_estimated_setup_part2_00d_agency_ori_Choice"
            },
            "indicator_estimated_setup_part2_00d_agency_ori_Choice": {
              "Type": "Choice",
              "Default": "indicator_estimated_setup_part2_00d_agency_ori_Skip",
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
                  "Next": "indicator_estimated_setup_part2_00d_agency_ori_RunEcs"
                }
              ]
            },
            "indicator_estimated_setup_part2_00d_agency_ori_Skip": {
              "Type": "Pass",
              "End": true
            },
            "indicator_estimated_setup_part2_00d_agency_ori_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "indicator_estimated_setup_part2_00d_agency_ori"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "indicator_estimated_setup_part2_00d_agency_ori"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "indicator_estimated_setup_part2_00c_gv_main_Decide",
          "States": {
            "indicator_estimated_setup_part2_00c_gv_main_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "indicator_estimated_setup_part2_00c_gv_main",
                  "execution_mode": "ecs",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "indicator_estimated_setup_part2_00c_gv_main_Choice"
            },
            "indicator_estimated_setup_part2_00c_gv_main_Choice": {
              "Type": "Choice",
              "Default": "indicator_estimated_setup_part2_00c_gv_main_Skip",
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
                  "Next": "indicator_estimated_setup_part2_00c_gv_main_RunEcs"
                }
              ]
            },
            "indicator_estimated_setup_part2_00c_gv_main_Skip": {
              "Type": "Pass",
              "End": true
            },
            "indicator_estimated_setup_part2_00c_gv_main_RunEcs": {
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
                          "Value": "nibrs"
                        },
                        {
                          "Name": "KAPTEN_TASK",
                          "Value": "indicator_estimated_setup_part2_00c_gv_main"
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
                    "Value": "nibrs"
                  },
                  {
                    "Key": "KaptenTask",
                    "Value": "indicator_estimated_setup_part2_00c_gv_main"
                  }
                ]
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "indicators_estimated_tables_part1_preprocessing_Decide"
    },
    "indicators_estimated_tables_part1_preprocessing_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "indicators_estimated_tables_part1_preprocessing",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "nibrs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "indicators_estimated_tables_part1_preprocessing_Choice"
    },
    "indicators_estimated_tables_part1_preprocessing_Choice": {
      "Type": "Choice",
      "Default": "indicators_estimated_tables_part1_preprocessing_Skip",
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
          "Next": "indicators_estimated_tables_part1_preprocessing_RunBatch"
        }
      ]
    },
    "indicators_estimated_tables_part1_preprocessing_Skip": {
      "Type": "Pass",
      "Next": "Lane14Parallel"
    },
    "indicators_estimated_tables_part1_preprocessing_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('nibrs-indicators_estimated_tables_part1_preprocessing-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "nibrs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "indicators_estimated_tables_part1_preprocessing"
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
          "KaptenPipeline": "nibrs",
          "KaptenTask": "indicators_estimated_tables_part1_preprocessing"
        }
      },
      "ResultPath": null,
      "Next": "Lane14Parallel"
    },
    "Lane14Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "indicators_estimated_tables_part2_generate_est_Decide",
          "States": {
            "indicators_estimated_tables_part2_generate_est_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "indicators_estimated_tables_part2_generate_est",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "indicators_estimated_tables_part2_generate_est_Choice"
            },
            "indicators_estimated_tables_part2_generate_est_Choice": {
              "Type": "Choice",
              "Default": "indicators_estimated_tables_part2_generate_est_Skip",
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
                  "Next": "indicators_estimated_tables_part2_generate_est_RunBatch"
                }
              ]
            },
            "indicators_estimated_tables_part2_generate_est_Skip": {
              "Type": "Pass",
              "End": true
            },
            "indicators_estimated_tables_part2_generate_est_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-indicators_estimated_tables_part2_generate_est-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "indicators_estimated_tables_part2_generate_est"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "indicators_estimated_tables_part2_generate_est"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        },
        {
          "StartAt": "indicators_estimated_tables_part2_create_additional_columns_Decide",
          "States": {
            "indicators_estimated_tables_part2_create_additional_columns_Decide": {
              "Type": "Task",
              "Resource": "arn:aws:states:::lambda:invoke",
              "Parameters": {
                "FunctionName": "${decider_lambda_arn}",
                "Payload": {
                  "state.$": "$",
                  "task_name": "indicators_estimated_tables_part2_create_additional_columns",
                  "execution_mode": "batch_array",
                  "TASKS_CONFIG_PATH": "kptn.yaml",
                  "PIPELINE_NAME": "nibrs"
                }
              },
              "ResultSelector": {
                "Payload.$": "$.Payload"
              },
              "ResultPath": "$.last_decision",
              "OutputPath": "$",
              "Next": "indicators_estimated_tables_part2_create_additional_columns_Choice"
            },
            "indicators_estimated_tables_part2_create_additional_columns_Choice": {
              "Type": "Choice",
              "Default": "indicators_estimated_tables_part2_create_additional_columns_Skip",
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
                  "Next": "indicators_estimated_tables_part2_create_additional_columns_RunBatch"
                }
              ]
            },
            "indicators_estimated_tables_part2_create_additional_columns_Skip": {
              "Type": "Pass",
              "End": true
            },
            "indicators_estimated_tables_part2_create_additional_columns_RunBatch": {
              "Type": "Task",
              "Resource": "arn:aws:states:::batch:submitJob.sync",
              "Parameters": {
                "JobName.$": "States.Format('nibrs-indicators_estimated_tables_part2_create_additional_columns-{}', $$.Execution.Name)",
                "JobQueue": "${batch_job_queue_arn}",
                "JobDefinition": "${batch_job_definition_arn}",
                "ArrayProperties": {
                  "Size.$": "$.last_decision.Payload.array_size"
                },
                "ContainerOverrides": {
                  "Environment": [
                    {
                      "Name": "KAPTEN_PIPELINE",
                      "Value": "nibrs"
                    },
                    {
                      "Name": "KAPTEN_TASK",
                      "Value": "indicators_estimated_tables_part2_create_additional_columns"
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
                  "KaptenPipeline": "nibrs",
                  "KaptenTask": "indicators_estimated_tables_part2_create_additional_columns"
                }
              },
              "ResultPath": null,
              "End": true
            }
          }
        }
      ],
      "Next": "indicators_estimated_tables_part3_finalize_Decide"
    },
    "indicators_estimated_tables_part3_finalize_Decide": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "FunctionName": "${decider_lambda_arn}",
        "Payload": {
          "state.$": "$",
          "task_name": "indicators_estimated_tables_part3_finalize",
          "execution_mode": "batch_array",
          "TASKS_CONFIG_PATH": "kptn.yaml",
          "PIPELINE_NAME": "nibrs"
        }
      },
      "ResultSelector": {
        "Payload.$": "$.Payload"
      },
      "ResultPath": "$.last_decision",
      "OutputPath": "$",
      "Next": "indicators_estimated_tables_part3_finalize_Choice"
    },
    "indicators_estimated_tables_part3_finalize_Choice": {
      "Type": "Choice",
      "Default": "indicators_estimated_tables_part3_finalize_Skip",
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
          "Next": "indicators_estimated_tables_part3_finalize_RunBatch"
        }
      ]
    },
    "indicators_estimated_tables_part3_finalize_Skip": {
      "Type": "Pass",
      "End": true
    },
    "indicators_estimated_tables_part3_finalize_RunBatch": {
      "Type": "Task",
      "Resource": "arn:aws:states:::batch:submitJob.sync",
      "Parameters": {
        "JobName.$": "States.Format('nibrs-indicators_estimated_tables_part3_finalize-{}', $$.Execution.Name)",
        "JobQueue": "${batch_job_queue_arn}",
        "JobDefinition": "${batch_job_definition_arn}",
        "ArrayProperties": {
          "Size.$": "$.last_decision.Payload.array_size"
        },
        "ContainerOverrides": {
          "Environment": [
            {
              "Name": "KAPTEN_PIPELINE",
              "Value": "nibrs"
            },
            {
              "Name": "KAPTEN_TASK",
              "Value": "indicators_estimated_tables_part3_finalize"
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
          "KaptenPipeline": "nibrs",
          "KaptenTask": "indicators_estimated_tables_part3_finalize"
        }
      },
      "ResultPath": null,
      "End": true
    }
  }
}
