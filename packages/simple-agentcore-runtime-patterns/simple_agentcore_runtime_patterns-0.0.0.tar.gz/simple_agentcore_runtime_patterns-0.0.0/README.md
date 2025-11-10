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
