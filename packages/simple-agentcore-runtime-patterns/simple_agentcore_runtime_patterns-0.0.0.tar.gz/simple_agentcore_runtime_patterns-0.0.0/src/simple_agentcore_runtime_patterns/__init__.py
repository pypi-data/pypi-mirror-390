r'''
# Simple AgentCore Runtime Patterns

An AWS CDK construct library for deploying AWS Bedrock AgentCore runtimes.

This library helps you deploy containerized AI agents to AWS Bedrock AgentCore using AWS CDK. It handles Docker image building, ECR deployment, IAM roles, and runtime configuration automatically.

## Installation

### TypeScript / JavaScript

```bash
npm install simple-agentcore-runtime-patterns
```

### Python

```bash
pip install simple-agentcore-runtime-patterns
```

## Quick Start

### Prerequisites

* AWS CDK installed (`npm install -g aws-cdk`)
* Docker installed and running
* Your agent code in a directory with a `Dockerfile`

### TypeScript Example

```python
import { SimpleAgentCoreRuntime } from 'simple-agentcore-runtime-patterns';
import { App, Stack } from 'aws-cdk-lib';

const app = new App();
const stack = new Stack(app, 'MyStack');

new SimpleAgentCoreRuntime(stack, 'MyAgent', {
  agentName: 'my_bedrock_agent',      // Required: snake_case, max 40 chars
  agentSrcPath: './my-agent-code',    // Required: path to your agent code
});

app.synth();
```

### Python Example

```python
from simple_agentcore_runtime_patterns import SimpleAgentCoreRuntime
from aws_cdk import App, Stack

app = App()
stack = Stack(app, "MyStack")

SimpleAgentCoreRuntime(stack, "MyAgent",
    agent_name="my_bedrock_agent",      # Required: snake_case, max 40 chars
    agent_src_path="./my-agent-code",   # Required: path to your agent code
)

app.synth()
```

## Architecture

```
Input Properties                                                         Outputs
─────────────────                                                        ───────
• agentName                                                              • runtimeId
• agentSrcPath       ┌────────────────────────────────────────────┐     • runtimeVersion
                 ───▶│ SimpleAgentCoreRuntime Construct           │────▶• runtimeArn
                     │                                             │     • runtimeExecutionRole
                     │  ┌──────────────────────────────────────┐  │
                     │  │ IAM Role                             │  │
                     │  │ (AgentCoreRuntimeExecutionRole)      │  │
                     │  │  • ECR access                        │  │
                     │  │  • CloudWatch Logs                   │  │
                     │  │  • Bedrock model invocation          │  │
                     │  └──────────────────┬───────────────────┘  │
                     │                     │                       │
                     │  ┌──────────────────▼───────────────────┐  │
Docker Image ────────┼─▶│ ECR Repository                       │  │
(from agentSrcPath)  │  │  • Stores container image            │  │
                     │  │  • Tag: latest                       │  │
                     │  └──────────────────┬───────────────────┘  │
                     │                     │                       │
                     │  ┌──────────────────▼───────────────────┐  │
                     │  │ Bedrock AgentCore Runtime            │  │
                     │  │  • Runs your agent container         │  │
                     │  │  • Network: PUBLIC (default)         │  │
                     │  │  • Environment variables             │  │
                     │  └──────────────────────────────────────┘  │
                     │                                             │
                     └────────────────────────────────────────────┘
                                      │
                                      │ checks & creates if needed
                                      ▼
                     ┌────────────────────────────────────────────┐
                     │ Service-Linked Roles (Outside Construct)   │
                     │  • Network SLR                             │
                     │  • Runtime Identity SLR                    │
                     └────────────────────────────────────────────┘
```

## Configuration Options

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| `agentName` | string | Name of your agent (snake_case, lowercase, numbers, underscores only, max 40 characters) |
| `agentSrcPath` | string | Path to directory containing your agent code and Dockerfile |

### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ecrRepositoryName` | string | Creates new repository | ECR repository name for container image |
| `runtimeExecutionRole` | IAM Role | Creates new role | IAM role for runtime execution |
| `networkConfiguration` | object | `{ networkMode: 'PUBLIC' }` | Network settings for the runtime |
| `environmentVariables` | object | None | Environment variables for your agent container |
| `agentDescription` | string | None | Description of your agent |

## Documentation

* [API Documentation](./API.md) - Complete API reference
* [AGENTS.md](./AGENTS.md) - Guide for AI coding assistants

## Requirements

* AWS CDK v2.221.0 or later
* Node.js 22 or later
* Docker (for building container images)

## License

MIT-0
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_bedrockagentcore as _aws_cdk_aws_bedrockagentcore_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import constructs as _constructs_77d1e7e8


class IamRoleFactory(
    metaclass=jsii.JSIIMeta,
    jsii_type="simple-agentcore-runtime-patterns.IamRoleFactory",
):
    '''Factory class for creating IAM roles and service-linked roles required by Bedrock AgentCore.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="createRuntimeExecutionRole")
    @builtins.classmethod
    def create_runtime_execution_role(
        cls,
        ctx: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        agent_name: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''Creates an IAM role for Bedrock AgentCore runtime execution.

        The role includes permissions for:

        - ECR image access
        - CloudWatch Logs
        - X-Ray tracing
        - CloudWatch metrics
        - Bedrock model invocation
        - AgentCore workload identity

        :param ctx: - The parent construct.
        :param id: - The construct ID.
        :param agent_name: - The name of the agent runtime.

        :return: The created IAM role
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d97fea57a1f7e730231edd98d82cf19af380408be0f75f1b820f10fc7d4be8e)
            check_type(argname="argument ctx", value=ctx, expected_type=type_hints["ctx"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument agent_name", value=agent_name, expected_type=type_hints["agent_name"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.sinvoke(cls, "createRuntimeExecutionRole", [ctx, id, agent_name]))

    @jsii.member(jsii_name="createServiceLinkedRoles")
    @builtins.classmethod
    def create_service_linked_roles(
        cls,
        ctx: _constructs_77d1e7e8.Construct,
        id: builtins.str,
    ) -> None:
        '''Creates service-linked roles required by Bedrock AgentCore.

        This method creates two service-linked roles:

        - Network SLR for network configuration
        - Runtime Identity SLR for workload identity management

        If the roles already exist, the errors are ignored.

        :param ctx: - The parent construct.
        :param id: - The construct ID.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b468f9087dd9ea96202992660a2d86378e391e3c4d6b16850c481b9a2e83d51c)
            check_type(argname="argument ctx", value=ctx, expected_type=type_hints["ctx"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        return typing.cast(None, jsii.sinvoke(cls, "createServiceLinkedRoles", [ctx, id]))


class SimpleAgentCoreRuntime(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="simple-agentcore-runtime-patterns.SimpleAgentCoreRuntime",
):
    '''A construct that creates an AWS Bedrock AgentCore runtime.

    This construct handles:

    - Building and deploying Docker container images to ECR
    - Creating IAM roles and service-linked roles
    - Configuring Bedrock AgentCore runtime with network and environment settings

    Example::

        new SimpleAgentCoreRuntime(this, 'MyAgent', {
          agentName: 'my-bedrock-agent',
          agentSrcPath: './agent-code',
        });
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        agent_name: builtins.str,
        agent_src_path: builtins.str,
        agent_description: typing.Optional[builtins.str] = None,
        ecr_repository_name: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        network_configuration: typing.Optional[typing.Union[_aws_cdk_aws_bedrockagentcore_ceddda9d.CfnRuntime.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        runtime_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param agent_name: The name of the Bedrock AgentCore runtime. This will be used as the runtime name and default ECR repository name.
        :param agent_src_path: Path to the agent source code directory containing Dockerfile.
        :param agent_description: Description of the agent runtime. Default: - No description
        :param ecr_repository_name: ECR repository name for the agent container image. Default: - Creates a new repository named with agentName
        :param environment_variables: Environment variables to pass to the agent container. Default: - No environment variables
        :param network_configuration: Network configuration for the AgentCore runtime. Default: - PUBLIC network mode: { networkMode: 'PUBLIC' }
        :param runtime_execution_role: IAM role for the AgentCore runtime execution. Default: - Creates a new role with required Bedrock AgentCore permissions
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__481f3e7badf4deb5e6f8d05944da84821bdf4897da5e5834d13c94e0ec8e3a68)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = SimpleAgentCoreRuntimeProps(
            agent_name=agent_name,
            agent_src_path=agent_src_path,
            agent_description=agent_description,
            ecr_repository_name=ecr_repository_name,
            environment_variables=environment_variables,
            network_configuration=network_configuration,
            runtime_execution_role=runtime_execution_role,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="runtimeArn")
    def runtime_arn(self) -> builtins.str:
        '''The ARN of the AgentCore runtime.'''
        return typing.cast(builtins.str, jsii.get(self, "runtimeArn"))

    @builtins.property
    @jsii.member(jsii_name="runtimeExecutionRole")
    def runtime_execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.Role:
        '''The IAM role used by the AgentCore runtime.'''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Role, jsii.get(self, "runtimeExecutionRole"))

    @builtins.property
    @jsii.member(jsii_name="runtimeId")
    def runtime_id(self) -> builtins.str:
        '''The unique identifier of the AgentCore runtime.'''
        return typing.cast(builtins.str, jsii.get(self, "runtimeId"))

    @builtins.property
    @jsii.member(jsii_name="runtimeVersion")
    def runtime_version(self) -> builtins.str:
        '''The version of the AgentCore runtime.'''
        return typing.cast(builtins.str, jsii.get(self, "runtimeVersion"))


@jsii.data_type(
    jsii_type="simple-agentcore-runtime-patterns.SimpleAgentCoreRuntimeProps",
    jsii_struct_bases=[],
    name_mapping={
        "agent_name": "agentName",
        "agent_src_path": "agentSrcPath",
        "agent_description": "agentDescription",
        "ecr_repository_name": "ecrRepositoryName",
        "environment_variables": "environmentVariables",
        "network_configuration": "networkConfiguration",
        "runtime_execution_role": "runtimeExecutionRole",
    },
)
class SimpleAgentCoreRuntimeProps:
    def __init__(
        self,
        *,
        agent_name: builtins.str,
        agent_src_path: builtins.str,
        agent_description: typing.Optional[builtins.str] = None,
        ecr_repository_name: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        network_configuration: typing.Optional[typing.Union[_aws_cdk_aws_bedrockagentcore_ceddda9d.CfnRuntime.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
        runtime_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
    ) -> None:
        '''Properties for SimpleAgentCoreRuntime construct.

        :param agent_name: The name of the Bedrock AgentCore runtime. This will be used as the runtime name and default ECR repository name.
        :param agent_src_path: Path to the agent source code directory containing Dockerfile.
        :param agent_description: Description of the agent runtime. Default: - No description
        :param ecr_repository_name: ECR repository name for the agent container image. Default: - Creates a new repository named with agentName
        :param environment_variables: Environment variables to pass to the agent container. Default: - No environment variables
        :param network_configuration: Network configuration for the AgentCore runtime. Default: - PUBLIC network mode: { networkMode: 'PUBLIC' }
        :param runtime_execution_role: IAM role for the AgentCore runtime execution. Default: - Creates a new role with required Bedrock AgentCore permissions
        '''
        if isinstance(network_configuration, dict):
            network_configuration = _aws_cdk_aws_bedrockagentcore_ceddda9d.CfnRuntime.NetworkConfigurationProperty(**network_configuration)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f94cb6c5267966c60a4bfbf21b4d81b6b1810fb8ca35b8eae96d3a64376453a1)
            check_type(argname="argument agent_name", value=agent_name, expected_type=type_hints["agent_name"])
            check_type(argname="argument agent_src_path", value=agent_src_path, expected_type=type_hints["agent_src_path"])
            check_type(argname="argument agent_description", value=agent_description, expected_type=type_hints["agent_description"])
            check_type(argname="argument ecr_repository_name", value=ecr_repository_name, expected_type=type_hints["ecr_repository_name"])
            check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
            check_type(argname="argument network_configuration", value=network_configuration, expected_type=type_hints["network_configuration"])
            check_type(argname="argument runtime_execution_role", value=runtime_execution_role, expected_type=type_hints["runtime_execution_role"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "agent_name": agent_name,
            "agent_src_path": agent_src_path,
        }
        if agent_description is not None:
            self._values["agent_description"] = agent_description
        if ecr_repository_name is not None:
            self._values["ecr_repository_name"] = ecr_repository_name
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if network_configuration is not None:
            self._values["network_configuration"] = network_configuration
        if runtime_execution_role is not None:
            self._values["runtime_execution_role"] = runtime_execution_role

    @builtins.property
    def agent_name(self) -> builtins.str:
        '''The name of the Bedrock AgentCore runtime.

        This will be used as the runtime name and default ECR repository name.
        '''
        result = self._values.get("agent_name")
        assert result is not None, "Required property 'agent_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_src_path(self) -> builtins.str:
        '''Path to the agent source code directory containing Dockerfile.'''
        result = self._values.get("agent_src_path")
        assert result is not None, "Required property 'agent_src_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_description(self) -> typing.Optional[builtins.str]:
        '''Description of the agent runtime.

        :default: - No description
        '''
        result = self._values.get("agent_description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ecr_repository_name(self) -> typing.Optional[builtins.str]:
        '''ECR repository name for the agent container image.

        :default: - Creates a new repository named with agentName
        '''
        result = self._values.get("ecr_repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables to pass to the agent container.

        :default: - No environment variables
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def network_configuration(
        self,
    ) -> typing.Optional[_aws_cdk_aws_bedrockagentcore_ceddda9d.CfnRuntime.NetworkConfigurationProperty]:
        '''Network configuration for the AgentCore runtime.

        :default: - PUBLIC network mode: { networkMode: 'PUBLIC' }
        '''
        result = self._values.get("network_configuration")
        return typing.cast(typing.Optional[_aws_cdk_aws_bedrockagentcore_ceddda9d.CfnRuntime.NetworkConfigurationProperty], result)

    @builtins.property
    def runtime_execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role]:
        '''IAM role for the AgentCore runtime execution.

        :default: - Creates a new role with required Bedrock AgentCore permissions
        '''
        result = self._values.get("runtime_execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SimpleAgentCoreRuntimeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "IamRoleFactory",
    "SimpleAgentCoreRuntime",
    "SimpleAgentCoreRuntimeProps",
]

publication.publish()

def _typecheckingstub__4d97fea57a1f7e730231edd98d82cf19af380408be0f75f1b820f10fc7d4be8e(
    ctx: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    agent_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b468f9087dd9ea96202992660a2d86378e391e3c4d6b16850c481b9a2e83d51c(
    ctx: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__481f3e7badf4deb5e6f8d05944da84821bdf4897da5e5834d13c94e0ec8e3a68(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    agent_name: builtins.str,
    agent_src_path: builtins.str,
    agent_description: typing.Optional[builtins.str] = None,
    ecr_repository_name: typing.Optional[builtins.str] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    network_configuration: typing.Optional[typing.Union[_aws_cdk_aws_bedrockagentcore_ceddda9d.CfnRuntime.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    runtime_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f94cb6c5267966c60a4bfbf21b4d81b6b1810fb8ca35b8eae96d3a64376453a1(
    *,
    agent_name: builtins.str,
    agent_src_path: builtins.str,
    agent_description: typing.Optional[builtins.str] = None,
    ecr_repository_name: typing.Optional[builtins.str] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    network_configuration: typing.Optional[typing.Union[_aws_cdk_aws_bedrockagentcore_ceddda9d.CfnRuntime.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]] = None,
    runtime_execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.Role] = None,
) -> None:
    """Type checking stubs"""
    pass
