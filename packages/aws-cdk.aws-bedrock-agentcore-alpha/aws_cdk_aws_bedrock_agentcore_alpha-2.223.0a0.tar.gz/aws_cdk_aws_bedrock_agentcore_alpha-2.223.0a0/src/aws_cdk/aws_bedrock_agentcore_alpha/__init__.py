r'''
# Amazon Bedrock AgentCore Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Language**                                                                                   | **Package**                             |
| :--------------------------------------------------------------------------------------------- | --------------------------------------- |
| ![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) TypeScript | `@aws-cdk/aws-bedrock-agentcore-alpha` |

[Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/) enables you to deploy and operate highly capable AI agents securely, at scale. It offers infrastructure purpose-built for dynamic agent workloads, powerful tools to enhance agents, and essential controls for real-world deployment. AgentCore services can be used together or independently and work with any framework including CrewAI, LangGraph, LlamaIndex, and Strands Agents, as well as any foundation model in or outside of Amazon Bedrock, giving you ultimate flexibility. AgentCore eliminates the undifferentiated heavy lifting of building specialized agent infrastructure, so you can accelerate agents to production.

This construct library facilitates the deployment of Bedrock AgentCore primitives, enabling you to create sophisticated AI applications that can interact with your systems and data sources.

## Table of contents

* [AgentCore Runtime](#agentcore-runtime)

  * [Runtime Versioning](#runtime-versioning)
  * [Runtime Endpoints](#runtime-endpoints)
  * [AgentCore Runtime Properties](#agentcore-runtime-properties)
  * [Runtime Endpoint Properties](#runtime-endpoint-properties)
  * [Creating a Runtime](#creating-a-runtime)

    * [Option 1: Use an existing image in ECR](#option-1-use-an-existing-image-in-ecr)
    * [Managing Endpoints and Versions](#managing-endpoints-and-versions)
    * [Option 2: Use a local asset](#option-2-use-a-local-asset)
* [Browser Custom tool](#browser)

  * [Browser properties](#browser-properties)
  * [Browser Network modes](#browser-network-modes)
  * [Basic Browser Creation](#basic-browser-creation)
  * [Browser IAM permissions](#browser-iam-permissions)
* [Code Interpreter Custom tool](#code-interpreter)

  * [Code Interpreter properties](#code-interpreter-properties)
  * [Code Interpreter Network Modes](#code-interpreter-network-modes)
  * [Basic Code Interpreter Creation](#basic-code-interpreter-creation)
  * [Code Interpreter IAM permissions](#code-interpreter-iam-permissions)
* [Memory](#memory)

  * [Memory properties](#memory-properties)
  * [Basic Memory Creation](#basic-memory-creation)
  * [LTM Memory Extraction Stategies](#ltm-memory-extraction-stategies)
  * [Memory Strategy Methods](#memory-strategy-methods)

## AgentCore Runtime

The AgentCore Runtime construct enables you to deploy containerized agents on Amazon Bedrock AgentCore.
This L2 construct simplifies runtime creation just pass your ECR repository name
and the construct handles all the configuration with sensible defaults.

### Runtime Endpoints

Endpoints provide a stable way to invoke specific versions of your agent runtime, enabling controlled deployments across different environments.
When you create an agent runtime, Amazon Bedrock AgentCore automatically creates a "DEFAULT" endpoint which always points to the latest version
of runtime.

You can create additional endpoints in two ways:

1. **Using Runtime.addEndpoint()** - Convenient method when creating endpoints alongside the runtime.
2. **Using RuntimeEndpoint** - Flexible approach for existing runtimes.

For example, you might keep a "production" endpoint on a stable version while testing newer versions
through a "staging" endpoint. This separation allows you to test changes thoroughly before promoting them
to production by simply updating the endpoint to point to the newer version.

### AgentCore Runtime Properties

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `runtimeName` | `string` | Yes | The name of the agent runtime. Valid characters are a-z, A-Z, 0-9, _ (underscore). Must start with a letter and can be up to 48 characters long |
| `agentRuntimeArtifact` | `AgentRuntimeArtifact` | Yes | The artifact configuration for the agent runtime containing the container configuration with ECR URI |
| `executionRole` | `iam.IRole` | No | The IAM role that provides permissions for the agent runtime. If not provided, a role will be created automatically |
| `networkConfiguration` | `NetworkConfiguration` | No | Network configuration for the agent runtime. Defaults to `RuntimeNetworkConfiguration.usingPublicNetwork()` |
| `description` | `string` | No | Optional description for the agent runtime |
| `protocolConfiguration` | `ProtocolType` | No | Protocol configuration for the agent runtime. Defaults to `ProtocolType.HTTP` |
| `authorizerConfiguration` | `RuntimeAuthorizerConfiguration` | No | Authorizer configuration for the agent runtime. Use `RuntimeAuthorizerConfiguration` static methods to create configurations for IAM, Cognito, JWT, or OAuth authentication |
| `environmentVariables` | `{ [key: string]: string }` | No | Environment variables for the agent runtime. Maximum 50 environment variables |
| `tags` | `{ [key: string]: string }` | No | Tags for the agent runtime. A list of key:value pairs of tags to apply to this Runtime resource |

### Runtime Endpoint Properties

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `endpointName` | `string` | Yes | The name of the runtime endpoint. Valid characters are a-z, A-Z, 0-9, _ (underscore). Must start with a letter and can be up to 48 characters long |
| `agentRuntimeId` | `string` | Yes | The Agent Runtime ID for this endpoint |
| `agentRuntimeVersion` | `string` | Yes | The Agent Runtime version for this endpoint. Must be between 1 and 5 characters long.|
| `description` | `string` | No | Optional description for the runtime endpoint |
| `tags` | `{ [key: string]: string }` | No | Tags for the runtime endpoint |

### Creating a Runtime

#### Option 1: Use an existing image in ECR

Reference an image available within ECR.

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)

# The runtime by default create ECR permission only for the repository available in the account the stack is being deployed
agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")

# Create runtime using the built image
runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact
)
```

To grant the runtime permission to invoke a Bedrock model or inference profile:

```python
# Note: This example uses @aws-cdk/aws-bedrock-alpha which must be installed separately
# runtime: agentcore.Runtime


# Create a cross-region inference profile for Claude 3.7 Sonnet
inference_profile = bedrock.CrossRegionInferenceProfile.from_config(
    geo_region=bedrock.CrossRegionInferenceProfileRegion.US,
    model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_7_SONNET_V1_0
)

# Grant the runtime permission to invoke the inference profile
inference_profile.grant_invoke(runtime)
```

#### Option 2: Use a local asset

Reference a local directory containing a Dockerfile.
Images are built from a local Docker context directory (with a Dockerfile), uploaded to Amazon Elastic Container Registry (ECR)
by the CDK toolkit,and can be naturally referenced in your CDK app .

```python
agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_asset(
    path.join(__dirname, "path to agent dockerfile directory"))

runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact
)
```

### Runtime Versioning

Amazon Bedrock AgentCore automatically manages runtime versioning to ensure safe deployments and rollback capabilities.
When you create an agent runtime, AgentCore automatically creates version 1 (V1). Each subsequent update to the
runtime configuration (such as updating the container image, modifying network settings, or changing protocol configurations)
creates a new immutable version. These versions contain complete, self-contained configurations that can be referenced by endpoints,
allowing you to maintain different versions for different environments or gradually roll out updates.

#### Managing Endpoints and Versions

Amazon Bedrock AgentCore automatically manages runtime versioning to provide safe deployments and rollback capabilities. You can follow
the steps below to understand how to use versioning with runtime for controlled deployments across different environments.

##### Step 1: Initial Deployment

When you first create an agent runtime, AgentCore automatically creates Version 1 of your runtime. At this point, a DEFAULT endpoint is
automatically created that points to Version 1. This DEFAULT endpoint serves as the main access point for your runtime.

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)

runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")
)
```

##### Step 2: Creating Custom Endpoints

After the initial deployment, you can create additional endpoints for different environments. For example, you might create a "production"
endpoint that explicitly points to Version 1. This allows you to maintain stable access points for specific environments while keeping the
flexibility to test newer versions elsewhere.

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)

runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")
)

prod_endpoint = runtime.add_endpoint("production",
    version="1",
    description="Stable production endpoint - pinned to v1"
)
```

##### Step 3: Runtime Update Deployment

When you update the runtime configuration (such as updating the container image, modifying network settings, or changing protocol
configurations), AgentCore automatically creates a new version (Version 2). Upon this update:

* Version 2 is created automatically with the new configuration
* The DEFAULT endpoint automatically updates to point to Version 2
* Any explicitly pinned endpoints (like the production endpoint) remain on their specified versions

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)

agent_runtime_artifact_new = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v2.0.0")

runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact_new
)
```

##### Step 4: Testing with Staging Endpoints

Once Version 2 exists, you can create a staging endpoint that points to the new version. This staging endpoint allows you to test the
new version in a controlled environment before promoting it to production. This separation ensures that production traffic continues
to use the stable version while you validate the new version.

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)

agent_runtime_artifact_new = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v2.0.0")

runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact_new
)

staging_endpoint = runtime.add_endpoint("staging",
    version="2",
    description="Staging environment for testing new version"
)
```

##### Step 5: Promoting to Production

After thoroughly testing the new version through the staging endpoint, you can update the production endpoint to point to Version 2.
This controlled promotion process ensures that you can validate changes before they affect production traffic.

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)

agent_runtime_artifact_new = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v2.0.0")

runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact_new
)

prod_endpoint = runtime.add_endpoint("production",
    version="2",  # New version added here
    description="Stable production endpoint"
)
```

### Creating Standalone Runtime Endpoints

RuntimeEndpoint can also be created as a standalone resource.

#### Example: Creating an endpoint for an existing runtime

```python
# Reference an existing runtime by its ID
existing_runtime_id = "abc123-runtime-id" # The ID of an existing runtime

# Create a standalone endpoint
endpoint = agentcore.RuntimeEndpoint(self, "MyEndpoint",
    endpoint_name="production",
    agent_runtime_id=existing_runtime_id,
    agent_runtime_version="1",  # Specify which version to use
    description="Production endpoint for existing runtime"
)
```

### Runtime Authentication Configuration

The AgentCore Runtime supports multiple authentication modes to secure access to your agent endpoints. Authentication is configured during runtime creation using the `RuntimeAuthorizerConfiguration` class's static factory methods.

#### IAM Authentication (Default)

IAM authentication is the default mode, when no authorizerConfiguration is set then the underlying service use IAM.

#### Cognito Authentication

To configure AWS Cognito User Pool authentication:

```python
# user_pool: cognito.UserPool
# user_pool_client: cognito.UserPoolClient
# another_user_pool_client: cognito.UserPoolClient


repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)
agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")

runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact,
    authorizer_configuration=agentcore.RuntimeAuthorizerConfiguration.using_cognito(user_pool, [user_pool_client, another_user_pool_client])
)
```

#### JWT Authentication

To configure custom JWT authentication with your own OpenID Connect (OIDC) provider:

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)
agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")

runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact,
    authorizer_configuration=agentcore.RuntimeAuthorizerConfiguration.using_jWT("https://example.com/.well-known/openid-configuration", ["client1", "client2"], ["audience1"])
)
```

**Note**: The discovery URL must end with `/.well-known/openid-configuration`.

#### OAuth Authentication

To configure OAuth 2.0 authentication:

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)
agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")

runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact,
    authorizer_configuration=agentcore.RuntimeAuthorizerConfiguration.using_oAuth("https://github.com/.well-known/openid-configuration", "oauth_client_123")
)
```

#### Using a Custom IAM Role

Instead of using the auto-created execution role, you can provide your own IAM role with specific permissions:
The auto-created role includes all necessary baseline permissions for ECR access, CloudWatch logging, and X-Ray tracing. When providing a custom role, ensure these permissions are included.

### Runtime Network Configuration

The AgentCore Runtime supports two network modes for deployment:

#### Public Network Mode (Default)

By default, runtimes are deployed in PUBLIC network mode, which provides internet access suitable for less sensitive or open-use scenarios:

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)
agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")

# Explicitly using public network (this is the default)
runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact,
    network_configuration=agentcore.RuntimeNetworkConfiguration.using_public_network()
)
```

#### VPC Network Mode

For enhanced security and network isolation, you can deploy your runtime within a VPC:

```python
repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)
agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")

# Create or use an existing VPC
vpc = ec2.Vpc(self, "MyVpc",
    max_azs=2
)

# Configure runtime with VPC
runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact,
    network_configuration=agentcore.RuntimeNetworkConfiguration.using_vpc(self,
        vpc=vpc,
        vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
    )
)
```

#### Managing Security Groups with VPC Configuration

When using VPC mode, the Runtime implements `ec2.IConnectable`, allowing you to manage network access using the `connections` property:

```python
vpc = ec2.Vpc(self, "MyVpc",
    max_azs=2
)

repository = ecr.Repository(self, "TestRepository",
    repository_name="test-agent-runtime"
)
agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")

# Create runtime with VPC configuration
runtime = agentcore.Runtime(self, "MyAgentRuntime",
    runtime_name="myAgent",
    agent_runtime_artifact=agent_runtime_artifact,
    network_configuration=agentcore.RuntimeNetworkConfiguration.using_vpc(self,
        vpc=vpc,
        vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
    )
)

# Now you can manage network access using the connections property
# Allow inbound HTTPS traffic from a specific security group
web_server_security_group = ec2.SecurityGroup(self, "WebServerSG", vpc=vpc)
runtime.connections.allow_from(web_server_security_group, ec2.Port.tcp(443), "Allow HTTPS from web servers")

# Allow outbound connections to a database
database_security_group = ec2.SecurityGroup(self, "DatabaseSG", vpc=vpc)
runtime.connections.allow_to(database_security_group, ec2.Port.tcp(5432), "Allow PostgreSQL connection")

# Allow outbound HTTPS to anywhere (for external API calls)
runtime.connections.allow_to_any_ipv4(ec2.Port.tcp(443), "Allow HTTPS outbound")
```

## Browser

The Amazon Bedrock AgentCore Browser provides a secure, cloud-based browser that enables AI agents to interact with websites. It includes security features such as session isolation, built-in observability through live viewing, CloudTrail logging, and session replay capabilities.

Additional information about the browser tool can be found in the [official documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html)

### Browser Network modes

The Browser construct supports the following network modes:

1. **Public Network Mode** (`BrowserNetworkMode.usingPublicNetwork()`) - Default

   * Allows internet access for web browsing and external API calls
   * Suitable for scenarios where agents need to interact with publicly available websites
   * Enables full web browsing capabilities
   * VPC mode is not supported with this option
2. **VPC (Virtual Private Cloud)** (`BrowserNetworkMode.usingVpc()`)

   * Select whether to run the browser in a virtual private cloud (VPC).
   * By configuring VPC connectivity, you enable secure access to private resources such as databases, internal APIs, and services within your VPC.

   While the VPC itself is mandatory, these are optional:

   * Subnets - if not provided, CDK will select appropriate subnets from the VPC
   * Security Groups - if not provided, CDK will create a default security group
   * Specific subnet selection criteria - you can let CDK choose automatically

For more information on VPC connectivity for Amazon Bedrock AgentCore Browser, please refer to the [official documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-vpc.html).

### Browser Properties

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `browserCustomName` | `string` | Yes | The name of the browser. Must start with a letter and can be up to 48 characters long. Pattern: `[a-zA-Z][a-zA-Z0-9_]{0,47}` |
| `description` | `string` | No | Optional description for the browser. Can have up to 200 characters |
| `networkConfiguration` | `BrowserNetworkConfiguration` | No | Network configuration for browser. Defaults to PUBLIC network mode |
| `recordingConfig` | `RecordingConfig` | No | Recording configuration for browser. Defaults to no recording |
| `executionRole` | `iam.IRole` | No | The IAM role that provides permissions for the browser to access AWS services. A new role will be created if not provided |
| `tags` | `{ [key: string]: string }` | No | Tags to apply to the browser resource |

### Basic Browser Creation

```python
# Create a basic browser with public network access
browser = agentcore.BrowserCustom(self, "MyBrowser",
    browser_custom_name="my_browser",
    description="A browser for web automation"
)
```

### Browser with Tags

```python
# Create a browser with custom tags
browser = agentcore.BrowserCustom(self, "MyBrowser",
    browser_custom_name="my_browser",
    description="A browser for web automation with tags",
    network_configuration=agentcore.BrowserNetworkConfiguration.using_public_network(),
    tags={
        "Environment": "Production",
        "Team": "AI/ML",
        "Project": "AgentCore"
    }
)
```

### Browser with VPC

```python
browser = agentcore.BrowserCustom(self, "BrowserVpcWithRecording",
    browser_custom_name="browser_recording",
    network_configuration=agentcore.BrowserNetworkConfiguration.using_vpc(self,
        vpc=ec2.Vpc(self, "VPC", restrict_default_security_group=False)
    )
)
```

Browser exposes a [connections](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Connections.html) property. This property returns a connections object, which simplifies the process of defining and managing ingress and egress rules for security groups in your AWS CDK applications. Instead of directly manipulating security group rules, you interact with the Connections object of a construct, which then translates your connectivity requirements into the appropriate security group rules. For instance:

```python
vpc = ec2.Vpc(self, "testVPC")

browser = agentcore.BrowserCustom(self, "test-browser",
    browser_custom_name="test_browser",
    network_configuration=agentcore.BrowserNetworkConfiguration.using_vpc(self,
        vpc=vpc
    )
)

browser.connections.add_security_group(ec2.SecurityGroup(self, "AdditionalGroup", vpc=vpc))
```

So security groups can be added after the browser construct creation. You can use methods like allowFrom() and allowTo() to grant ingress access to/egress access from a specified peer over a given portRange. The Connections object automatically adds the necessary ingress or egress rules to the security group(s) associated with the calling construct.

### Browser with Recording Configuration

```python
# Create an S3 bucket for recordings
recording_bucket = s3.Bucket(self, "RecordingBucket",
    bucket_name="my-browser-recordings",
    removal_policy=RemovalPolicy.DESTROY
)

# Create browser with recording enabled
browser = agentcore.BrowserCustom(self, "MyBrowser",
    browser_custom_name="my_browser",
    description="Browser with recording enabled",
    network_configuration=agentcore.BrowserNetworkConfiguration.using_public_network(),
    recording_config=agentcore.RecordingConfig(
        enabled=True,
        s3_location=s3.Location(
            bucket_name=recording_bucket.bucket_name,
            object_key="browser-recordings/"
        )
    )
)
```

### Browser with Custom Execution Role

```python
# Create a custom execution role
execution_role = iam.Role(self, "BrowserExecutionRole",
    assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
    managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockAgentCoreBrowserExecutionRolePolicy")
    ]
)

# Create browser with custom execution role
browser = agentcore.BrowserCustom(self, "MyBrowser",
    browser_custom_name="my_browser",
    description="Browser with custom execution role",
    network_configuration=agentcore.BrowserNetworkConfiguration.using_public_network(),
    execution_role=execution_role
)
```

### Browser with S3 Recording and Permissions

```python
# Create an S3 bucket for recordings
recording_bucket = s3.Bucket(self, "RecordingBucket",
    bucket_name="my-browser-recordings",
    removal_policy=RemovalPolicy.DESTROY
)

# Create browser with recording enabled
browser = agentcore.BrowserCustom(self, "MyBrowser",
    browser_custom_name="my_browser",
    description="Browser with recording enabled",
    network_configuration=agentcore.BrowserNetworkConfiguration.using_public_network(),
    recording_config=agentcore.RecordingConfig(
        enabled=True,
        s3_location=s3.Location(
            bucket_name=recording_bucket.bucket_name,
            object_key="browser-recordings/"
        )
    )
)
```

### Browser IAM Permissions

The Browser construct provides convenient methods for granting IAM permissions:

```python
# Create a browser
browser = agentcore.BrowserCustom(self, "MyBrowser",
    browser_custom_name="my_browser",
    description="Browser for web automation",
    network_configuration=agentcore.BrowserNetworkConfiguration.using_public_network()
)

# Create a role that needs access to the browser
user_role = iam.Role(self, "UserRole",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)

# Grant read permissions (Get and List actions)
browser.grant_read(user_role)

# Grant use permissions (Start, Update, Stop actions)
browser.grant_use(user_role)

# Grant specific custom permissions
browser.grant(user_role, "bedrock-agentcore:GetBrowserSession")
```

## Code Interpreter

The Amazon Bedrock AgentCore Code Interpreter enables AI agents to write and execute code securely in sandbox environments, enhancing their accuracy and expanding their ability to solve complex end-to-end tasks. This is critical in Agentic AI applications where the agents may execute arbitrary code that can lead to data compromise or security risks. The AgentCore Code Interpreter tool provides secure code execution, which helps you avoid running into these issues.

For more information about code interpreter, please refer to the [official documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-tool.html)

### Code Interpreter Network Modes

The Code Interpreter construct supports the following network modes:

1. **Public Network Mode** (`CodeInterpreterNetworkMode.usingPublicNetwork()`) - Default

   * Allows internet access for package installation and external API calls
   * Suitable for development and testing environments
   * Enables downloading Python packages from PyPI
2. **Sandbox Network Mode** (`CodeInterpreterNetworkMode.usingSandboxNetwork()`)

   * Isolated network environment with no internet access
   * Suitable for production environments with strict security requirements
   * Only allows access to pre-installed packages and local resources
3. **VPC (Virtual Private Cloud)** (`CodeInterpreterNetworkMode.usingVpc()`)

   * Select whether to run the browser in a virtual private cloud (VPC).
   * By configuring VPC connectivity, you enable secure access to private resources such as databases, internal APIs, and services within your VPC.

   While the VPC itself is mandatory, these are optional:

   * Subnets - if not provided, CDK will select appropriate subnets from the VPC
   * Security Groups - if not provided, CDK will create a default security group
   * Specific subnet selection criteria - you can let CDK choose automatically

For more information on VPC connectivity for Amazon Bedrock AgentCore Browser, please refer to the [official documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-vpc.html).

### Code Interpreter Properties

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `codeInterpreterCustomName` | `string` | Yes | The name of the code interpreter. Must start with a letter and can be up to 48 characters long. Pattern: `[a-zA-Z][a-zA-Z0-9_]{0,47}` |
| `description` | `string` | No | Optional description for the code interpreter. Can have up to 200 characters |
| `executionRole` | `iam.IRole` | No | The IAM role that provides permissions for the code interpreter to access AWS services. A new role will be created if not provided |
| `networkConfiguration` | `CodeInterpreterNetworkConfiguration` | No | Network configuration for code interpreter. Defaults to PUBLIC network mode |
| `tags` | `{ [key: string]: string }` | No | Tags to apply to the code interpreter resource |

### Basic Code Interpreter Creation

```python
# Create a basic code interpreter with public network access
code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
    code_interpreter_custom_name="my_code_interpreter",
    description="A code interpreter for Python execution"
)
```

### Code Interpreter with VPC

```python
code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
    code_interpreter_custom_name="my_sandbox_interpreter",
    description="Code interpreter with isolated network access",
    network_configuration=agentcore.BrowserNetworkConfiguration.using_vpc(self,
        vpc=ec2.Vpc(self, "VPC", restrict_default_security_group=False)
    )
)
```

Code Interpreter exposes a [connections](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_ec2.Connections.html) property. This property returns a connections object, which simplifies the process of defining and managing ingress and egress rules for security groups in your AWS CDK applications. Instead of directly manipulating security group rules, you interact with the Connections object of a construct, which then translates your connectivity requirements into the appropriate security group rules. For instance:

```python
vpc = ec2.Vpc(self, "testVPC")

code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
    code_interpreter_custom_name="my_sandbox_interpreter",
    description="Code interpreter with isolated network access",
    network_configuration=agentcore.BrowserNetworkConfiguration.using_vpc(self,
        vpc=vpc
    )
)

code_interpreter.connections.add_security_group(ec2.SecurityGroup(self, "AdditionalGroup", vpc=vpc))
```

So security groups can be added after the browser construct creation. You can use methods like allowFrom() and allowTo() to grant ingress access to/egress access from a specified peer over a given portRange. The Connections object automatically adds the necessary ingress or egress rules to the security group(s) associated with the calling construct.

### Code Interpreter with Sandbox Network Mode

```python
# Create code interpreter with sandbox network mode (isolated)
code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
    code_interpreter_custom_name="my_sandbox_interpreter",
    description="Code interpreter with isolated network access",
    network_configuration=agentcore.CodeInterpreterNetworkConfiguration.using_sandbox_network()
)
```

### Code Interpreter with Custom Execution Role

```python
# Create a custom execution role
execution_role = iam.Role(self, "CodeInterpreterExecutionRole",
    assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com")
)

# Create code interpreter with custom execution role
code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
    code_interpreter_custom_name="my_code_interpreter",
    description="Code interpreter with custom execution role",
    network_configuration=agentcore.CodeInterpreterNetworkConfiguration.using_public_network(),
    execution_role=execution_role
)
```

### Code Interpreter IAM Permissions

The Code Interpreter construct provides convenient methods for granting IAM permissions:

```python
# Create a code interpreter
code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
    code_interpreter_custom_name="my_code_interpreter",
    description="Code interpreter for Python execution",
    network_configuration=agentcore.CodeInterpreterNetworkConfiguration.using_public_network()
)

# Create a role that needs access to the code interpreter
user_role = iam.Role(self, "UserRole",
    assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
)

# Grant read permissions (Get and List actions)
code_interpreter.grant_read(user_role)

# Grant use permissions (Start, Invoke, Stop actions)
code_interpreter.grant_use(user_role)

# Grant specific custom permissions
code_interpreter.grant(user_role, "bedrock-agentcore:GetCodeInterpreterSession")
```

### Code interpreter with tags

```python
# Create code interpreter with sandbox network mode (isolated)
code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
    code_interpreter_custom_name="my_sandbox_interpreter",
    description="Code interpreter with isolated network access",
    network_configuration=agentcore.CodeInterpreterNetworkConfiguration.using_public_network(),
    tags={
        "Environment": "Production",
        "Team": "AI/ML",
        "Project": "AgentCore"
    }
)
```

## Memory

Memory is a critical component of intelligence. While Large Language Models (LLMs) have impressive capabilities, they lack persistent memory across conversations. Amazon Bedrock AgentCore Memory addresses this limitation by providing a managed service that enables AI agents to maintain context over time, remember important facts, and deliver consistent, personalized experiences.

AgentCore Memory operates on two levels:

* **Short-Term Memory**: Immediate conversation context and session-based information that provides continuity within a single interaction or closely related sessions.
* **Long-Term Memory**: Persistent information extracted and stored across multiple conversations, including facts, preferences, and summaries that enable personalized experiences over time.

When you interact with the memory via the `CreateEvent` API, you store interactions in Short-Term Memory (STM) instantly. These interactions can include everything from user messages, assistant responses, to tool actions.

To write to long-term memory, you need to configure extraction strategies which define how and where to store information from conversations for future use. These strategies are asynchronously processed from raw events after every few turns based on the strategy that was selected. You can't create long term memory records directly, as they are extracted asynchronously by AgentCore Memory.

### Memory Properties

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `memoryName` | `string` | Yes | The name of the memory |
| `expirationDuration` | `Duration` | No | Short-term memory expiration in days (between 7 and 365). Default: 90 days |
| `description` | `string` | No | Optional description for the memory. Default: no description. |
| `kmsKey` | `IKey` | No | Custom KMS key to use for encryption. Default: Your data is encrypted with a key that AWS owns and manages for you |
| `memoryStrategies` | `MemoryStrategyBase[]` | No | Built-in extraction strategies to use for this memory. Default: No extraction strategies (short term memory only) |
| `executionRole` | `iam.IRole` | No | The IAM role that provides permissions for the memory to access AWS services. Default: A new role will be created. |
| `tags` | `{ [key: string]: string }` | No | Tags for memory. Default: no tags. |

### Basic Memory Creation

Below you can find how to configure a simple short-term memory (STM) with no long-term memory extraction strategies.
Note how you set `expirationDuration`, which defines the time the events will be stored in the short-term memory before they expire.

```python
# Create a basic memory with default settings, no LTM strategies
memory = agentcore.Memory(self, "MyMemory",
    memory_name="my_memory",
    description="A memory for storing user interactions for a period of 90 days",
    expiration_duration=cdk.Duration.days(90)
)
```

Basic Memory with Custom KMS Encryption

```python
# Create a custom KMS key for encryption
encryption_key = kms.Key(self, "MemoryEncryptionKey",
    enable_key_rotation=True,
    description="KMS key for memory encryption"
)

# Create memory with custom encryption
memory = agentcore.Memory(self, "MyMemory",
    memory_name="my_encrypted_memory",
    description="Memory with custom KMS encryption",
    expiration_duration=cdk.Duration.days(90),
    kms_key=encryption_key
)
```

### LTM Memory Extraction Stategies

If you need long-term memory for context recall across sessions, you can setup memory extraction strategies
to extract the relevant memory from the raw events.

Amazon Bedrock AgentCore Memory has different memory strategies for extracting and organizing information:

* **Summarization**: to summarize interactions to preserve critical context and key insights.
* **Semantic Memory**: to extract general factual knowledge, concepts and meanings from raw conversations using vector embeddings.
  This enables similarity-based retrieval of relevant facts and context.
* **User Preferences**: to extract user behavior patterns from raw conversations.

You can use built-in extraction strategies for quick setup, or create custom extraction strategies with specific models and prompt templates.

### Memory with Built-in Strategies

The library provides three built-in LTM strategies. These are default strategies for organizing and extracting memory data,
each optimized for specific use cases.

For example: An agent helps multiple users with cloud storage setup. From these conversations,
see how each strategy processes users expressing confusion about account connection:

1. **Summarization Strategy** (`MemoryStrategy.usingBuiltInSummarization()`)
   This strategy compresses conversations into concise overviews, preserving essential context and key insights for quick recall.
   Extracted memory example: Users confused by cloud setup during onboarding.

   * Extracts concise summaries to preserve critical context and key insights
   * Namespace: `/strategies/{memoryStrategyId}/actors/{actorId}/sessions/{sessionId}`
2. **Semantic Memory Strategy** (`MemoryStrategy.usingBuiltInSemantic()`)
   Distills general facts, concepts, and underlying meanings from raw conversational data, presenting the information in a context-independent format.
   Extracted memory example: In-context learning = task-solving via examples, no training needed.

   * Extracts general factual knowledge, concepts and meanings from raw conversations
   * Namespace: `/strategies/{memoryStrategyId}/actors/{actorId}`
3. **User Preference Strategy** (`MemoryStrategy.usingBuiltInUserPreference()`)
   Captures individual preferences, interaction patterns, and personalized settings to enhance future experiences.
   Extracted memory example: User needs clear guidance on cloud storage account connection during onboarding.

   * Extracts user behavior patterns from raw conversations
   * Namespace: `/strategies/{memoryStrategyId}/actors/{actorId}`

```python
# Create memory with built-in strategies
memory = agentcore.Memory(self, "MyMemory",
    memory_name="my_memory",
    description="Memory with built-in strategies",
    expiration_duration=cdk.Duration.days(90),
    memory_strategies=[
        agentcore.MemoryStrategy.using_built_in_summarization(),
        agentcore.MemoryStrategy.using_built_in_semantic(),
        agentcore.MemoryStrategy.using_built_in_user_preference()
    ]
)
```

The name generated for each built in memory strategy is as follows:

* For Summarization: `summary_builtin_cdk001`
* For Semantic:`semantic_builtin_cdk001>`
* For User Preferences: `preference_builtin_cdk001`

### Memory with custom Strategies

With Long-Term Memory, organization is managed through Namespaces.

An `actor` refers to entity such as end users or agent/user combinations. For example, in a coding support chatbot,
the actor is usually the developer asking questions. Using the actor ID helps the system know which user the memory belongs to,
keeping each user's data separate and organized.

A `session` is usually a single conversation or interaction period between the user and the AI agent.
It groups all related messages and events that happen during that conversation.

A `namespace` is used to logically group and organize long-term memories. It ensures data stays neat, separate, and secure.

With AgentCore Memory, you need to add a namespace when you define a memory strategy. This namespace helps define where the long-term memory
will be logically grouped. Every time a new long-term memory is extracted using this memory strategy, it is saved under the namespace you set.
This means that all long-term memories are scoped to their specific namespace, keeping them organized and preventing any mix-ups with other
users or sessions. You should use a hierarchical format separated by forward slashes /. This helps keep memories organized clearly. As needed,
you can choose to use the below pre-defined variables within braces in the namespace based on your applications' organization needs:

* `actorId` – Identifies who the long-term memory belongs to, such as a user
* `memoryStrategyId` – Shows which memory strategy is being used. This strategy identifier is auto-generated when you create a memory using CreateMemory operation.
* `sessionId` – Identifies which session or conversation the memory is from.

For example, if you define the following namespace as the input to your strategy in CreateMemory operation:

```shell
/strategy/{memoryStrategyId}/actor/{actorId}/session/{sessionId}
```

After memory creation, this namespace might look like:

```shell
/strategy/summarization-93483043//actor/actor-9830m2w3/session/session-9330sds8
```

You can customise the namespace, i.e. where the memories are stored by using the following methods:

1. **Summarization Strategy** (`MemoryStrategy.usingSummarization(props)`)
2. **Semantic Memory Strategy** (`MemoryStrategy.usingSemantic(props)`)
3. **User Preference Strategy** (`MemoryStrategy.usingUserPreference(props)`)

```python
# Create memory with built-in strategies
memory = agentcore.Memory(self, "MyMemory",
    memory_name="my_memory",
    description="Memory with built-in strategies",
    expiration_duration=cdk.Duration.days(90),
    memory_strategies=[
        agentcore.MemoryStrategy.using_user_preference(
            name="CustomerPreferences",
            namespaces=["support/customer/{actorId}/preferences"]
        ),
        agentcore.MemoryStrategy.using_semantic(
            name="CustomerSupportSemantic",
            namespaces=["support/customer/{actorId}/semantic"]
        )
    ]
)
```

Custom memory strategies let you tailor memory extraction and consolidation to your specific domain or use case.
You can override the prompts for extracting and consolidating semantic, summary, or user preferences.
You can also choose the model that you want to use for extraction and consolidation.

The custom prompts you create are appended to a non-editable system prompt.

Since a custom strategy requires you to invoke certain FMs, you need a role with appropriate permissions. For that, you can:

* Let the L2 construct create a minimum permission role for you when use L2 Bedrock Foundation Models.
* Use a custom role with the overly permissive `AmazonBedrockAgentCoreMemoryBedrockModelInferenceExecutionRolePolicy` managed policy.
* Use a custom role with your own custom policies.

#### Memory with Custom Execution Role

Keep in mind that memories that **do not** use custom strategies do not require a service role.
So even if you provide it, it will be ignored as it will never be used.

```python
# Create a custom execution role
execution_role = iam.Role(self, "MemoryExecutionRole",
    assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
    managed_policies=[
        iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockAgentCoreMemoryBedrockModelInferenceExecutionRolePolicy")
    ]
)

# Create memory with custom execution role
memory = agentcore.Memory(self, "MyMemory",
    memory_name="my_memory",
    description="Memory with custom execution role",
    expiration_duration=cdk.Duration.days(90),
    execution_role=execution_role
)
```

In customConsolidation and customExtraction, the model property uses the [@aws-cdk/aws-bedrock-alph](https://www.npmjs.com/package/@aws-cdk/aws-bedrock-alpha) library which must be installed separately.

```python
# Create a custom semantic memory strategy
custom_semantic_strategy = agentcore.MemoryStrategy.using_semantic(
    name="customSemanticStrategy",
    description="Custom semantic memory strategy",
    namespaces=["/custom/strategies/{memoryStrategyId}/actors/{actorId}"],
    custom_consolidation=agentcore.OverrideConfig(
        model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
        append_to_prompt="Custom consolidation prompt for semantic memory"
    ),
    custom_extraction=agentcore.OverrideConfig(
        model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
        append_to_prompt="Custom extraction prompt for semantic memory"
    )
)

# Create memory with custom strategy
memory = agentcore.Memory(self, "MyMemory",
    memory_name="my-custom-memory",
    description="Memory with custom strategy",
    expiration_duration=cdk.Duration.days(90),
    memory_strategies=[custom_semantic_strategy]
)
```

### Memory with self-managed Strategies

A self-managed strategy in Amazon Bedrock AgentCore Memory gives you complete control over your memory extraction and consolidation pipelines.
With a self-managed strategy, you can build custom memory processing workflows while leveraging Amazon Bedrock AgentCore for storage and retrieval.

For additional information, you can refer to the [developer guide for self managed strategies](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-self-managed-strategies.html).

Create the required AWS resources including:

* an S3 bucket in your account where Amazon Bedrock AgentCore will deliver batched event payloads.
* an SNS topic for job notifications. Use FIFO topics if processing order within sessions is important for your use case.

The construct will apply the correct permissions to the memory execution role to access these resources.

```python
bucket = s3.Bucket(self, "memoryBucket",
    bucket_name="test-memory",
    removal_policy=cdk.RemovalPolicy.DESTROY,
    auto_delete_objects=True
)

topic = sns.Topic(self, "topic")

# Create a custom semantic memory strategy
self_managed_strategy = agentcore.MemoryStrategy.using_self_managed(
    name="selfManagedStrategy",
    description="self managed memory strategy",
    historical_context_window_size=5,
    invocation_configuration=agentcore.InvocationConfiguration(
        topic=topic,
        s3_location=s3.Location(
            bucket_name=bucket.bucket_name,
            object_key="memory/"
        )
    ),
    trigger_conditions=agentcore.TriggerConditions(
        message_based_trigger=1,
        time_based_trigger=cdk.Duration.seconds(10),
        token_based_trigger=100
    )
)

# Create memory with custom strategy
memory = agentcore.Memory(self, "MyMemory",
    memory_name="my-custom-memory",
    description="Memory with custom strategy",
    expiration_duration=cdk.Duration.days(90),
    memory_strategies=[self_managed_strategy]
)
```

### Memory Strategy Methods

You can add new memory strategies to the memory construct using the `addMemoryStrategy()` method, for instance:

```python
# Create memory without initial strategies
memory = agentcore.Memory(self, "test-memory",
    memory_name="test_memory_add_strategy",
    description="A test memory for testing addMemoryStrategy method",
    expiration_duration=cdk.Duration.days(90)
)

# Add strategies after instantiation
memory.add_memory_strategy(agentcore.MemoryStrategy.using_built_in_summarization())
memory.add_memory_strategy(agentcore.MemoryStrategy.using_built_in_semantic())
```
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

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_bedrock_alpha as _aws_cdk_aws_bedrock_alpha_3753ded9
import aws_cdk.aws_bedrockagentcore as _aws_cdk_aws_bedrockagentcore_ceddda9d
import aws_cdk.aws_cloudwatch as _aws_cdk_aws_cloudwatch_ceddda9d
import aws_cdk.aws_cognito as _aws_cdk_aws_cognito_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecr as _aws_cdk_aws_ecr_ceddda9d
import aws_cdk.aws_ecr_assets as _aws_cdk_aws_ecr_assets_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_sns as _aws_cdk_aws_sns_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.AddEndpointOptions",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "version": "version"},
)
class AddEndpointOptions:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Options for adding an endpoint to the runtime.

        :param description: (experimental) Description for the endpoint, Must be between 1 and 1200 characters. Default: - No description
        :param version: (experimental) Override the runtime version for this endpoint. Default: 1

        :stability: experimental
        :exampleMetadata: infused

        Example::

            repository = ecr.Repository(self, "TestRepository",
                repository_name="test-agent-runtime"
            )
            
            agent_runtime_artifact_new = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v2.0.0")
            
            runtime = agentcore.Runtime(self, "MyAgentRuntime",
                runtime_name="myAgent",
                agent_runtime_artifact=agent_runtime_artifact_new
            )
            
            staging_endpoint = runtime.add_endpoint("staging",
                version="2",
                description="Staging environment for testing new version"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__175b1aee490f549cb19d8945b728786765752ce863f0a55d8732e6f777128e9b)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Description for the endpoint, Must be between 1 and 1200 characters.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''(experimental) Override the runtime version for this endpoint.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AddEndpointOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AgentRuntimeArtifact(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.AgentRuntimeArtifact",
):
    '''(experimental) Abstract base class for agent runtime artifacts.

    Provides methods to reference container images from ECR repositories or local assets.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        repository = ecr.Repository(self, "TestRepository",
            repository_name="test-agent-runtime"
        )
        agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")
        
        runtime = agentcore.Runtime(self, "MyAgentRuntime",
            runtime_name="myAgent",
            agent_runtime_artifact=agent_runtime_artifact,
            authorizer_configuration=agentcore.RuntimeAuthorizerConfiguration.using_oAuth("https://github.com/.well-known/openid-configuration", "oauth_client_123")
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="fromAsset")
    @builtins.classmethod
    def from_asset(
        cls,
        directory: builtins.str,
        *,
        asset_name: typing.Optional[builtins.str] = None,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        build_secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        build_ssh: typing.Optional[builtins.str] = None,
        cache_disabled: typing.Optional[builtins.bool] = None,
        cache_from: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]]] = None,
        cache_to: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]] = None,
        display_name: typing.Optional[builtins.str] = None,
        file: typing.Optional[builtins.str] = None,
        invalidation: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerImageAssetInvalidationOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        network_mode: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.NetworkMode] = None,
        outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
        platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
        target: typing.Optional[builtins.str] = None,
        extra_hash: typing.Optional[builtins.str] = None,
        exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
        follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
        ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
    ) -> "AgentRuntimeArtifact":
        '''(experimental) Reference an agent runtime artifact that's constructed directly from sources on disk.

        :param directory: The directory where the Dockerfile is stored.
        :param asset_name: Unique identifier of the docker image asset and its potential revisions. Required if using AppScopedStagingSynthesizer. Default: - no asset name
        :param build_args: Build args to pass to the ``docker build`` command. Since Docker build arguments are resolved before deployment, keys and values cannot refer to unresolved tokens (such as ``lambda.functionArn`` or ``queue.queueUrl``). Default: - no build args are passed
        :param build_secrets: Build secrets. Docker BuildKit must be enabled to use build secrets. Default: - no build secrets
        :param build_ssh: SSH agent socket or keys to pass to the ``docker build`` command. Docker BuildKit must be enabled to use the ssh flag Default: - no --ssh flag
        :param cache_disabled: Disable the cache and pass ``--no-cache`` to the ``docker build`` command. Default: - cache is used
        :param cache_from: Cache from options to pass to the ``docker build`` command. Default: - no cache from options are passed to the build command
        :param cache_to: Cache to options to pass to the ``docker build`` command. Default: - no cache to options are passed to the build command
        :param display_name: A display name for this asset. If supplied, the display name will be used in locations where the asset identifier is printed, like in the CLI progress information. If the same asset is added multiple times, the display name of the first occurrence is used. If ``assetName`` is given, it will also be used as the default ``displayName``. Otherwise, the default is the construct path of the ImageAsset construct, with respect to the enclosing stack. If the asset is produced by a construct helper function (such as ``lambda.Code.fromAssetImage()``), this will look like ``MyFunction/AssetImage``. We use the stack-relative construct path so that in the common case where you have multiple stacks with the same asset, we won't show something like ``/MyBetaStack/MyFunction/Code`` when you are actually deploying to production. Default: - Stack-relative construct path
        :param file: Path to the Dockerfile (relative to the directory). Default: 'Dockerfile'
        :param invalidation: Options to control which parameters are used to invalidate the asset hash. Default: - hash all parameters
        :param network_mode: Networking mode for the RUN commands during build. Support docker API 1.25+. Default: - no networking mode specified (the default networking mode ``NetworkMode.DEFAULT`` will be used)
        :param outputs: Outputs to pass to the ``docker build`` command. Default: - no outputs are passed to the build command (default outputs are used)
        :param platform: Platform to build for. *Requires Docker Buildx*. Default: - no platform specified (the current machine architecture will be used)
        :param target: Docker target to build to. Default: - no target
        :param extra_hash: Extra information to encode into the fingerprint (e.g. build instructions and other inputs). Default: - hash is only based on source content
        :param exclude: File paths matching the patterns will be excluded. See ``ignoreMode`` to set the matching behavior. Has no effect on Assets bundled using the ``bundling`` property. Default: - nothing is excluded
        :param follow_symlinks: A strategy for how to handle symlinks. Default: SymlinkFollowMode.NEVER
        :param ignore_mode: The ignore behavior to use for ``exclude`` patterns. Default: IgnoreMode.GLOB

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__604d365a86a290247af7992e6be98b47b27307a51f5ffdb436c6c1ea4019453a)
            check_type(argname="argument directory", value=directory, expected_type=type_hints["directory"])
        options = _aws_cdk_aws_ecr_assets_ceddda9d.DockerImageAssetOptions(
            asset_name=asset_name,
            build_args=build_args,
            build_secrets=build_secrets,
            build_ssh=build_ssh,
            cache_disabled=cache_disabled,
            cache_from=cache_from,
            cache_to=cache_to,
            display_name=display_name,
            file=file,
            invalidation=invalidation,
            network_mode=network_mode,
            outputs=outputs,
            platform=platform,
            target=target,
            extra_hash=extra_hash,
            exclude=exclude,
            follow_symlinks=follow_symlinks,
            ignore_mode=ignore_mode,
        )

        return typing.cast("AgentRuntimeArtifact", jsii.sinvoke(cls, "fromAsset", [directory, options]))

    @jsii.member(jsii_name="fromEcrRepository")
    @builtins.classmethod
    def from_ecr_repository(
        cls,
        repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
        tag: typing.Optional[builtins.str] = None,
    ) -> "AgentRuntimeArtifact":
        '''(experimental) Reference an image in an ECR repository.

        :param repository: -
        :param tag: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5378ad450d2e50130983bd4e4c0d41f7ddc7b25ef75b63e107cdace81383db49)
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
            check_type(argname="argument tag", value=tag, expected_type=type_hints["tag"])
        return typing.cast("AgentRuntimeArtifact", jsii.sinvoke(cls, "fromEcrRepository", [repository, tag]))

    @jsii.member(jsii_name="bind")
    @abc.abstractmethod
    def bind(self, scope: _constructs_77d1e7e8.Construct, runtime: "Runtime") -> None:
        '''(experimental) Called when the image is used by a Runtime to handle side effects like permissions.

        :param scope: -
        :param runtime: -

        :stability: experimental
        '''
        ...


class _AgentRuntimeArtifactProxy(AgentRuntimeArtifact):
    @jsii.member(jsii_name="bind")
    def bind(self, scope: _constructs_77d1e7e8.Construct, runtime: "Runtime") -> None:
        '''(experimental) Called when the image is used by a Runtime to handle side effects like permissions.

        :param scope: -
        :param runtime: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bedccb351eb2d100e954ac8354c709d22031237b55a8c9439b4fa56a9c488298)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument runtime", value=runtime, expected_type=type_hints["runtime"])
        return typing.cast(None, jsii.invoke(self, "bind", [scope, runtime]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, AgentRuntimeArtifact).__jsii_proxy_class__ = lambda : _AgentRuntimeArtifactProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.AgentRuntimeAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "agent_runtime_arn": "agentRuntimeArn",
        "agent_runtime_id": "agentRuntimeId",
        "agent_runtime_name": "agentRuntimeName",
        "role_arn": "roleArn",
        "agent_runtime_version": "agentRuntimeVersion",
        "agent_status": "agentStatus",
        "created_at": "createdAt",
        "description": "description",
        "last_updated_at": "lastUpdatedAt",
        "security_groups": "securityGroups",
    },
)
class AgentRuntimeAttributes:
    def __init__(
        self,
        *,
        agent_runtime_arn: builtins.str,
        agent_runtime_id: builtins.str,
        agent_runtime_name: builtins.str,
        role_arn: builtins.str,
        agent_runtime_version: typing.Optional[builtins.str] = None,
        agent_status: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        last_updated_at: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    ) -> None:
        '''(experimental) Attributes for importing an existing Agent Runtime.

        :param agent_runtime_arn: (experimental) The ARN of the agent runtime.
        :param agent_runtime_id: (experimental) The ID of the agent runtime.
        :param agent_runtime_name: (experimental) The name of the agent runtime.
        :param role_arn: (experimental) The IAM role ARN.
        :param agent_runtime_version: (experimental) The version of the agent runtime When importing a runtime and this is not specified or undefined, endpoints created on this runtime will point to version "1" unless explicitly overridden. Default: - undefined
        :param agent_status: (experimental) The current status of the agent runtime. Default: - Status not available
        :param created_at: (experimental) The time at which the runtime was created. Default: - Creation time not available
        :param description: (experimental) The description of the agent runtime. Default: - No description
        :param last_updated_at: (experimental) The time at which the runtime was last updated. Default: - Last update time not available
        :param security_groups: (experimental) The security groups for this runtime, if in a VPC. Default: - By default, the runtime is not in a VPC.

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_bedrock_agentcore_alpha as bedrock_agentcore_alpha
            from aws_cdk import aws_ec2 as ec2
            
            # security_group: ec2.SecurityGroup
            
            agent_runtime_attributes = bedrock_agentcore_alpha.AgentRuntimeAttributes(
                agent_runtime_arn="agentRuntimeArn",
                agent_runtime_id="agentRuntimeId",
                agent_runtime_name="agentRuntimeName",
                role_arn="roleArn",
            
                # the properties below are optional
                agent_runtime_version="agentRuntimeVersion",
                agent_status="agentStatus",
                created_at="createdAt",
                description="description",
                last_updated_at="lastUpdatedAt",
                security_groups=[security_group]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__521eb5a43c1809da91e6b913f83fa6446f5b8ac2c440a565fa2764b3cd9f4ad8)
            check_type(argname="argument agent_runtime_arn", value=agent_runtime_arn, expected_type=type_hints["agent_runtime_arn"])
            check_type(argname="argument agent_runtime_id", value=agent_runtime_id, expected_type=type_hints["agent_runtime_id"])
            check_type(argname="argument agent_runtime_name", value=agent_runtime_name, expected_type=type_hints["agent_runtime_name"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument agent_runtime_version", value=agent_runtime_version, expected_type=type_hints["agent_runtime_version"])
            check_type(argname="argument agent_status", value=agent_status, expected_type=type_hints["agent_status"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument last_updated_at", value=last_updated_at, expected_type=type_hints["last_updated_at"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "agent_runtime_arn": agent_runtime_arn,
            "agent_runtime_id": agent_runtime_id,
            "agent_runtime_name": agent_runtime_name,
            "role_arn": role_arn,
        }
        if agent_runtime_version is not None:
            self._values["agent_runtime_version"] = agent_runtime_version
        if agent_status is not None:
            self._values["agent_status"] = agent_status
        if created_at is not None:
            self._values["created_at"] = created_at
        if description is not None:
            self._values["description"] = description
        if last_updated_at is not None:
            self._values["last_updated_at"] = last_updated_at
        if security_groups is not None:
            self._values["security_groups"] = security_groups

    @builtins.property
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent runtime.

        :stability: experimental
        '''
        result = self._values.get("agent_runtime_arn")
        assert result is not None, "Required property 'agent_runtime_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_runtime_id(self) -> builtins.str:
        '''(experimental) The ID of the agent runtime.

        :stability: experimental
        '''
        result = self._values.get("agent_runtime_id")
        assert result is not None, "Required property 'agent_runtime_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_runtime_name(self) -> builtins.str:
        '''(experimental) The name of the agent runtime.

        :stability: experimental
        '''
        result = self._values.get("agent_runtime_name")
        assert result is not None, "Required property 'agent_runtime_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''(experimental) The IAM role ARN.

        :stability: experimental
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_runtime_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of the agent runtime When importing a runtime and this is not specified or undefined, endpoints created on this runtime will point to version "1" unless explicitly overridden.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("agent_runtime_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def agent_status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the agent runtime.

        :default: - Status not available

        :stability: experimental
        '''
        result = self._values.get("agent_status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was created.

        :default: - Creation time not available

        :stability: experimental
        '''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the agent runtime.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was last updated.

        :default: - Last update time not available

        :stability: experimental
        '''
        result = self._values.get("last_updated_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) The security groups for this runtime, if in a VPC.

        :default: - By default, the runtime is not in a VPC.

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AgentRuntimeAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.BrowserCustomAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "browser_arn": "browserArn",
        "role_arn": "roleArn",
        "created_at": "createdAt",
        "last_updated_at": "lastUpdatedAt",
        "security_groups": "securityGroups",
        "status": "status",
    },
)
class BrowserCustomAttributes:
    def __init__(
        self,
        *,
        browser_arn: builtins.str,
        role_arn: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        last_updated_at: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes for specifying an imported Browser Custom.

        :param browser_arn: (experimental) The ARN of the agent.
        :param role_arn: (experimental) The ARN of the IAM role associated to the browser.
        :param created_at: (experimental) The created timestamp of the browser. Default: undefined - No created timestamp is provided
        :param last_updated_at: (experimental) When this browser was last updated. Default: undefined - No last updated timestamp is provided
        :param security_groups: (experimental) The security groups for this browser, if in a VPC. Default: - By default, the browser is not in a VPC.
        :param status: (experimental) The status of the browser. Default: undefined - No status is provided

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_bedrock_agentcore_alpha as bedrock_agentcore_alpha
            from aws_cdk import aws_ec2 as ec2
            
            # security_group: ec2.SecurityGroup
            
            browser_custom_attributes = bedrock_agentcore_alpha.BrowserCustomAttributes(
                browser_arn="browserArn",
                role_arn="roleArn",
            
                # the properties below are optional
                created_at="createdAt",
                last_updated_at="lastUpdatedAt",
                security_groups=[security_group],
                status="status"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14ea7632e5df00d60970b59a9a4cb5f38d208fd7a26740e3444fd2b1e4b432ba)
            check_type(argname="argument browser_arn", value=browser_arn, expected_type=type_hints["browser_arn"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument last_updated_at", value=last_updated_at, expected_type=type_hints["last_updated_at"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "browser_arn": browser_arn,
            "role_arn": role_arn,
        }
        if created_at is not None:
            self._values["created_at"] = created_at
        if last_updated_at is not None:
            self._values["last_updated_at"] = last_updated_at
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def browser_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent.

        :stability: experimental
        :attribute: true
        '''
        result = self._values.get("browser_arn")
        assert result is not None, "Required property 'browser_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''(experimental) The ARN of the IAM role associated to the browser.

        :stability: experimental
        :attribute: true
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The created timestamp of the browser.

        :default: undefined - No created timestamp is provided

        :stability: experimental
        '''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When this browser was last updated.

        :default: undefined - No last updated timestamp is provided

        :stability: experimental
        '''
        result = self._values.get("last_updated_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) The security groups for this browser, if in a VPC.

        :default: - By default, the browser is not in a VPC.

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the browser.

        :default: undefined - No status is provided

        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BrowserCustomAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.BrowserCustomProps",
    jsii_struct_bases=[],
    name_mapping={
        "browser_custom_name": "browserCustomName",
        "description": "description",
        "execution_role": "executionRole",
        "network_configuration": "networkConfiguration",
        "recording_config": "recordingConfig",
        "tags": "tags",
    },
)
class BrowserCustomProps:
    def __init__(
        self,
        *,
        browser_custom_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_configuration: typing.Optional["BrowserNetworkConfiguration"] = None,
        recording_config: typing.Optional[typing.Union["RecordingConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for creating a Browser resource.

        :param browser_custom_name: (experimental) The name of the browser Valid characters are a-z, A-Z, 0-9, _ (underscore) The name must start with a letter and can be up to 48 characters long Pattern: [a-zA-Z][a-zA-Z0-9_]{0,47}.
        :param description: (experimental) Optional description for the browser Valid characters are a-z, A-Z, 0-9, _ (underscore), - (hyphen) and spaces The description can have up to 200 characters. Default: - No description
        :param execution_role: (experimental) The IAM role that provides permissions for the browser to access AWS services. Default: - A new role will be created
        :param network_configuration: (experimental) Network configuration for browser. Default: - PUBLIC network mode
        :param recording_config: (experimental) Recording configuration for browser. Default: - No recording configuration
        :param tags: (experimental) Tags (optional) A list of key:value pairs of tags to apply to this Browser resource. Default: {} - no tags

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            # Create a custom execution role
            execution_role = iam.Role(self, "BrowserExecutionRole",
                assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockAgentCoreBrowserExecutionRolePolicy")
                ]
            )
            
            # Create browser with custom execution role
            browser = agentcore.BrowserCustom(self, "MyBrowser",
                browser_custom_name="my_browser",
                description="Browser with custom execution role",
                network_configuration=agentcore.BrowserNetworkConfiguration.using_public_network(),
                execution_role=execution_role
            )
        '''
        if isinstance(recording_config, dict):
            recording_config = RecordingConfig(**recording_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c723ceb06d7434df1c72a1865f418037daeeda29f30194820f0872da7d50bbe8)
            check_type(argname="argument browser_custom_name", value=browser_custom_name, expected_type=type_hints["browser_custom_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument network_configuration", value=network_configuration, expected_type=type_hints["network_configuration"])
            check_type(argname="argument recording_config", value=recording_config, expected_type=type_hints["recording_config"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "browser_custom_name": browser_custom_name,
        }
        if description is not None:
            self._values["description"] = description
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if network_configuration is not None:
            self._values["network_configuration"] = network_configuration
        if recording_config is not None:
            self._values["recording_config"] = recording_config
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def browser_custom_name(self) -> builtins.str:
        '''(experimental) The name of the browser Valid characters are a-z, A-Z, 0-9, _ (underscore) The name must start with a letter and can be up to 48 characters long Pattern: [a-zA-Z][a-zA-Z0-9_]{0,47}.

        :stability: experimental
        :required: - Yes
        '''
        result = self._values.get("browser_custom_name")
        assert result is not None, "Required property 'browser_custom_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional description for the browser Valid characters are a-z, A-Z, 0-9, _ (underscore), - (hyphen) and spaces The description can have up to 200 characters.

        :default: - No description

        :stability: experimental
        :required: - No
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that provides permissions for the browser to access AWS services.

        :default: - A new role will be created

        :stability: experimental
        :required: - No
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def network_configuration(self) -> typing.Optional["BrowserNetworkConfiguration"]:
        '''(experimental) Network configuration for browser.

        :default: - PUBLIC network mode

        :stability: experimental
        :required: - No
        '''
        result = self._values.get("network_configuration")
        return typing.cast(typing.Optional["BrowserNetworkConfiguration"], result)

    @builtins.property
    def recording_config(self) -> typing.Optional["RecordingConfig"]:
        '''(experimental) Recording configuration for browser.

        :default: - No recording configuration

        :stability: experimental
        :required: - No
        '''
        result = self._values.get("recording_config")
        return typing.cast(typing.Optional["RecordingConfig"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Tags (optional) A list of key:value pairs of tags to apply to this Browser resource.

        :default: {} - no tags

        :stability: experimental
        :required: - No
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BrowserCustomProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.CodeInterpreterCustomAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "code_interpreter_arn": "codeInterpreterArn",
        "role_arn": "roleArn",
        "created_at": "createdAt",
        "last_updated_at": "lastUpdatedAt",
        "security_groups": "securityGroups",
        "status": "status",
    },
)
class CodeInterpreterCustomAttributes:
    def __init__(
        self,
        *,
        code_interpreter_arn: builtins.str,
        role_arn: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        last_updated_at: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes for specifying an imported Code Interpreter Custom.

        :param code_interpreter_arn: (experimental) The ARN of the agent.
        :param role_arn: (experimental) The ARN of the IAM role associated to the code interpreter.
        :param created_at: (experimental) The created timestamp of the code interpreter. Default: undefined - No created timestamp is provided
        :param last_updated_at: (experimental) When this code interpreter was last updated. Default: undefined - No last updated timestamp is provided
        :param security_groups: (experimental) The security groups for this code interpreter, if in a VPC. Default: - By default, the code interpreter is not in a VPC.
        :param status: (experimental) The status of the code interpreter. Default: undefined - No status is provided

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_bedrock_agentcore_alpha as bedrock_agentcore_alpha
            from aws_cdk import aws_ec2 as ec2
            
            # security_group: ec2.SecurityGroup
            
            code_interpreter_custom_attributes = bedrock_agentcore_alpha.CodeInterpreterCustomAttributes(
                code_interpreter_arn="codeInterpreterArn",
                role_arn="roleArn",
            
                # the properties below are optional
                created_at="createdAt",
                last_updated_at="lastUpdatedAt",
                security_groups=[security_group],
                status="status"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f96ed57c1afc648e15cebfa320e03f93dc4c161c09d253072930e4b7d4e4ed24)
            check_type(argname="argument code_interpreter_arn", value=code_interpreter_arn, expected_type=type_hints["code_interpreter_arn"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument last_updated_at", value=last_updated_at, expected_type=type_hints["last_updated_at"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "code_interpreter_arn": code_interpreter_arn,
            "role_arn": role_arn,
        }
        if created_at is not None:
            self._values["created_at"] = created_at
        if last_updated_at is not None:
            self._values["last_updated_at"] = last_updated_at
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if status is not None:
            self._values["status"] = status

    @builtins.property
    def code_interpreter_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent.

        :stability: experimental
        :attribute: true
        '''
        result = self._values.get("code_interpreter_arn")
        assert result is not None, "Required property 'code_interpreter_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''(experimental) The ARN of the IAM role associated to the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The created timestamp of the code interpreter.

        :default: undefined - No created timestamp is provided

        :stability: experimental
        '''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When this code interpreter was last updated.

        :default: undefined - No last updated timestamp is provided

        :stability: experimental
        '''
        result = self._values.get("last_updated_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) The security groups for this code interpreter, if in a VPC.

        :default: - By default, the code interpreter is not in a VPC.

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the code interpreter.

        :default: undefined - No status is provided

        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeInterpreterCustomAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.CodeInterpreterCustomProps",
    jsii_struct_bases=[],
    name_mapping={
        "code_interpreter_custom_name": "codeInterpreterCustomName",
        "description": "description",
        "execution_role": "executionRole",
        "network_configuration": "networkConfiguration",
        "tags": "tags",
    },
)
class CodeInterpreterCustomProps:
    def __init__(
        self,
        *,
        code_interpreter_custom_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_configuration: typing.Optional["CodeInterpreterNetworkConfiguration"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for creating a CodeInterpreter resource.

        :param code_interpreter_custom_name: (experimental) The name of the code interpreter Valid characters are a-z, A-Z, 0-9, _ (underscore) The name must start with a letter and can be up to 48 characters long Pattern: [a-zA-Z][a-zA-Z0-9_]{0,47}.
        :param description: (experimental) Optional description for the code interpreter Valid characters are a-z, A-Z, 0-9, _ (underscore), - (hyphen) and spaces The description can have up to 200 characters. Default: - No description
        :param execution_role: (experimental) The IAM role that provides permissions for the code interpreter to access AWS services. Default: - A new role will be created.
        :param network_configuration: (experimental) Network configuration for code interpreter. Default: - PUBLIC network mode
        :param tags: (experimental) Tags (optional) A list of key:value pairs of tags to apply to this Code Interpreter resource. Default: {} - no tags

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            # Create a custom execution role
            execution_role = iam.Role(self, "CodeInterpreterExecutionRole",
                assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com")
            )
            
            # Create code interpreter with custom execution role
            code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
                code_interpreter_custom_name="my_code_interpreter",
                description="Code interpreter with custom execution role",
                network_configuration=agentcore.CodeInterpreterNetworkConfiguration.using_public_network(),
                execution_role=execution_role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e75974384deaaee0d0812c3570b15b1adf0a19fbd67095aea1229a4d3d5c5c05)
            check_type(argname="argument code_interpreter_custom_name", value=code_interpreter_custom_name, expected_type=type_hints["code_interpreter_custom_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument network_configuration", value=network_configuration, expected_type=type_hints["network_configuration"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "code_interpreter_custom_name": code_interpreter_custom_name,
        }
        if description is not None:
            self._values["description"] = description
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if network_configuration is not None:
            self._values["network_configuration"] = network_configuration
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def code_interpreter_custom_name(self) -> builtins.str:
        '''(experimental) The name of the code interpreter Valid characters are a-z, A-Z, 0-9, _ (underscore) The name must start with a letter and can be up to 48 characters long Pattern: [a-zA-Z][a-zA-Z0-9_]{0,47}.

        :stability: experimental
        :required: - Yes
        '''
        result = self._values.get("code_interpreter_custom_name")
        assert result is not None, "Required property 'code_interpreter_custom_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional description for the code interpreter Valid characters are a-z, A-Z, 0-9, _ (underscore), - (hyphen) and spaces The description can have up to 200 characters.

        :default: - No description

        :stability: experimental
        :required: - No
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that provides permissions for the code interpreter to access AWS services.

        :default: - A new role will be created.

        :stability: experimental
        :required: - No
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def network_configuration(
        self,
    ) -> typing.Optional["CodeInterpreterNetworkConfiguration"]:
        '''(experimental) Network configuration for code interpreter.

        :default: - PUBLIC network mode

        :stability: experimental
        :required: - No
        '''
        result = self._values.get("network_configuration")
        return typing.cast(typing.Optional["CodeInterpreterNetworkConfiguration"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Tags (optional) A list of key:value pairs of tags to apply to this Code Interpreter resource.

        :default: {} - no tags

        :stability: experimental
        :required: - No
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CodeInterpreterCustomProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.IBedrockAgentRuntime")
class IBedrockAgentRuntime(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_iam_ceddda9d.IGrantable,
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    typing_extensions.Protocol,
):
    '''(experimental) Interface for Agent Runtime resources.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent runtime resource - Format ``arn:${Partition}:bedrock-agentcore:${Region}:${Account}:runtime/${RuntimeId}``.

        :stability: experimental
        :attribute: true

        Example::

            "arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/runtime-abc123"
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeId")
    def agent_runtime_id(self) -> builtins.str:
        '''(experimental) The ID of the agent runtime.

        :stability: experimental
        :attribute: true

        Example::

            "runtime-abc123"
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeName")
    def agent_runtime_name(self) -> builtins.str:
        '''(experimental) The name of the agent runtime.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the agent runtime.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeVersion")
    def agent_runtime_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of the agent runtime.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentStatus")
    def agent_status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the agent runtime.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was created.

        :stability: experimental
        :attribute: true

        Example::

            "2024-01-15T10:30:00Z"
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was last updated.

        :stability: experimental
        :attribute: true

        Example::

            "2024-01-15T14:45:00Z"
        '''
        ...

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> "IBedrockAgentRuntime":
        '''(experimental) Adds a policy statement to the runtime's execution role.

        :param statement: The IAM policy statement to add.

        :return: The runtime instance for chaining

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        actions: typing.Sequence[builtins.str],
        resources: typing.Sequence[builtins.str],
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the runtime specific actions on AWS resources.

        :param actions: The actions to grant.
        :param resources: The resource ARNs to grant access to.

        :return: The Grant object for chaining

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal to invoke this runtime both directly and on behalf of users Grants both bedrock-agentcore:InvokeAgentRuntime and bedrock-agentcore:InvokeAgentRuntimeForUser permissions.

        :param grantee: The principal to grant access to.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantInvokeRuntime")
    def grant_invoke_runtime(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal to invoke this runtime Grants the bedrock-agentcore:InvokeAgentRuntime permission.

        :param grantee: The principal to grant access to.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantInvokeRuntimeForUser")
    def grant_invoke_runtime_for_user(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal to invoke this runtime on behalf of a user Grants the bedrock-agentcore:InvokeAgentRuntimeForUser permission Required when using the X-Amzn-Bedrock-AgentCore-Runtime-User-Id header.

        :param grantee: The principal to grant access to.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this agent runtime.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricInvocations")
    def metric_invocations(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of invocations for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricInvocationsAggregated")
    def metric_invocations_aggregated(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of invocations across all resources.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricLatency")
    def metric_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of requests for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricSessionCount")
    def metric_session_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of agent sessions for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricSessionsAggregated")
    def metric_sessions_aggregated(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of sessions across all resources.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricSystemErrors")
    def metric_system_errors(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of system errors for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricThrottles")
    def metric_throttles(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of throttled requests for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricTotalErrors")
    def metric_total_errors(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of errors (system + user) for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricUserErrors")
    def metric_user_errors(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user errors for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...


class _IBedrockAgentRuntimeProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
):
    '''(experimental) Interface for Agent Runtime resources.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-bedrock-agentcore-alpha.IBedrockAgentRuntime"

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent runtime resource - Format ``arn:${Partition}:bedrock-agentcore:${Region}:${Account}:runtime/${RuntimeId}``.

        :stability: experimental
        :attribute: true

        Example::

            "arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/runtime-abc123"
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeArn"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeId")
    def agent_runtime_id(self) -> builtins.str:
        '''(experimental) The ID of the agent runtime.

        :stability: experimental
        :attribute: true

        Example::

            "runtime-abc123"
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeId"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeName")
    def agent_runtime_name(self) -> builtins.str:
        '''(experimental) The name of the agent runtime.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeName"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the agent runtime.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeVersion")
    def agent_runtime_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of the agent runtime.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentRuntimeVersion"))

    @builtins.property
    @jsii.member(jsii_name="agentStatus")
    def agent_status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the agent runtime.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentStatus"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was created.

        :stability: experimental
        :attribute: true

        Example::

            "2024-01-15T10:30:00Z"
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was last updated.

        :stability: experimental
        :attribute: true

        Example::

            "2024-01-15T14:45:00Z"
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> IBedrockAgentRuntime:
        '''(experimental) Adds a policy statement to the runtime's execution role.

        :param statement: The IAM policy statement to add.

        :return: The runtime instance for chaining

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b1a5766ae93ba39d5e7df12bdfc35c2a7d298375e7689fbc39a3c76d50d2639)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(IBedrockAgentRuntime, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        actions: typing.Sequence[builtins.str],
        resources: typing.Sequence[builtins.str],
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the runtime specific actions on AWS resources.

        :param actions: The actions to grant.
        :param resources: The resource ARNs to grant access to.

        :return: The Grant object for chaining

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3208bdcc07b3a3b3b7ac0ed80c7b033074eab2659722a2dec0d8400cf5da5af8)
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [actions, resources]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal to invoke this runtime both directly and on behalf of users Grants both bedrock-agentcore:InvokeAgentRuntime and bedrock-agentcore:InvokeAgentRuntimeForUser permissions.

        :param grantee: The principal to grant access to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e4ed0dc7cd812fb1d50239f33a79cd0a5de1be6488c8ee24a3b016a546ef94b)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvoke", [grantee]))

    @jsii.member(jsii_name="grantInvokeRuntime")
    def grant_invoke_runtime(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal to invoke this runtime Grants the bedrock-agentcore:InvokeAgentRuntime permission.

        :param grantee: The principal to grant access to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e37d3744eaf4f98404f5daccedff6e7a637774c39193ceadfd0f88c7aa16d50)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvokeRuntime", [grantee]))

    @jsii.member(jsii_name="grantInvokeRuntimeForUser")
    def grant_invoke_runtime_for_user(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal to invoke this runtime on behalf of a user Grants the bedrock-agentcore:InvokeAgentRuntimeForUser permission Required when using the X-Amzn-Bedrock-AgentCore-Runtime-User-Id header.

        :param grantee: The principal to grant access to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b28241dea68e79093525ede5e9deed8adeda944e89126bbcebe733fd16561495)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvokeRuntimeForUser", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this agent runtime.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3beecc1a8cde07edfff6ed6fa9c6deb0e5c35524c1b4ca5bc87c39f95ca1f565)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, dimensions, props]))

    @jsii.member(jsii_name="metricInvocations")
    def metric_invocations(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of invocations for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocations", [props]))

    @jsii.member(jsii_name="metricInvocationsAggregated")
    def metric_invocations_aggregated(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of invocations across all resources.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocationsAggregated", [props]))

    @jsii.member(jsii_name="metricLatency")
    def metric_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of requests for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatency", [props]))

    @jsii.member(jsii_name="metricSessionCount")
    def metric_session_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of agent sessions for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSessionCount", [props]))

    @jsii.member(jsii_name="metricSessionsAggregated")
    def metric_sessions_aggregated(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of sessions across all resources.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSessionsAggregated", [props]))

    @jsii.member(jsii_name="metricSystemErrors")
    def metric_system_errors(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of system errors for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSystemErrors", [props]))

    @jsii.member(jsii_name="metricThrottles")
    def metric_throttles(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of throttled requests for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricThrottles", [props]))

    @jsii.member(jsii_name="metricTotalErrors")
    def metric_total_errors(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of errors (system + user) for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTotalErrors", [props]))

    @jsii.member(jsii_name="metricUserErrors")
    def metric_user_errors(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user errors for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricUserErrors", [props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBedrockAgentRuntime).__jsii_proxy_class__ = lambda : _IBedrockAgentRuntimeProxy


@jsii.interface(jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.IBrowserCustom")
class IBrowserCustom(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_iam_ceddda9d.IGrantable,
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    typing_extensions.Protocol,
):
    '''(experimental) Interface for Browser resources.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="browserArn")
    def browser_arn(self) -> builtins.str:
        '''(experimental) The ARN of the browser resource.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="browserId")
    def browser_id(self) -> builtins.str:
        '''(experimental) The id of the browser.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the browser to access AWS services.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the browser was created.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the browser was last updated.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the browser.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants IAM actions to the IAM Principal.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants ``Get`` and ``List`` actions on the Browser.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantUse")
    def grant_use(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants ``Invoke``, ``Start``, and ``Update`` actions on the Browser.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this browser.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricErrorsForApiOperation")
    def metric_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of errors for a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricForApiOperation")
    def metric_for_api_operation(
        self,
        metric_name: builtins.str,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric related to the API operation performed on this browser.

        :param metric_name: -
        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricInvocationsForApiOperation")
    def metric_invocations_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of API requests made for a specific browser operation.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricLatencyForApiOperation")
    def metric_latency_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricSessionDuration")
    def metric_session_duration(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the duration of browser sessions.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricSystemErrorsForApiOperation")
    def metric_system_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of system errors for a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricTakeOverCount")
    def metric_take_over_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user takeovers.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricTakeOverDuration")
    def metric_take_over_duration(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the duration of user takeovers.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricTakeOverReleaseCount")
    def metric_take_over_release_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user takeovers released.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricThrottlesForApiOperation")
    def metric_throttles_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of throttled requests for a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricUserErrorsForApiOperation")
    def metric_user_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user errors for a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...


class _IBrowserCustomProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
):
    '''(experimental) Interface for Browser resources.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-bedrock-agentcore-alpha.IBrowserCustom"

    @builtins.property
    @jsii.member(jsii_name="browserArn")
    def browser_arn(self) -> builtins.str:
        '''(experimental) The ARN of the browser resource.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "browserArn"))

    @builtins.property
    @jsii.member(jsii_name="browserId")
    def browser_id(self) -> builtins.str:
        '''(experimental) The id of the browser.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "browserId"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the browser to access AWS services.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the browser was created.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the browser was last updated.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the browser.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants IAM actions to the IAM Principal.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4826f7478acda3a04d53cc2e00e999d28d4b6af89d40b4863b0007b08c0b26bf)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants ``Get`` and ``List`` actions on the Browser.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da9382b030a7d475c5afa4286f7e177b609a5f61d4d9d40b1767f5c1e99b8815)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantUse")
    def grant_use(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants ``Invoke``, ``Start``, and ``Update`` actions on the Browser.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd8850bcf1d06baf4b66c051e33ef652a6c75bc169744326c9d541535c3f3ca7)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantUse", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this browser.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efd83ae8402a4ac91c4d9cee61087a64dc24f53da2f48b59aa2cc85cde883b29)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, dimensions, props]))

    @jsii.member(jsii_name="metricErrorsForApiOperation")
    def metric_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of errors for a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9182d2fd8511b983f694d71df771315bd2911e5e5d9482b933161a628210ec54)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricForApiOperation")
    def metric_for_api_operation(
        self,
        metric_name: builtins.str,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric related to the API operation performed on this browser.

        :param metric_name: -
        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e825fd71c16a04ffa07fa3e9ff9d61d6e478bdf2f90788eba67bba76e9f38ccb)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricForApiOperation", [metric_name, operation, props]))

    @jsii.member(jsii_name="metricInvocationsForApiOperation")
    def metric_invocations_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of API requests made for a specific browser operation.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cf7f7691dff5fcb719882b3a76ff7b4a55b686f01244cf9ab3c1ee39a4dd4fc)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocationsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricLatencyForApiOperation")
    def metric_latency_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6be7d90ffdb2f66b76b997f0926ae3ff14c53cc65c008f5a0591e3f4676265a)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatencyForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricSessionDuration")
    def metric_session_duration(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the duration of browser sessions.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSessionDuration", [props]))

    @jsii.member(jsii_name="metricSystemErrorsForApiOperation")
    def metric_system_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of system errors for a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfb1295c98675d8b1f487abc85bf1d69ec7ac709035de1d15c83e328863a23ec)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSystemErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricTakeOverCount")
    def metric_take_over_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user takeovers.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTakeOverCount", [props]))

    @jsii.member(jsii_name="metricTakeOverDuration")
    def metric_take_over_duration(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the duration of user takeovers.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTakeOverDuration", [props]))

    @jsii.member(jsii_name="metricTakeOverReleaseCount")
    def metric_take_over_release_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user takeovers released.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTakeOverReleaseCount", [props]))

    @jsii.member(jsii_name="metricThrottlesForApiOperation")
    def metric_throttles_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of throttled requests for a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea0c6d4b07cd9212bb39f789638d8a9a6af30cbc0157a19bcd58f6b94d852755)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricThrottlesForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricUserErrorsForApiOperation")
    def metric_user_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user errors for a specific API operation performed on this browser.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1768ca682c2fd421a544ff8111e6e6985b07e3d62cdc62c35ef9cee5896ce2e)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricUserErrorsForApiOperation", [operation, props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IBrowserCustom).__jsii_proxy_class__ = lambda : _IBrowserCustomProxy


@jsii.interface(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.ICodeInterpreterCustom"
)
class ICodeInterpreterCustom(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_iam_ceddda9d.IGrantable,
    _aws_cdk_aws_ec2_ceddda9d.IConnectable,
    typing_extensions.Protocol,
):
    '''(experimental) Interface for CodeInterpreterCustom resources.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="codeInterpreterArn")
    def code_interpreter_arn(self) -> builtins.str:
        '''(experimental) The ARN of the code interpreter resource.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="codeInterpreterId")
    def code_interpreter_id(self) -> builtins.str:
        '''(experimental) The id of the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the code interpreter to access AWS services.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the code interpreter was created.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the code interpreter was last updated.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants IAM actions to the IAM Principal.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants ``Get`` and ``List`` actions on the Code Interpreter.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantUse")
    def grant_use(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants ``Invoke``, ``Start``, and ``Stop`` actions on the Code Interpreter.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this code interpreter.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricErrorsForApiOperation")
    def metric_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of errors for a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricForApiOperation")
    def metric_for_api_operation(
        self,
        metric_name: builtins.str,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric related to the API operation performed on this code interpreter.

        :param metric_name: -
        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricInvocationsForApiOperation")
    def metric_invocations_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of API requests made for a specific code interpreter operation.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricLatencyForApiOperation")
    def metric_latency_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricSessionDuration")
    def metric_session_duration(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the duration of code interpreter sessions.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricSystemErrorsForApiOperation")
    def metric_system_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of system errors for a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricThrottlesForApiOperation")
    def metric_throttles_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of throttled requests for a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricUserErrorsForApiOperation")
    def metric_user_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user errors for a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...


class _ICodeInterpreterCustomProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_ec2_ceddda9d.IConnectable), # type: ignore[misc]
):
    '''(experimental) Interface for CodeInterpreterCustom resources.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-bedrock-agentcore-alpha.ICodeInterpreterCustom"

    @builtins.property
    @jsii.member(jsii_name="codeInterpreterArn")
    def code_interpreter_arn(self) -> builtins.str:
        '''(experimental) The ARN of the code interpreter resource.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "codeInterpreterArn"))

    @builtins.property
    @jsii.member(jsii_name="codeInterpreterId")
    def code_interpreter_id(self) -> builtins.str:
        '''(experimental) The id of the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "codeInterpreterId"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the code interpreter to access AWS services.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the code interpreter was created.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the code interpreter was last updated.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants IAM actions to the IAM Principal.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04274b315577b6819dda4346fc076850f28656449a559f5561ca7d53df97f5e3)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants ``Get`` and ``List`` actions on the Code Interpreter.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ec65ea8e752705bafc58f0d6cacd39d556973c472ffb0789fa4af3ebcce4bcc)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantUse")
    def grant_use(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants ``Invoke``, ``Start``, and ``Stop`` actions on the Code Interpreter.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d24a36658edbfd7ecf76e5be971a6012fc93c641f1a510d1ddfd95730be1d7db)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantUse", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this code interpreter.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4df790d3e336e48159d1eef607374eaf8f903928d69bd2620e375c4794e4fb3)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, dimensions, props]))

    @jsii.member(jsii_name="metricErrorsForApiOperation")
    def metric_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of errors for a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eedad4c7938113f5f34f301a9b648ae40f5400a9e4de351b0186137052a65fab)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricForApiOperation")
    def metric_for_api_operation(
        self,
        metric_name: builtins.str,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric related to the API operation performed on this code interpreter.

        :param metric_name: -
        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__669e8f3a0db7a0b0e3787f22af4e559b8709590c28a9b79f240d11855cd87a11)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricForApiOperation", [metric_name, operation, props]))

    @jsii.member(jsii_name="metricInvocationsForApiOperation")
    def metric_invocations_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of API requests made for a specific code interpreter operation.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5ade6561c63063084b2bd832a2df3362c624482ddaf7b7207ebec55d3e5431b)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocationsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricLatencyForApiOperation")
    def metric_latency_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79fd1126b940aa58648080ebef78a6ecac9291a3f4e257a9e9b8a3b62fb84e5a)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatencyForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricSessionDuration")
    def metric_session_duration(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the duration of code interpreter sessions.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSessionDuration", [props]))

    @jsii.member(jsii_name="metricSystemErrorsForApiOperation")
    def metric_system_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of system errors for a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b950226f77f1b8ff84aba977a1f05f62ed459462976db6648d94a67e1e1ef8cf)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSystemErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricThrottlesForApiOperation")
    def metric_throttles_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of throttled requests for a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4e3175daf088ea941aee60546645fc39148e3a11ab2b2e5d897a48eff09f4e0)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricThrottlesForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricUserErrorsForApiOperation")
    def metric_user_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user errors for a specific API operation performed on this code interpreter.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e9e3e47628eaf2b6a4ffa31b2d7904f6d5438386a823eeca9d34b97f6f484df)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricUserErrorsForApiOperation", [operation, props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICodeInterpreterCustom).__jsii_proxy_class__ = lambda : _ICodeInterpreterCustomProxy


@jsii.interface(jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.IMemory")
class IMemory(
    _aws_cdk_ceddda9d.IResource,
    _aws_cdk_aws_iam_ceddda9d.IGrantable,
    typing_extensions.Protocol,
):
    '''(experimental) Interface for Memory resources.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="memoryArn")
    def memory_arn(self) -> builtins.str:
        '''(experimental) The ARN of the memory resource.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="memoryId")
    def memory_id(self) -> builtins.str:
        '''(experimental) The id of the memory.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the memory was created.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that provides permissions for the memory to access AWS services.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Custom KMS key for encryption (if provided).

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the memory.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the memory was last updated.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to perform actions on this memory.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantAdmin")
    def grant_admin(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to manage the control plane of this memory.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantDelete")
    def grant_delete(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to delete content on this memory.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantDeleteLongTermMemory")
    def grant_delete_long_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to delete Long-Term Memory (LTM) content on this memory.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantDeleteShortTermMemory")
    def grant_delete_short_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to delete Short-Term Memory (STM) content on this memory.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantFullAccess")
    def grant_full_access(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to do every action on this memory.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to read the contents of this memory.

        Both Short-Term Memory (STM) and Long-Term Memory (LTM).

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantReadLongTermMemory")
    def grant_read_long_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to read the Long-Term Memory (LTM) contents of this memory.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantReadShortTermMemory")
    def grant_read_short_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to read the Short-Term Memory (STM) contents of this memory.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to write content to this memory.

        :param grantee: -

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this memory.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricErrorsForApiOperation")
    def metric_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of errors for a specific API operation performed on this memory.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricEventCreationCount")
    def metric_event_creation_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Returns the metric containing the number of created memory events and memory records.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricForApiOperation")
    def metric_for_api_operation(
        self,
        metric_name: builtins.str,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric related to the API operation performed on this memory.

        :param metric_name: -
        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricInvocationsForApiOperation")
    def metric_invocations_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of API requests made for a specific memory operation.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="metricLatencyForApiOperation")
    def metric_latency_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of a specific API operation performed on this memory.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        ...


class _IMemoryProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
    jsii.proxy_for(_aws_cdk_aws_iam_ceddda9d.IGrantable), # type: ignore[misc]
):
    '''(experimental) Interface for Memory resources.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-bedrock-agentcore-alpha.IMemory"

    @builtins.property
    @jsii.member(jsii_name="memoryArn")
    def memory_arn(self) -> builtins.str:
        '''(experimental) The ARN of the memory resource.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "memoryArn"))

    @builtins.property
    @jsii.member(jsii_name="memoryId")
    def memory_id(self) -> builtins.str:
        '''(experimental) The id of the memory.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "memoryId"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the memory was created.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that provides permissions for the memory to access AWS services.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Custom KMS key for encryption (if provided).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "kmsKey"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the memory.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the memory was last updated.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedAt"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to perform actions on this memory.

        :param grantee: -
        :param actions: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1ba6d29d64132509e28874cca93c8505709d69d09be77f6f547e643a9774030)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantAdmin")
    def grant_admin(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to manage the control plane of this memory.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a457d9a5a92b2c5dd54c5d40968692e34fd532950d041ea5bfd0de913373be6)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantAdmin", [grantee]))

    @jsii.member(jsii_name="grantDelete")
    def grant_delete(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to delete content on this memory.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c3efca2cc63cffb669b48299f658d617bda63982dc81fa5aa921c81c38ca079)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantDelete", [grantee]))

    @jsii.member(jsii_name="grantDeleteLongTermMemory")
    def grant_delete_long_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to delete Long-Term Memory (LTM) content on this memory.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7fcbbdfb908085fece3b62e0ffaf13f969e5bedd85b66a5c13523ce5bbee646)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantDeleteLongTermMemory", [grantee]))

    @jsii.member(jsii_name="grantDeleteShortTermMemory")
    def grant_delete_short_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to delete Short-Term Memory (STM) content on this memory.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__525b2d326cfe421d9a86d322af9dc60a4ed2bb6edc363fe98cfa6d82ff3adc06)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantDeleteShortTermMemory", [grantee]))

    @jsii.member(jsii_name="grantFullAccess")
    def grant_full_access(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to do every action on this memory.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af17b3916084293603368124beefd4ec59dde44dc47b240d7c9a1ec0f2f5ffa5)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantFullAccess", [grantee]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to read the contents of this memory.

        Both Short-Term Memory (STM) and Long-Term Memory (LTM).

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__783d0a6fd1dc20ff0f9527e5c3a52633d4321b96341e6b9bc5d3fa0e92dc5dfe)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantReadLongTermMemory")
    def grant_read_long_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to read the Long-Term Memory (LTM) contents of this memory.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9f0a0f5b7fbecabe02b1b20a8835379801ca7f66484f1dd2ef68046ff8b462f)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantReadLongTermMemory", [grantee]))

    @jsii.member(jsii_name="grantReadShortTermMemory")
    def grant_read_short_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to read the Short-Term Memory (STM) contents of this memory.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c589e19a59d911709d856e20382d97b619ddb3a73bbe0dee0153bfc97d443b7c)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantReadShortTermMemory", [grantee]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to write content to this memory.

        :param grantee: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94eb3e104c0dd678b10cd6541492be79335617ce87b76c7e823bbc387f58660e)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantWrite", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this memory.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9345c8520d55c1b82df6b4c9358835ed22ef5781b504459d222e3fc6908b84c7)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, dimensions, props]))

    @jsii.member(jsii_name="metricErrorsForApiOperation")
    def metric_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of errors for a specific API operation performed on this memory.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22ff2e593babb16dbf3ae7775b5b673ea5bc68bba3e2e5317817e4a1a5206a17)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricEventCreationCount")
    def metric_event_creation_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Returns the metric containing the number of created memory events and memory records.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricEventCreationCount", [props]))

    @jsii.member(jsii_name="metricForApiOperation")
    def metric_for_api_operation(
        self,
        metric_name: builtins.str,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric related to the API operation performed on this memory.

        :param metric_name: -
        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a0a57ceae64fde7d7d2cfe0668f54aa401bbf9dcd02a1c202ab70648e8cda21)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricForApiOperation", [metric_name, operation, props]))

    @jsii.member(jsii_name="metricInvocationsForApiOperation")
    def metric_invocations_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of API requests made for a specific memory operation.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e61b20f12b812c882b8260200f86a0153fe5fbde4437c6d474693246202a1b9)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocationsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricLatencyForApiOperation")
    def metric_latency_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of a specific API operation performed on this memory.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9002a7efe6fb5cf7e675e605de960b66ee27aeceb3ef6161eac905e343326468)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatencyForApiOperation", [operation, props]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMemory).__jsii_proxy_class__ = lambda : _IMemoryProxy


@jsii.interface(jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.IMemoryStrategy")
class IMemoryStrategy(typing_extensions.Protocol):
    '''(experimental) Interface for Memory strategies.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the memory strategy.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="strategyType")
    def strategy_type(self) -> "MemoryStrategyType":
        '''(experimental) The type of memory strategy.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the memory strategy.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Grant]:
        '''(experimental) Grants the necessary permissions to the role.

        :param grantee: - The grantee to grant permissions to.

        :return: The Grant object for chaining

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="render")
    def render(
        self,
    ) -> _aws_cdk_aws_bedrockagentcore_ceddda9d.CfnMemory.MemoryStrategyProperty:
        '''(experimental) Renders internal attributes to CloudFormation.

        :stability: experimental
        '''
        ...


class _IMemoryStrategyProxy:
    '''(experimental) Interface for Memory strategies.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-bedrock-agentcore-alpha.IMemoryStrategy"

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the memory strategy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="strategyType")
    def strategy_type(self) -> "MemoryStrategyType":
        '''(experimental) The type of memory strategy.

        :stability: experimental
        '''
        return typing.cast("MemoryStrategyType", jsii.get(self, "strategyType"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the memory strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Grant]:
        '''(experimental) Grants the necessary permissions to the role.

        :param grantee: - The grantee to grant permissions to.

        :return: The Grant object for chaining

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__934b8b491b04ba3c7c4ab4f5bc06c324dbefd303c41cbc2cfa977906701fa994)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Grant], jsii.invoke(self, "grant", [grantee]))

    @jsii.member(jsii_name="render")
    def render(
        self,
    ) -> _aws_cdk_aws_bedrockagentcore_ceddda9d.CfnMemory.MemoryStrategyProperty:
        '''(experimental) Renders internal attributes to CloudFormation.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_bedrockagentcore_ceddda9d.CfnMemory.MemoryStrategyProperty, jsii.invoke(self, "render", []))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IMemoryStrategy).__jsii_proxy_class__ = lambda : _IMemoryStrategyProxy


@jsii.interface(jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.IRuntimeEndpoint")
class IRuntimeEndpoint(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Interface for Runtime Endpoint resources.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the parent agent runtime.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeEndpointArn")
    def agent_runtime_endpoint_arn(self) -> builtins.str:
        '''(experimental) The ARN of the runtime endpoint resource.

        :stability: experimental
        :attribute: true

        Example::

            "arn:aws:bedrock-agentcore:us-west-2:123456789012:agent-runtime-endpoint/endpoint-abc123"
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> builtins.str:
        '''(experimental) The name of the runtime endpoint.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When the endpoint was created.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the runtime endpoint.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="liveVersion")
    def live_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The live version of the agent runtime that is currently serving requests.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the runtime endpoint.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="targetVersion")
    def target_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The target version the endpoint is transitioning to (during updates).

        :stability: experimental
        :attribute: true
        '''
        ...


class _IRuntimeEndpointProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Interface for Runtime Endpoint resources.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-bedrock-agentcore-alpha.IRuntimeEndpoint"

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the parent agent runtime.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeArn"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeEndpointArn")
    def agent_runtime_endpoint_arn(self) -> builtins.str:
        '''(experimental) The ARN of the runtime endpoint resource.

        :stability: experimental
        :attribute: true

        Example::

            "arn:aws:bedrock-agentcore:us-west-2:123456789012:agent-runtime-endpoint/endpoint-abc123"
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeEndpointArn"))

    @builtins.property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> builtins.str:
        '''(experimental) The name of the runtime endpoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointName"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When the endpoint was created.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the runtime endpoint.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="liveVersion")
    def live_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The live version of the agent runtime that is currently serving requests.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "liveVersion"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the runtime endpoint.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="targetVersion")
    def target_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The target version the endpoint is transitioning to (during updates).

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetVersion"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IRuntimeEndpoint).__jsii_proxy_class__ = lambda : _IRuntimeEndpointProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.InvocationConfiguration",
    jsii_struct_bases=[],
    name_mapping={"s3_location": "s3Location", "topic": "topic"},
)
class InvocationConfiguration:
    def __init__(
        self,
        *,
        s3_location: typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]],
        topic: _aws_cdk_aws_sns_ceddda9d.ITopic,
    ) -> None:
        '''(experimental) Invocation configuration for self managed memory strategy.

        :param s3_location: (experimental) S3 Location Configuration.
        :param topic: (experimental) SNS Topic Configuration.

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            bucket = s3.Bucket(self, "memoryBucket",
                bucket_name="test-memory",
                removal_policy=cdk.RemovalPolicy.DESTROY,
                auto_delete_objects=True
            )
            
            topic = sns.Topic(self, "topic")
            
            # Create a custom semantic memory strategy
            self_managed_strategy = agentcore.MemoryStrategy.using_self_managed(
                name="selfManagedStrategy",
                description="self managed memory strategy",
                historical_context_window_size=5,
                invocation_configuration=agentcore.InvocationConfiguration(
                    topic=topic,
                    s3_location=s3.Location(
                        bucket_name=bucket.bucket_name,
                        object_key="memory/"
                    )
                ),
                trigger_conditions=agentcore.TriggerConditions(
                    message_based_trigger=1,
                    time_based_trigger=cdk.Duration.seconds(10),
                    token_based_trigger=100
                )
            )
            
            # Create memory with custom strategy
            memory = agentcore.Memory(self, "MyMemory",
                memory_name="my-custom-memory",
                description="Memory with custom strategy",
                expiration_duration=cdk.Duration.days(90),
                memory_strategies=[self_managed_strategy]
            )
        '''
        if isinstance(s3_location, dict):
            s3_location = _aws_cdk_aws_s3_ceddda9d.Location(**s3_location)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa543deca8fc3f65b1c914de7ff1c671f34fc56d017dd3a14ead3387b906c0c4)
            check_type(argname="argument s3_location", value=s3_location, expected_type=type_hints["s3_location"])
            check_type(argname="argument topic", value=topic, expected_type=type_hints["topic"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "s3_location": s3_location,
            "topic": topic,
        }

    @builtins.property
    def s3_location(self) -> _aws_cdk_aws_s3_ceddda9d.Location:
        '''(experimental) S3 Location Configuration.

        :stability: experimental
        '''
        result = self._values.get("s3_location")
        assert result is not None, "Required property 's3_location' is missing"
        return typing.cast(_aws_cdk_aws_s3_ceddda9d.Location, result)

    @builtins.property
    def topic(self) -> _aws_cdk_aws_sns_ceddda9d.ITopic:
        '''(experimental) SNS Topic Configuration.

        :stability: experimental
        '''
        result = self._values.get("topic")
        assert result is not None, "Required property 'topic' is missing"
        return typing.cast(_aws_cdk_aws_sns_ceddda9d.ITopic, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InvocationConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IMemoryStrategy)
class ManagedMemoryStrategy(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.ManagedMemoryStrategy",
):
    '''(experimental) Managed memory strategy that handles both built-in and override configurations.

    This strategy can be used for quick setup with built-in defaults or customized
    with specific models and prompt templates.

    :stability: experimental
    :exampleMetadata: fixture=default infused

    Example::

        # Create a custom semantic memory strategy
        custom_semantic_strategy = agentcore.MemoryStrategy.using_semantic(
            name="customSemanticStrategy",
            description="Custom semantic memory strategy",
            namespaces=["/custom/strategies/{memoryStrategyId}/actors/{actorId}"],
            custom_consolidation=agentcore.OverrideConfig(
                model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
                append_to_prompt="Custom consolidation prompt for semantic memory"
            ),
            custom_extraction=agentcore.OverrideConfig(
                model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
                append_to_prompt="Custom extraction prompt for semantic memory"
            )
        )
        
        # Create memory with custom strategy
        memory = agentcore.Memory(self, "MyMemory",
            memory_name="my-custom-memory",
            description="Memory with custom strategy",
            expiration_duration=cdk.Duration.days(90),
            memory_strategies=[custom_semantic_strategy]
        )
    '''

    def __init__(
        self,
        strategy_type: "MemoryStrategyType",
        *,
        namespaces: typing.Sequence[builtins.str],
        custom_consolidation: typing.Optional[typing.Union["OverrideConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_extraction: typing.Optional[typing.Union["OverrideConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Constructor to create a new managed memory strategy.

        :param strategy_type: the strategy type.
        :param namespaces: (experimental) The namespaces for the strategy Represents a namespace for organizing memory data Use a hierarchical format separated by forward slashes (/). Use a hierarchical format separated by forward slashes (/) to organize namespaces logically. You can include these defined variables: - {sessionId} - the user identifier to be created in the CreateEvent API - {memoryStrategyId} - an identifier for an extraction strategy - {sessionId} - an identifier for each session Example namespace path: /strategies/{memoryStrategyId}/actions/{actionId}/sessions/{sessionId} After memory creation, this namespace might look like: /actor/actor-3afc5aa8fef9/strategy/summarization-fy5c5fwc7/session/session-qj7tpd1kvr8
        :param custom_consolidation: (experimental) The configuration for the custom consolidation. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction
        :param custom_extraction: (experimental) The configuration for the custom extraction. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction
        :param name: (experimental) The name for the strategy.
        :param description: (experimental) The description of the strategy. Default: - No description

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9656ac57c24ef4e4e75d86e1e22eccddbeda2a4c2f59b55521bc042a2350d17c)
            check_type(argname="argument strategy_type", value=strategy_type, expected_type=type_hints["strategy_type"])
        props = ManagedStrategyProps(
            namespaces=namespaces,
            custom_consolidation=custom_consolidation,
            custom_extraction=custom_extraction,
            name=name,
            description=description,
        )

        jsii.create(self.__class__, self, [strategy_type, props])

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Grant]:
        '''(experimental) Grants the necessary permissions to the role.

        :param grantee: - The grantee to grant permissions to.

        :return: The Grant object for chaining

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__026d68ecbae145c075bcc9aa152bf018434394cf6d580dcb55ada773bcffda7b)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Grant], jsii.invoke(self, "grant", [grantee]))

    @jsii.member(jsii_name="render")
    def render(
        self,
    ) -> _aws_cdk_aws_bedrockagentcore_ceddda9d.CfnMemory.MemoryStrategyProperty:
        '''(experimental) Renders the network configuration as a CloudFormation property.

        :return: The CloudFormation property for the memory strategy.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_bedrockagentcore_ceddda9d.CfnMemory.MemoryStrategyProperty, jsii.invoke(self, "render", []))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the memory strategy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="namespaces")
    def namespaces(self) -> typing.List[builtins.str]:
        '''(experimental) The namespaces for the strategy.

        :stability: experimental
        '''
        return typing.cast(typing.List[builtins.str], jsii.get(self, "namespaces"))

    @builtins.property
    @jsii.member(jsii_name="strategyType")
    def strategy_type(self) -> "MemoryStrategyType":
        '''(experimental) The type of memory strategy.

        :stability: experimental
        '''
        return typing.cast("MemoryStrategyType", jsii.get(self, "strategyType"))

    @builtins.property
    @jsii.member(jsii_name="consolidationOverride")
    def consolidation_override(self) -> typing.Optional["OverrideConfig"]:
        '''(experimental) The configuration for the custom consolidation.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["OverrideConfig"], jsii.get(self, "consolidationOverride"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the memory strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="extractionOverride")
    def extraction_override(self) -> typing.Optional["OverrideConfig"]:
        '''(experimental) The configuration for the custom extraction.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["OverrideConfig"], jsii.get(self, "extractionOverride"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.MemoryAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "memory_arn": "memoryArn",
        "role_arn": "roleArn",
        "created_at": "createdAt",
        "kms_key_arn": "kmsKeyArn",
        "status": "status",
        "updated_at": "updatedAt",
    },
)
class MemoryAttributes:
    def __init__(
        self,
        *,
        memory_arn: builtins.str,
        role_arn: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes for specifying an imported Memory.

        :param memory_arn: (experimental) The ARN of the memory.
        :param role_arn: (experimental) The ARN of the IAM role associated to the memory.
        :param created_at: (experimental) The created timestamp of the memory. Default: undefined - No created timestamp is provided
        :param kms_key_arn: (experimental) Optional KMS encryption key associated with this memory. Default: undefined - An AWS managed key is used
        :param status: (experimental) The status of the memory. Default: undefined - No status is provided
        :param updated_at: (experimental) When this memory was last updated. Default: undefined - No last updated timestamp is provided

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_bedrock_agentcore_alpha as bedrock_agentcore_alpha
            
            memory_attributes = bedrock_agentcore_alpha.MemoryAttributes(
                memory_arn="memoryArn",
                role_arn="roleArn",
            
                # the properties below are optional
                created_at="createdAt",
                kms_key_arn="kmsKeyArn",
                status="status",
                updated_at="updatedAt"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6a086dd3c259b4f5133e8dcca3563182c7cc9f12c0de8e826898a8aa640669c)
            check_type(argname="argument memory_arn", value=memory_arn, expected_type=type_hints["memory_arn"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument kms_key_arn", value=kms_key_arn, expected_type=type_hints["kms_key_arn"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument updated_at", value=updated_at, expected_type=type_hints["updated_at"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "memory_arn": memory_arn,
            "role_arn": role_arn,
        }
        if created_at is not None:
            self._values["created_at"] = created_at
        if kms_key_arn is not None:
            self._values["kms_key_arn"] = kms_key_arn
        if status is not None:
            self._values["status"] = status
        if updated_at is not None:
            self._values["updated_at"] = updated_at

    @builtins.property
    def memory_arn(self) -> builtins.str:
        '''(experimental) The ARN of the memory.

        :stability: experimental
        :attribute: true
        '''
        result = self._values.get("memory_arn")
        assert result is not None, "Required property 'memory_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''(experimental) The ARN of the IAM role associated to the memory.

        :stability: experimental
        :attribute: true
        '''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The created timestamp of the memory.

        :default: undefined - No created timestamp is provided

        :stability: experimental
        '''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def kms_key_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional KMS encryption key associated with this memory.

        :default: undefined - An AWS managed key is used

        :stability: experimental
        '''
        result = self._values.get("kms_key_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the memory.

        :default: undefined - No status is provided

        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When this memory was last updated.

        :default: undefined - No last updated timestamp is provided

        :stability: experimental
        '''
        result = self._values.get("updated_at")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemoryAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IMemory)
class MemoryBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.MemoryBase",
):
    '''(experimental) Abstract base class for a Memory.

    Contains methods and attributes valid for Memories either created with CDK or imported.

    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__574392a6603a24fac59c9a505b5e2ff912c7921a0c811d31aaf821e33095a259)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants IAM actions to the IAM Principal.

        :param grantee: - The IAM principal to grant permissions to.
        :param actions: - The actions to grant.

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80f21eef09775f5de00521f704cd0b377a899072ad12f31d3c102e3fcba11ff5)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantAdmin")
    def grant_admin(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to manage the control plane of this memory.

        :param grantee: - The IAM principal to grant admin permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:CreateMemory',
        'bedrock-agentcore:GetMemory',
        'bedrock-agentcore:DeleteMemory',
        'bedrock-agentcore:UpdateMemory'] on this.memoryArn

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c6e4dd70011581876e2bb5e8f8c08ac5c3444fd18ed45b7f0cff62c5076e299)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantAdmin", [grantee]))

    @jsii.member(jsii_name="grantDelete")
    def grant_delete(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to delete content on this memory.

        Both Short-Term Memory (STM) and Long-Term Memory (LTM).

        :param grantee: - The IAM principal to grant delete permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:DeleteEvent',
        'bedrock-agentcore:DeleteMemoryRecord'] on this.memoryArn

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6789868eda605d017128a6c6f954d81b5ef91ae498ca9b98f70464d6766b7fdd)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantDelete", [grantee]))

    @jsii.member(jsii_name="grantDeleteLongTermMemory")
    def grant_delete_long_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to delete Long-Term Memory (LTM) content on this memory.

        :param grantee: - The IAM principal to grant delete permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:DeleteMemoryRecord'] on this.memoryArn

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22d835385ded311b3a50da18cd698dd96efa8b025c2ce811f6b2c37cf0dcfd7a)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantDeleteLongTermMemory", [grantee]))

    @jsii.member(jsii_name="grantDeleteShortTermMemory")
    def grant_delete_short_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to delete Short-Term Memory (STM) content on this memory.

        :param grantee: - The IAM principal to grant delete permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:DeleteEvent'] on this.memoryArn

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e45f2d16955307339b561c5f88315e38b6e333658c3c42bf5a60ebfe2401865)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantDeleteShortTermMemory", [grantee]))

    @jsii.member(jsii_name="grantFullAccess")
    def grant_full_access(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to do every action on this memory.

        :param grantee: - The IAM principal to grant full access permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:CreateEvent',
        'bedrock-agentcore:GetEvent',
        'bedrock-agentcore:DeleteEvent',
        'bedrock-agentcore:GetMemoryRecord',
        'bedrock-agentcore:RetrieveMemoryRecords',
        'bedrock-agentcore:ListMemoryRecords',
        'bedrock-agentcore:ListActors',
        'bedrock-agentcore:ListSessions',
        'bedrock-agentcore:CreateMemory',
        'bedrock-agentcore:GetMemory',
        'bedrock-agentcore:DeleteMemory',
        'bedrock-agentcore:UpdateMemory'] on this.memoryArn

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0ec9374ec0867626f333d6a0e1b2e28e0bdb667583aee6e3be29fed5279bb21)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantFullAccess", [grantee]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to read the contents of this memory.

        Both Short-Term Memory (STM) and Long-Term Memory (LTM).

        :param grantee: - The IAM principal to grant read permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:GetMemoryRecord',
        'bedrock-agentcore:RetrieveMemoryRecords',
        'bedrock-agentcore:ListMemoryRecords',
        'bedrock-agentcore:ListActors',
        'bedrock-agentcore:ListSessions] on this.memoryArn

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be1c7af8fe6270d50b6d982667d42ab7e139c4f172018cd2035904bd5d7ff917)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantReadLongTermMemory")
    def grant_read_long_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to read the Long-Term Memory (LTM) contents of this memory.

        :param grantee: - The IAM principal to grant read permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:GetMemoryRecord',
        'bedrock-agentcore:RetrieveMemoryRecords',
        'bedrock-agentcore:ListMemoryRecords',
        'bedrock-agentcore:ListActors',
        'bedrock-agentcore:ListSessions',] on this.memoryArn

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebc2c8cd9c54c3d6983b81accbc7ae829b363a07574e1fe80dac1e83df78ac00)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantReadLongTermMemory", [grantee]))

    @jsii.member(jsii_name="grantReadShortTermMemory")
    def grant_read_short_term_memory(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to read the Short-Term Memory (STM) contents of this memory.

        :param grantee: - The IAM principal to grant read permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:GetEvent',
        'bedrock-agentcore:ListEvents',
        'bedrock-agentcore:ListActors',
        'bedrock-agentcore:ListSessions',] on this.memoryArn

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75b65dac82aa42a649070040d4a89e636efd205f740e9648e93babd0b2fdeee2)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantReadShortTermMemory", [grantee]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the given principal identity permissions to write content to short-term memory.

        :param grantee: - The IAM principal to grant read permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:CreateEvent'] on this.memoryArn

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__590ba37ea58d7dff8c2d3fc8274cc9987427363e687967c1d3958d73cbc53039)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantWrite", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this memory.

        By default, the metric will be calculated as a sum over a period of 5 minutes.
        You can customize this by using the ``statistic`` and ``period`` properties.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f53f70948f0d97aeb01fc6c9fd678ba05fbe2b91bfb844ed7ea119b30028142)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, dimensions, props]))

    @jsii.member(jsii_name="metricErrorsForApiOperation")
    def metric_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of errors for a specific API operation performed on this memory.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9e54bcc7e67cf46e5411aaa6f13470ba871429e3c67f47fa25598bc844c2d35)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricEventCreationCount")
    def metric_event_creation_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Returns the metric containing the number of short-term memory events.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricEventCreationCount", [props]))

    @jsii.member(jsii_name="metricForApiOperation")
    def metric_for_api_operation(
        self,
        metric_name: builtins.str,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric related to the API operation performed on this memory.

        :param metric_name: -
        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61fe7dbf381a793e49e0d24bad4f6af5b13e7d599048ff0dfa6bc01da7c285a9)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricForApiOperation", [metric_name, operation, props]))

    @jsii.member(jsii_name="metricInvocationsForApiOperation")
    def metric_invocations_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of API requests made for a specific memory operation like ``CreateEvent``, ``ListEvents``, ``RetrieveMemoryRecords`` ...

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__285e37e135c8ed6622ae06a06eac22ac25d53d96ce2553b060d7ddf527d730b3)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocationsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricLatencyForApiOperation")
    def metric_latency_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of a specific API operation performed on this memory.

        The latency metric represents the total time elapsed between receiving the request and sending
        the final response token, measuring complete end-to-end processing time.

        For memory creation events specifically, this measures the time from the last CreateEvent
        that met strategy criteria until memory storage is completed.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec8b37ef906686d3aceb55dac9ac696a112df78300ecb5165e0f8c21d6c442b8)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatencyForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricMemoryRecordCreationCount")
    def metric_memory_record_creation_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Returns the metric containing the number of long-term memory records created by the long-term extraction strategies.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricMemoryRecordCreationCount", [props]))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    @abc.abstractmethod
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="memoryArn")
    @abc.abstractmethod
    def memory_arn(self) -> builtins.str:
        '''(experimental) The ARN of the memory resource.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="memoryId")
    @abc.abstractmethod
    def memory_id(self) -> builtins.str:
        '''(experimental) The id of the memory.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    @abc.abstractmethod
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the memory was created.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    @abc.abstractmethod
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that provides permissions for the memory to access AWS services.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    @abc.abstractmethod
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Custom KMS key for encryption (if provided).

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="status")
    @abc.abstractmethod
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the memory.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    @abc.abstractmethod
    def updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the memory was last updated.

        :stability: experimental
        '''
        ...


class _MemoryBaseProxy(
    MemoryBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="memoryArn")
    def memory_arn(self) -> builtins.str:
        '''(experimental) The ARN of the memory resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "memoryArn"))

    @builtins.property
    @jsii.member(jsii_name="memoryId")
    def memory_id(self) -> builtins.str:
        '''(experimental) The id of the memory.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "memoryId"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the memory was created.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that provides permissions for the memory to access AWS services.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Custom KMS key for encryption (if provided).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "kmsKey"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the memory.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the memory was last updated.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedAt"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, MemoryBase).__jsii_proxy_class__ = lambda : _MemoryBaseProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.MemoryProps",
    jsii_struct_bases=[],
    name_mapping={
        "memory_name": "memoryName",
        "description": "description",
        "execution_role": "executionRole",
        "expiration_duration": "expirationDuration",
        "kms_key": "kmsKey",
        "memory_strategies": "memoryStrategies",
        "tags": "tags",
    },
)
class MemoryProps:
    def __init__(
        self,
        *,
        memory_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        expiration_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        memory_strategies: typing.Optional[typing.Sequence[IMemoryStrategy]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for creating a Memory resource.

        :param memory_name: (experimental) The name of the memory Valid characters are a-z, A-Z, 0-9, _ (underscore) The name must start with a letter and can be up to 48 characters long Pattern: [a-zA-Z][a-zA-Z0-9_]{0,47}.
        :param description: (experimental) Optional description for the memory Valid characters are a-z, A-Z, 0-9, _ (underscore), - (hyphen) and spaces The description can have up to 200 characters. Default: - No description
        :param execution_role: (experimental) The IAM role that provides permissions for the memory to access AWS services when using custom strategies. Default: - A new role will be created.
        :param expiration_duration: (experimental) Short-term memory expiration in days (between 7 and 365). Sets the short-term (raw event) memory retention. Events older than the specified duration will expire and no longer be stored. Default: - 90 days
        :param kms_key: (experimental) Custom KMS key to use for encryption. Default: - Your data is encrypted with a key that AWS owns and manages for you
        :param memory_strategies: (experimental) If you need long-term memory for context recall across sessions, you can setup memory extraction strategies to extract the relevant memory from the raw events. Default: - No extraction strategies (short term memory only)
        :param tags: (experimental) Tags (optional) A list of key:value pairs of tags to apply to this memory resource. Default: - no tags

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            # Create a custom execution role
            execution_role = iam.Role(self, "MemoryExecutionRole",
                assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockAgentCoreMemoryBedrockModelInferenceExecutionRolePolicy")
                ]
            )
            
            # Create memory with custom execution role
            memory = agentcore.Memory(self, "MyMemory",
                memory_name="my_memory",
                description="Memory with custom execution role",
                expiration_duration=cdk.Duration.days(90),
                execution_role=execution_role
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12709904e77db162aec81a7042ff51a5ef06724c2d2a50b65427d8cc3d0a4513)
            check_type(argname="argument memory_name", value=memory_name, expected_type=type_hints["memory_name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument expiration_duration", value=expiration_duration, expected_type=type_hints["expiration_duration"])
            check_type(argname="argument kms_key", value=kms_key, expected_type=type_hints["kms_key"])
            check_type(argname="argument memory_strategies", value=memory_strategies, expected_type=type_hints["memory_strategies"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "memory_name": memory_name,
        }
        if description is not None:
            self._values["description"] = description
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if expiration_duration is not None:
            self._values["expiration_duration"] = expiration_duration
        if kms_key is not None:
            self._values["kms_key"] = kms_key
        if memory_strategies is not None:
            self._values["memory_strategies"] = memory_strategies
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def memory_name(self) -> builtins.str:
        '''(experimental) The name of the memory Valid characters are a-z, A-Z, 0-9, _ (underscore) The name must start with a letter and can be up to 48 characters long Pattern: [a-zA-Z][a-zA-Z0-9_]{0,47}.

        :stability: experimental
        '''
        result = self._values.get("memory_name")
        assert result is not None, "Required property 'memory_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional description for the memory Valid characters are a-z, A-Z, 0-9, _ (underscore), - (hyphen) and spaces The description can have up to 200 characters.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that provides permissions for the memory to access AWS services when using custom strategies.

        :default: - A new role will be created.

        :stability: experimental
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def expiration_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Short-term memory expiration in days (between 7 and 365).

        Sets the short-term (raw event) memory retention.
        Events older than the specified duration will expire and no longer be stored.

        :default: - 90 days

        :stability: experimental
        '''
        result = self._values.get("expiration_duration")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Custom KMS key to use for encryption.

        :default: - Your data is encrypted with a key that AWS owns and manages for you

        :stability: experimental
        '''
        result = self._values.get("kms_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def memory_strategies(self) -> typing.Optional[typing.List[IMemoryStrategy]]:
        '''(experimental) If you need long-term memory for context recall across sessions, you can setup memory extraction strategies to extract the relevant memory from the raw events.

        :default: - No extraction strategies (short term memory only)

        :stability: experimental
        '''
        result = self._values.get("memory_strategies")
        return typing.cast(typing.Optional[typing.List[IMemoryStrategy]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Tags (optional) A list of key:value pairs of tags to apply to this memory resource.

        :default: - no tags

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MemoryStrategy(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.MemoryStrategy",
):
    '''(experimental) Factory class for creating memory strategies If you need long-term memory for context recall across sessions, you can setup memory extraction strategies to extract the relevant memory from the raw events.

    Use built-in strategies for quick setup, use built-in strategies with override to specify models and prompt templates.

    :see: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-strategies.html
    :stability: experimental
    :exampleMetadata: fixture=default infused

    Example::

        # Create a custom semantic memory strategy
        custom_semantic_strategy = agentcore.MemoryStrategy.using_semantic(
            name="customSemanticStrategy",
            description="Custom semantic memory strategy",
            namespaces=["/custom/strategies/{memoryStrategyId}/actors/{actorId}"],
            custom_consolidation=agentcore.OverrideConfig(
                model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
                append_to_prompt="Custom consolidation prompt for semantic memory"
            ),
            custom_extraction=agentcore.OverrideConfig(
                model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
                append_to_prompt="Custom extraction prompt for semantic memory"
            )
        )
        
        # Create memory with custom strategy
        memory = agentcore.Memory(self, "MyMemory",
            memory_name="my-custom-memory",
            description="Memory with custom strategy",
            expiration_duration=cdk.Duration.days(90),
            memory_strategies=[custom_semantic_strategy]
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="usingBuiltInSemantic")
    @builtins.classmethod
    def using_built_in_semantic(cls) -> ManagedMemoryStrategy:
        '''(experimental) Default strategies for organizing and extracting memory data, each optimized for specific use cases.

        Distills general facts, concepts, and underlying meanings from raw conversational data, presenting the information in a context-independent format.
        Extracted memory example: In-context learning = task-solving via examples, no training needed.

        :return: A ManagedMemoryStrategy.

        :stability: experimental
        '''
        return typing.cast(ManagedMemoryStrategy, jsii.sinvoke(cls, "usingBuiltInSemantic", []))

    @jsii.member(jsii_name="usingBuiltInSummarization")
    @builtins.classmethod
    def using_built_in_summarization(cls) -> ManagedMemoryStrategy:
        '''(experimental) Default strategies for organizing and extracting memory data, each optimized for specific use cases.

        This strategy compresses conversations into concise overviews, preserving essential context and key insights for quick recall.
        Extracted memory example: Users confused by cloud setup during onboarding.

        :return: A ManagedMemoryStrategy.

        :stability: experimental
        '''
        return typing.cast(ManagedMemoryStrategy, jsii.sinvoke(cls, "usingBuiltInSummarization", []))

    @jsii.member(jsii_name="usingBuiltInUserPreference")
    @builtins.classmethod
    def using_built_in_user_preference(cls) -> ManagedMemoryStrategy:
        '''(experimental) Default strategies for organizing and extracting memory data, each optimized for specific use cases.

        Captures individual preferences, interaction patterns, and personalized settings to enhance future experiences.
        Extracted memory example: User needs clear guidance on cloud storage account connection during onboarding.

        :return: A ManagedMemoryStrategy.

        :stability: experimental
        '''
        return typing.cast(ManagedMemoryStrategy, jsii.sinvoke(cls, "usingBuiltInUserPreference", []))

    @jsii.member(jsii_name="usingSelfManaged")
    @builtins.classmethod
    def using_self_managed(
        cls,
        *,
        invocation_configuration: typing.Union[InvocationConfiguration, typing.Dict[builtins.str, typing.Any]],
        historical_context_window_size: typing.Optional[jsii.Number] = None,
        trigger_conditions: typing.Optional[typing.Union["TriggerConditions", typing.Dict[builtins.str, typing.Any]]] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> "SelfManagedMemoryStrategy":
        '''(experimental) Creates a self-managed memory strategy.

        A self-managed strategy gives you complete control over your memory extraction and consolidation pipelines.

        :param invocation_configuration: (experimental) Invocation configuration for self managed memory strategy.
        :param historical_context_window_size: (experimental) Define the number of previous events to be included when processing memory. A larger history window provides more context from past conversations. Default: 4
        :param trigger_conditions: (experimental) Trigger conditions for self managed memory strategy. Default: - undefined
        :param name: (experimental) The name for the strategy.
        :param description: (experimental) The description of the strategy. Default: - No description

        :return: A SelfManagedMemoryStrategy.

        :stability: experimental
        '''
        config = SelfManagedStrategyProps(
            invocation_configuration=invocation_configuration,
            historical_context_window_size=historical_context_window_size,
            trigger_conditions=trigger_conditions,
            name=name,
            description=description,
        )

        return typing.cast("SelfManagedMemoryStrategy", jsii.sinvoke(cls, "usingSelfManaged", [config]))

    @jsii.member(jsii_name="usingSemantic")
    @builtins.classmethod
    def using_semantic(
        cls,
        *,
        namespaces: typing.Sequence[builtins.str],
        custom_consolidation: typing.Optional[typing.Union["OverrideConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_extraction: typing.Optional[typing.Union["OverrideConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> ManagedMemoryStrategy:
        '''(experimental) Creates a semantic memory strategy with custom configuration.

        Distills general facts, concepts, and underlying meanings from raw conversational data, presenting the information in a context-independent format.
        Extracted memory example: In-context learning = task-solving via examples, no training needed.

        :param namespaces: (experimental) The namespaces for the strategy Represents a namespace for organizing memory data Use a hierarchical format separated by forward slashes (/). Use a hierarchical format separated by forward slashes (/) to organize namespaces logically. You can include these defined variables: - {sessionId} - the user identifier to be created in the CreateEvent API - {memoryStrategyId} - an identifier for an extraction strategy - {sessionId} - an identifier for each session Example namespace path: /strategies/{memoryStrategyId}/actions/{actionId}/sessions/{sessionId} After memory creation, this namespace might look like: /actor/actor-3afc5aa8fef9/strategy/summarization-fy5c5fwc7/session/session-qj7tpd1kvr8
        :param custom_consolidation: (experimental) The configuration for the custom consolidation. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction
        :param custom_extraction: (experimental) The configuration for the custom extraction. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction
        :param name: (experimental) The name for the strategy.
        :param description: (experimental) The description of the strategy. Default: - No description

        :return: A ManagedMemoryStrategy.

        :stability: experimental
        '''
        config = ManagedStrategyProps(
            namespaces=namespaces,
            custom_consolidation=custom_consolidation,
            custom_extraction=custom_extraction,
            name=name,
            description=description,
        )

        return typing.cast(ManagedMemoryStrategy, jsii.sinvoke(cls, "usingSemantic", [config]))

    @jsii.member(jsii_name="usingSummarization")
    @builtins.classmethod
    def using_summarization(
        cls,
        *,
        namespaces: typing.Sequence[builtins.str],
        custom_consolidation: typing.Optional[typing.Union["OverrideConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_extraction: typing.Optional[typing.Union["OverrideConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> ManagedMemoryStrategy:
        '''(experimental) Creates a summarization memory strategy with custom configuration.

        This strategy compresses conversations into concise overviews, preserving essential context and key insights for quick recall.
        Extracted memory example: Users confused by cloud setup during onboarding.

        :param namespaces: (experimental) The namespaces for the strategy Represents a namespace for organizing memory data Use a hierarchical format separated by forward slashes (/). Use a hierarchical format separated by forward slashes (/) to organize namespaces logically. You can include these defined variables: - {sessionId} - the user identifier to be created in the CreateEvent API - {memoryStrategyId} - an identifier for an extraction strategy - {sessionId} - an identifier for each session Example namespace path: /strategies/{memoryStrategyId}/actions/{actionId}/sessions/{sessionId} After memory creation, this namespace might look like: /actor/actor-3afc5aa8fef9/strategy/summarization-fy5c5fwc7/session/session-qj7tpd1kvr8
        :param custom_consolidation: (experimental) The configuration for the custom consolidation. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction
        :param custom_extraction: (experimental) The configuration for the custom extraction. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction
        :param name: (experimental) The name for the strategy.
        :param description: (experimental) The description of the strategy. Default: - No description

        :return: A ManagedMemoryStrategy.

        :stability: experimental
        '''
        config = ManagedStrategyProps(
            namespaces=namespaces,
            custom_consolidation=custom_consolidation,
            custom_extraction=custom_extraction,
            name=name,
            description=description,
        )

        return typing.cast(ManagedMemoryStrategy, jsii.sinvoke(cls, "usingSummarization", [config]))

    @jsii.member(jsii_name="usingUserPreference")
    @builtins.classmethod
    def using_user_preference(
        cls,
        *,
        namespaces: typing.Sequence[builtins.str],
        custom_consolidation: typing.Optional[typing.Union["OverrideConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        custom_extraction: typing.Optional[typing.Union["OverrideConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> ManagedMemoryStrategy:
        '''(experimental) Creates a user preference memory strategy with custom configuration.

        Captures individual preferences, interaction patterns, and personalized settings to enhance future experiences.
        Extracted memory example: User needs clear guidance on cloud storage account connection during onboarding.

        :param namespaces: (experimental) The namespaces for the strategy Represents a namespace for organizing memory data Use a hierarchical format separated by forward slashes (/). Use a hierarchical format separated by forward slashes (/) to organize namespaces logically. You can include these defined variables: - {sessionId} - the user identifier to be created in the CreateEvent API - {memoryStrategyId} - an identifier for an extraction strategy - {sessionId} - an identifier for each session Example namespace path: /strategies/{memoryStrategyId}/actions/{actionId}/sessions/{sessionId} After memory creation, this namespace might look like: /actor/actor-3afc5aa8fef9/strategy/summarization-fy5c5fwc7/session/session-qj7tpd1kvr8
        :param custom_consolidation: (experimental) The configuration for the custom consolidation. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction
        :param custom_extraction: (experimental) The configuration for the custom extraction. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction
        :param name: (experimental) The name for the strategy.
        :param description: (experimental) The description of the strategy. Default: - No description

        :return: A ManagedMemoryStrategy.

        :stability: experimental
        '''
        config = ManagedStrategyProps(
            namespaces=namespaces,
            custom_consolidation=custom_consolidation,
            custom_extraction=custom_extraction,
            name=name,
            description=description,
        )

        return typing.cast(ManagedMemoryStrategy, jsii.sinvoke(cls, "usingUserPreference", [config]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.MemoryStrategyCommonProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "description": "description"},
)
class MemoryStrategyCommonProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Configuration parameters common for any memory strategy.

        :param name: (experimental) The name for the strategy.
        :param description: (experimental) The description of the strategy. Default: - No description

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_bedrock_agentcore_alpha as bedrock_agentcore_alpha
            
            memory_strategy_common_props = bedrock_agentcore_alpha.MemoryStrategyCommonProps(
                name="name",
            
                # the properties below are optional
                description="description"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33bd2546f76cfe4b81d759a553b1092fab937231ba1d88a09e69aed7c50ee949)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name for the strategy.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the strategy.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MemoryStrategyCommonProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.MemoryStrategyType")
class MemoryStrategyType(enum.Enum):
    '''(experimental) Long-term memory extraction strategy types.

    :stability: experimental
    '''

    SUMMARIZATION = "SUMMARIZATION"
    '''(experimental) Summarization strategy - extracts concise summaries to preserve critical context and key insights.

    :stability: experimental
    '''
    SEMANTIC = "SEMANTIC"
    '''(experimental) Semantic memory strategy - extracts general factual knowledge, concepts and meanings from raw conversations using vector embeddings for similarity search.

    :stability: experimental
    '''
    USER_PREFERENCE = "USER_PREFERENCE"
    '''(experimental) User preferences strategy - extracts user behavior patterns from raw conversations.

    :stability: experimental
    '''
    CUSTOM = "CUSTOM"
    '''(experimental) Customize memory processing through custom foundation model and prompt templates.

    :stability: experimental
    '''


class NetworkConfiguration(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.NetworkConfiguration",
):
    '''(experimental) Abstract base class for network configuration.

    :stability: experimental
    '''

    def __init__(
        self,
        mode: builtins.str,
        scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Creates a new network configuration.

        :param mode: - the network mode to use for the tool.
        :param scope: -
        :param vpc: (experimental) The VPC to deploy the resource to.
        :param allow_all_outbound: (experimental) Whether to allow the resource to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the resource to connect to network targets. Do not specify this property if the ``securityGroups`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param security_groups: (experimental) The list of security groups to associate with the resource's network interfaces. Only used if 'vpc' is supplied. Default: - If the resource is placed within a VPC and a security group is not specified by this prop, a dedicated security group will be created for this resource.
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1156fe37fe7149a4f863e83246fb36b82ce35366fd78287a7abd74852fa9ecd)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        vpc_config = VpcConfigProps(
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [mode, scope, vpc_config])

    @builtins.property
    @jsii.member(jsii_name="networkMode")
    def network_mode(self) -> builtins.str:
        '''(experimental) The network mode to use.

        Configure the security level for agent
        execution to control access, isolate resources, and protect sensitive data.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "networkMode"))

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Connections]:
        '''(experimental) The connections object to the network.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.Connections], jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional[_constructs_77d1e7e8.Construct]:
        '''(experimental) The scope to create the resource in.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_constructs_77d1e7e8.Construct], jsii.get(self, "scope"))

    @builtins.property
    @jsii.member(jsii_name="vpcSubnets")
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) The VPC subnets to use.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], jsii.get(self, "vpcSubnets"))


class _NetworkConfigurationProxy(NetworkConfiguration):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, NetworkConfiguration).__jsii_proxy_class__ = lambda : _NetworkConfigurationProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.OverrideConfig",
    jsii_struct_bases=[],
    name_mapping={"append_to_prompt": "appendToPrompt", "model": "model"},
)
class OverrideConfig:
    def __init__(
        self,
        *,
        append_to_prompt: builtins.str,
        model: _aws_cdk_aws_bedrock_alpha_3753ded9.IBedrockInvokable,
    ) -> None:
        '''(experimental) Configuration for overriding model and prompt template.

        :param append_to_prompt: (experimental) The prompt that will be appended to the system prompt to define the model's memory consolidation/extraction strategy. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. You can use the default user prompt or create a customized one.
        :param model: (experimental) The model to use for consolidation/extraction.

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            # Create a custom semantic memory strategy
            custom_semantic_strategy = agentcore.MemoryStrategy.using_semantic(
                name="customSemanticStrategy",
                description="Custom semantic memory strategy",
                namespaces=["/custom/strategies/{memoryStrategyId}/actors/{actorId}"],
                custom_consolidation=agentcore.OverrideConfig(
                    model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
                    append_to_prompt="Custom consolidation prompt for semantic memory"
                ),
                custom_extraction=agentcore.OverrideConfig(
                    model=bedrock.BedrockFoundationModel.ANTHROPIC_CLAUDE_3_5_SONNET_V1_0,
                    append_to_prompt="Custom extraction prompt for semantic memory"
                )
            )
            
            # Create memory with custom strategy
            memory = agentcore.Memory(self, "MyMemory",
                memory_name="my-custom-memory",
                description="Memory with custom strategy",
                expiration_duration=cdk.Duration.days(90),
                memory_strategies=[custom_semantic_strategy]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3dfe3652e8566d6eb013039b79337022b12d64febe65e86a809b46dff375947)
            check_type(argname="argument append_to_prompt", value=append_to_prompt, expected_type=type_hints["append_to_prompt"])
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "append_to_prompt": append_to_prompt,
            "model": model,
        }

    @builtins.property
    def append_to_prompt(self) -> builtins.str:
        '''(experimental) The prompt that will be appended to the system prompt to define the model's memory consolidation/extraction strategy.

        This configuration provides customization to how the model identifies and extracts
        relevant information for memory storage. You can use the default user prompt or create a customized one.

        :see: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/system-prompts.html
        :stability: experimental
        '''
        result = self._values.get("append_to_prompt")
        assert result is not None, "Required property 'append_to_prompt' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model(self) -> _aws_cdk_aws_bedrock_alpha_3753ded9.IBedrockInvokable:
        '''(experimental) The model to use for consolidation/extraction.

        :stability: experimental
        '''
        result = self._values.get("model")
        assert result is not None, "Required property 'model' is missing"
        return typing.cast(_aws_cdk_aws_bedrock_alpha_3753ded9.IBedrockInvokable, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OverrideConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.ProtocolType")
class ProtocolType(enum.Enum):
    '''(experimental) Protocol configuration for Agent Runtime.

    :stability: experimental
    '''

    MCP = "MCP"
    '''(experimental) Model Context Protocol.

    :stability: experimental
    '''
    HTTP = "HTTP"
    '''(experimental) HTTP protocol.

    :stability: experimental
    '''
    A2A = "A2A"
    '''(experimental) A2A protocol.

    :stability: experimental
    '''


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.RecordingConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "s3_location": "s3Location"},
)
class RecordingConfig:
    def __init__(
        self,
        *,
        enabled: typing.Optional[builtins.bool] = None,
        s3_location: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Recording configuration for browser.

        :param enabled: (experimental) Whether recording is enabled. Default: - false
        :param s3_location: (experimental) S3 Location Configuration. Default: - undefined

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            # Create an S3 bucket for recordings
            recording_bucket = s3.Bucket(self, "RecordingBucket",
                bucket_name="my-browser-recordings",
                removal_policy=RemovalPolicy.DESTROY
            )
            
            # Create browser with recording enabled
            browser = agentcore.BrowserCustom(self, "MyBrowser",
                browser_custom_name="my_browser",
                description="Browser with recording enabled",
                network_configuration=agentcore.BrowserNetworkConfiguration.using_public_network(),
                recording_config=agentcore.RecordingConfig(
                    enabled=True,
                    s3_location=s3.Location(
                        bucket_name=recording_bucket.bucket_name,
                        object_key="browser-recordings/"
                    )
                )
            )
        '''
        if isinstance(s3_location, dict):
            s3_location = _aws_cdk_aws_s3_ceddda9d.Location(**s3_location)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__847016f3fc41e4cdc9b08f4aeed6b6521f23c2c1ef8b55de56db5d14f7dbdc82)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument s3_location", value=s3_location, expected_type=type_hints["s3_location"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if s3_location is not None:
            self._values["s3_location"] = s3_location

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether recording is enabled.

        :default: - false

        :stability: experimental
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def s3_location(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Location]:
        '''(experimental) S3 Location Configuration.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("s3_location")
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Location], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RecordingConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RuntimeAuthorizerConfiguration(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.RuntimeAuthorizerConfiguration",
):
    '''(experimental) Abstract base class for runtime authorizer configurations.

    Provides static factory methods to create different authentication types.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        repository = ecr.Repository(self, "TestRepository",
            repository_name="test-agent-runtime"
        )
        agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")
        
        runtime = agentcore.Runtime(self, "MyAgentRuntime",
            runtime_name="myAgent",
            agent_runtime_artifact=agent_runtime_artifact,
            authorizer_configuration=agentcore.RuntimeAuthorizerConfiguration.using_oAuth("https://github.com/.well-known/openid-configuration", "oauth_client_123")
        )
    '''

    def __init__(self) -> None:
        '''
        :stability: experimental
        '''
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="usingCognito")
    @builtins.classmethod
    def using_cognito(
        cls,
        user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
        user_pool_clients: typing.Sequence[_aws_cdk_aws_cognito_ceddda9d.IUserPoolClient],
        allowed_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "RuntimeAuthorizerConfiguration":
        '''(experimental) Use AWS Cognito User Pool authentication.

        Validates Cognito-issued JWT tokens.

        :param user_pool: The Cognito User Pool.
        :param user_pool_clients: -
        :param allowed_audience: Optional array of allowed audiences.

        :return: RuntimeAuthorizerConfiguration for Cognito authentication

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b924023484b6dec8c84698f52f4e325bbda80efa65704ec656d07d774f0f360a)
            check_type(argname="argument user_pool", value=user_pool, expected_type=type_hints["user_pool"])
            check_type(argname="argument user_pool_clients", value=user_pool_clients, expected_type=type_hints["user_pool_clients"])
            check_type(argname="argument allowed_audience", value=allowed_audience, expected_type=type_hints["allowed_audience"])
        return typing.cast("RuntimeAuthorizerConfiguration", jsii.sinvoke(cls, "usingCognito", [user_pool, user_pool_clients, allowed_audience]))

    @jsii.member(jsii_name="usingIAM")
    @builtins.classmethod
    def using_iam(cls) -> "RuntimeAuthorizerConfiguration":
        '''(experimental) Use IAM authentication (default).

        Requires AWS credentials to sign requests using SigV4.

        :return: RuntimeAuthorizerConfiguration for IAM authentication

        :stability: experimental
        '''
        return typing.cast("RuntimeAuthorizerConfiguration", jsii.sinvoke(cls, "usingIAM", []))

    @jsii.member(jsii_name="usingJWT")
    @builtins.classmethod
    def using_jwt(
        cls,
        discovery_url: builtins.str,
        allowed_clients: typing.Optional[typing.Sequence[builtins.str]] = None,
        allowed_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "RuntimeAuthorizerConfiguration":
        '''(experimental) Use custom JWT authentication.

        Validates JWT tokens against the specified OIDC provider.

        :param discovery_url: The OIDC discovery URL (must end with /.well-known/openid-configuration).
        :param allowed_clients: Optional array of allowed client IDs.
        :param allowed_audience: Optional array of allowed audiences.

        :return: RuntimeAuthorizerConfiguration for JWT authentication

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ac01ece0cc4140cb0b2a31ed95c6b9e03284a2363131d8f59958f4506fdec5f)
            check_type(argname="argument discovery_url", value=discovery_url, expected_type=type_hints["discovery_url"])
            check_type(argname="argument allowed_clients", value=allowed_clients, expected_type=type_hints["allowed_clients"])
            check_type(argname="argument allowed_audience", value=allowed_audience, expected_type=type_hints["allowed_audience"])
        return typing.cast("RuntimeAuthorizerConfiguration", jsii.sinvoke(cls, "usingJWT", [discovery_url, allowed_clients, allowed_audience]))

    @jsii.member(jsii_name="usingOAuth")
    @builtins.classmethod
    def using_o_auth(
        cls,
        discovery_url: builtins.str,
        client_id: builtins.str,
        allowed_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> "RuntimeAuthorizerConfiguration":
        '''(experimental) Use OAuth 2.0 authentication. Supports various OAuth providers.

        :param discovery_url: The OIDC discovery URL (must end with /.well-known/openid-configuration).
        :param client_id: OAuth client ID.
        :param allowed_audience: Optional array of allowed audiences.

        :return: RuntimeAuthorizerConfiguration for OAuth authentication

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0b8de9eb8f6b27c5ad0708ddadcf0e5e78987856a5b94b421cb1abbcc761229)
            check_type(argname="argument discovery_url", value=discovery_url, expected_type=type_hints["discovery_url"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument allowed_audience", value=allowed_audience, expected_type=type_hints["allowed_audience"])
        return typing.cast("RuntimeAuthorizerConfiguration", jsii.sinvoke(cls, "usingOAuth", [discovery_url, client_id, allowed_audience]))


class _RuntimeAuthorizerConfigurationProxy(RuntimeAuthorizerConfiguration):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, RuntimeAuthorizerConfiguration).__jsii_proxy_class__ = lambda : _RuntimeAuthorizerConfigurationProxy


@jsii.implements(IBedrockAgentRuntime)
class RuntimeBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.RuntimeBase",
):
    '''(experimental) Base class for Agent Runtime.

    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16350f8e803148ae58824c157d92d6b5b360c3802a4018cc1e88f99466e7fa95)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="addToRolePolicy")
    def add_to_role_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> IBedrockAgentRuntime:
        '''(experimental) Adds a policy statement to the runtime's execution role.

        :param statement: The IAM policy statement to add.

        :return: The runtime instance for chaining

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7231f6dcdd2551159f4e644a7b39271f091fade67469f9bf285044a8c4c90b60)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(IBedrockAgentRuntime, jsii.invoke(self, "addToRolePolicy", [statement]))

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        actions: typing.Sequence[builtins.str],
        resources: typing.Sequence[builtins.str],
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant the runtime specific actions on AWS resources.

        :param actions: The actions to grant.
        :param resources: The resource ARNs to grant access to.

        :return: The Grant object for chaining

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87eb6e84d44b507957213f90c634b593ff68893ef29137a6154e73fa53e18e18)
            check_type(argname="argument actions", value=actions, expected_type=type_hints["actions"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [actions, resources]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal to invoke this runtime both directly and on behalf of users Grants both bedrock-agentcore:InvokeAgentRuntime and bedrock-agentcore:InvokeAgentRuntimeForUser permissions.

        :param grantee: The principal to grant access to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f464dbb8ec8dc44c2f152bffa0fe6b7e25a72226db47d4575639ab76a3ee504b)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvoke", [grantee]))

    @jsii.member(jsii_name="grantInvokeRuntime")
    def grant_invoke_runtime(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal to invoke this runtime Grants the bedrock-agentcore:InvokeAgentRuntime permission.

        :param grantee: The principal to grant access to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23262a416c2bde8ca6024d06971509afa97486440111e79dfae8c143d05ed9be)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvokeRuntime", [grantee]))

    @jsii.member(jsii_name="grantInvokeRuntimeForUser")
    def grant_invoke_runtime_for_user(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Permits an IAM principal to invoke this runtime on behalf of a user Grants the bedrock-agentcore:InvokeAgentRuntimeForUser permission Required when using the X-Amzn-Bedrock-AgentCore-Runtime-User-Id header.

        :param grantee: The principal to grant access to.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__894ad60671ea950414fd0416fead36cee5e0bc1348fcb31b422ba8e37ea00c08)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvokeRuntimeForUser", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this agent runtime.

        By default, the metric will be calculated as a sum over a period of 5 minutes.
        You can customize this by using the ``statistic`` and ``period`` properties.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6a2aba3c163e6d2d8cfa3127ef4170f55abf85a15cea83297552f1fe625776d)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, dimensions, props]))

    @jsii.member(jsii_name="metricInvocations")
    def metric_invocations(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of invocations for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocations", [props]))

    @jsii.member(jsii_name="metricInvocationsAggregated")
    def metric_invocations_aggregated(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of invocations across all resources.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocationsAggregated", [props]))

    @jsii.member(jsii_name="metricLatency")
    def metric_latency(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric measuring the latency of requests for this agent runtime.

        The latency metric represents the total time elapsed between receiving the request
        and sending the final response token, representing complete end-to-end processing time.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatency", [props]))

    @jsii.member(jsii_name="metricSessionCount")
    def metric_session_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of agent sessions for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSessionCount", [props]))

    @jsii.member(jsii_name="metricSessionsAggregated")
    def metric_sessions_aggregated(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of sessions across all resources.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSessionsAggregated", [props]))

    @jsii.member(jsii_name="metricSystemErrors")
    def metric_system_errors(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of system errors for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSystemErrors", [props]))

    @jsii.member(jsii_name="metricThrottles")
    def metric_throttles(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of throttled requests for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricThrottles", [props]))

    @jsii.member(jsii_name="metricTotalErrors")
    def metric_total_errors(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the total number of errors (system + user) for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTotalErrors", [props]))

    @jsii.member(jsii_name="metricUserErrors")
    def metric_user_errors(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return a metric containing the number of user errors for this agent runtime.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricUserErrors", [props]))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    @abc.abstractmethod
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent runtime resource - Format ``arn:${Partition}:bedrock-agentcore:${Region}:${Account}:runtime/${RuntimeId}``.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeId")
    @abc.abstractmethod
    def agent_runtime_id(self) -> builtins.str:
        '''(experimental) The ID of the agent runtime.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeName")
    @abc.abstractmethod
    def agent_runtime_name(self) -> builtins.str:
        '''(experimental) The name of the agent runtime.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) An accessor for the Connections object that will fail if this Runtime does not have a VPC configured.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    @abc.abstractmethod
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="role")
    @abc.abstractmethod
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the agent runtime.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeVersion")
    @abc.abstractmethod
    def agent_runtime_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of the agent runtime.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentStatus")
    @abc.abstractmethod
    def agent_status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the agent runtime.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    @abc.abstractmethod
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was created.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    @abc.abstractmethod
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was last updated.

        :stability: experimental
        '''
        ...


class _RuntimeBaseProxy(
    RuntimeBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent runtime resource - Format ``arn:${Partition}:bedrock-agentcore:${Region}:${Account}:runtime/${RuntimeId}``.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeArn"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeId")
    def agent_runtime_id(self) -> builtins.str:
        '''(experimental) The ID of the agent runtime.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeId"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeName")
    def agent_runtime_name(self) -> builtins.str:
        '''(experimental) The name of the agent runtime.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeName"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the agent runtime.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeVersion")
    def agent_runtime_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of the agent runtime.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentRuntimeVersion"))

    @builtins.property
    @jsii.member(jsii_name="agentStatus")
    def agent_status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the agent runtime.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentStatus"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was created.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The time at which the runtime was last updated.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, RuntimeBase).__jsii_proxy_class__ = lambda : _RuntimeBaseProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.RuntimeEndpointAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "agent_runtime_arn": "agentRuntimeArn",
        "agent_runtime_endpoint_arn": "agentRuntimeEndpointArn",
        "endpoint_name": "endpointName",
        "created_at": "createdAt",
        "description": "description",
        "endpoint_id": "endpointId",
        "last_updated_at": "lastUpdatedAt",
        "live_version": "liveVersion",
        "status": "status",
        "target_version": "targetVersion",
    },
)
class RuntimeEndpointAttributes:
    def __init__(
        self,
        *,
        agent_runtime_arn: builtins.str,
        agent_runtime_endpoint_arn: builtins.str,
        endpoint_name: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        endpoint_id: typing.Optional[builtins.str] = None,
        last_updated_at: typing.Optional[builtins.str] = None,
        live_version: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        target_version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Attributes for importing an existing Runtime Endpoint.

        :param agent_runtime_arn: (experimental) The ARN of the parent agent runtime.
        :param agent_runtime_endpoint_arn: (experimental) The ARN of the runtime endpoint.
        :param endpoint_name: (experimental) The name of the runtime endpoint.
        :param created_at: (experimental) When the endpoint was created. Default: - Creation time not available
        :param description: (experimental) The description of the runtime endpoint. Default: - No description
        :param endpoint_id: (experimental) The unique identifier of the runtime endpoint. Default: - Endpoint ID not available
        :param last_updated_at: (experimental) When the endpoint was last updated. Default: - Last update time not available
        :param live_version: (experimental) The live version of the agent runtime that is currently serving requests. Default: - Live version not available
        :param status: (experimental) The current status of the runtime endpoint. Default: - Status not available
        :param target_version: (experimental) The target version the endpoint is transitioning to (during updates). Default: - Target version not available

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_bedrock_agentcore_alpha as bedrock_agentcore_alpha
            
            runtime_endpoint_attributes = bedrock_agentcore_alpha.RuntimeEndpointAttributes(
                agent_runtime_arn="agentRuntimeArn",
                agent_runtime_endpoint_arn="agentRuntimeEndpointArn",
                endpoint_name="endpointName",
            
                # the properties below are optional
                created_at="createdAt",
                description="description",
                endpoint_id="endpointId",
                last_updated_at="lastUpdatedAt",
                live_version="liveVersion",
                status="status",
                target_version="targetVersion"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8f995850b550d0ef0b0c5967813f910df0c54b53b6273e50eef58f9c9a599ff)
            check_type(argname="argument agent_runtime_arn", value=agent_runtime_arn, expected_type=type_hints["agent_runtime_arn"])
            check_type(argname="argument agent_runtime_endpoint_arn", value=agent_runtime_endpoint_arn, expected_type=type_hints["agent_runtime_endpoint_arn"])
            check_type(argname="argument endpoint_name", value=endpoint_name, expected_type=type_hints["endpoint_name"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument endpoint_id", value=endpoint_id, expected_type=type_hints["endpoint_id"])
            check_type(argname="argument last_updated_at", value=last_updated_at, expected_type=type_hints["last_updated_at"])
            check_type(argname="argument live_version", value=live_version, expected_type=type_hints["live_version"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument target_version", value=target_version, expected_type=type_hints["target_version"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "agent_runtime_arn": agent_runtime_arn,
            "agent_runtime_endpoint_arn": agent_runtime_endpoint_arn,
            "endpoint_name": endpoint_name,
        }
        if created_at is not None:
            self._values["created_at"] = created_at
        if description is not None:
            self._values["description"] = description
        if endpoint_id is not None:
            self._values["endpoint_id"] = endpoint_id
        if last_updated_at is not None:
            self._values["last_updated_at"] = last_updated_at
        if live_version is not None:
            self._values["live_version"] = live_version
        if status is not None:
            self._values["status"] = status
        if target_version is not None:
            self._values["target_version"] = target_version

    @builtins.property
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the parent agent runtime.

        :stability: experimental
        '''
        result = self._values.get("agent_runtime_arn")
        assert result is not None, "Required property 'agent_runtime_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_runtime_endpoint_arn(self) -> builtins.str:
        '''(experimental) The ARN of the runtime endpoint.

        :stability: experimental
        '''
        result = self._values.get("agent_runtime_endpoint_arn")
        assert result is not None, "Required property 'agent_runtime_endpoint_arn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint_name(self) -> builtins.str:
        '''(experimental) The name of the runtime endpoint.

        :stability: experimental
        '''
        result = self._values.get("endpoint_name")
        assert result is not None, "Required property 'endpoint_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When the endpoint was created.

        :default: - Creation time not available

        :stability: experimental
        '''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the runtime endpoint.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def endpoint_id(self) -> typing.Optional[builtins.str]:
        '''(experimental) The unique identifier of the runtime endpoint.

        :default: - Endpoint ID not available

        :stability: experimental
        '''
        result = self._values.get("endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When the endpoint was last updated.

        :default: - Last update time not available

        :stability: experimental
        '''
        result = self._values.get("last_updated_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def live_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The live version of the agent runtime that is currently serving requests.

        :default: - Live version not available

        :stability: experimental
        '''
        result = self._values.get("live_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the runtime endpoint.

        :default: - Status not available

        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The target version the endpoint is transitioning to (during updates).

        :default: - Target version not available

        :stability: experimental
        '''
        result = self._values.get("target_version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuntimeEndpointAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IRuntimeEndpoint)
class RuntimeEndpointBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.RuntimeEndpointBase",
):
    '''(experimental) Base class for Runtime Endpoint.

    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07caa672d91c2d444bbd6350d0c5232e8b425f0f99ff16fa910ac554ef216410)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    @abc.abstractmethod
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the parent agent runtime.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeEndpointArn")
    @abc.abstractmethod
    def agent_runtime_endpoint_arn(self) -> builtins.str:
        '''(experimental) The ARN of the runtime endpoint resource.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="endpointName")
    @abc.abstractmethod
    def endpoint_name(self) -> builtins.str:
        '''(experimental) The name of the runtime endpoint.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    @abc.abstractmethod
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When the endpoint was created.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="description")
    @abc.abstractmethod
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the runtime endpoint.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="liveVersion")
    @abc.abstractmethod
    def live_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The live version of the agent runtime that is currently serving requests.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="status")
    @abc.abstractmethod
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the runtime endpoint.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="targetVersion")
    @abc.abstractmethod
    def target_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The target version the endpoint is transitioning to (during updates).

        :stability: experimental
        '''
        ...


class _RuntimeEndpointBaseProxy(
    RuntimeEndpointBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the parent agent runtime.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeArn"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeEndpointArn")
    def agent_runtime_endpoint_arn(self) -> builtins.str:
        '''(experimental) The ARN of the runtime endpoint resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeEndpointArn"))

    @builtins.property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> builtins.str:
        '''(experimental) The name of the runtime endpoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointName"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When the endpoint was created.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the runtime endpoint.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="liveVersion")
    def live_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The live version of the agent runtime that is currently serving requests.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "liveVersion"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The current status of the runtime endpoint.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="targetVersion")
    def target_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The target version the endpoint is transitioning to (during updates).

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetVersion"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, RuntimeEndpointBase).__jsii_proxy_class__ = lambda : _RuntimeEndpointBaseProxy


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.RuntimeEndpointProps",
    jsii_struct_bases=[],
    name_mapping={
        "agent_runtime_id": "agentRuntimeId",
        "endpoint_name": "endpointName",
        "agent_runtime_version": "agentRuntimeVersion",
        "description": "description",
        "tags": "tags",
    },
)
class RuntimeEndpointProps:
    def __init__(
        self,
        *,
        agent_runtime_id: builtins.str,
        endpoint_name: builtins.str,
        agent_runtime_version: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for creating a Bedrock Agent Core Runtime Endpoint resource.

        :param agent_runtime_id: (experimental) The ID of the agent runtime to associate with this endpoint This is the unique identifier of the runtime resource Pattern: ^[a-zA-Z][a-zA-Z0-9_]{0,99}-[a-zA-Z0-9]{10}$.
        :param endpoint_name: (experimental) The name of the agent runtime endpoint Valid characters are a-z, A-Z, 0-9, _ (underscore) Must start with a letter and can be up to 48 characters long Pattern: ^[a-zA-Z][a-zA-Z0-9_]{0,47}$.
        :param agent_runtime_version: (experimental) The version of the agent runtime to use for this endpoint If not specified, the endpoint will point to version "1" of the runtime. Pattern: ^([1-9][0-9]{0,4})$ Default: "1"
        :param description: (experimental) Optional description for the agent runtime endpoint Length Minimum: 1 , Maximum: 256. Default: - No description
        :param tags: (experimental) Tags for the agent runtime endpoint A list of key:value pairs of tags to apply to this RuntimeEndpoint resource Pattern: ^[a-zA-Z0-9\\s._:/=+@-]*$. Default: {} - no tags

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Reference an existing runtime by its ID
            existing_runtime_id = "abc123-runtime-id" # The ID of an existing runtime
            
            # Create a standalone endpoint
            endpoint = agentcore.RuntimeEndpoint(self, "MyEndpoint",
                endpoint_name="production",
                agent_runtime_id=existing_runtime_id,
                agent_runtime_version="1",  # Specify which version to use
                description="Production endpoint for existing runtime"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7edf14b5674c2c3647a66c54aa24ffa82abf23b571539cd8f02aa354e64da16a)
            check_type(argname="argument agent_runtime_id", value=agent_runtime_id, expected_type=type_hints["agent_runtime_id"])
            check_type(argname="argument endpoint_name", value=endpoint_name, expected_type=type_hints["endpoint_name"])
            check_type(argname="argument agent_runtime_version", value=agent_runtime_version, expected_type=type_hints["agent_runtime_version"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "agent_runtime_id": agent_runtime_id,
            "endpoint_name": endpoint_name,
        }
        if agent_runtime_version is not None:
            self._values["agent_runtime_version"] = agent_runtime_version
        if description is not None:
            self._values["description"] = description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def agent_runtime_id(self) -> builtins.str:
        '''(experimental) The ID of the agent runtime to associate with this endpoint This is the unique identifier of the runtime resource Pattern: ^[a-zA-Z][a-zA-Z0-9_]{0,99}-[a-zA-Z0-9]{10}$.

        :stability: experimental
        '''
        result = self._values.get("agent_runtime_id")
        assert result is not None, "Required property 'agent_runtime_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint_name(self) -> builtins.str:
        '''(experimental) The name of the agent runtime endpoint Valid characters are a-z, A-Z, 0-9, _ (underscore) Must start with a letter and can be up to 48 characters long Pattern: ^[a-zA-Z][a-zA-Z0-9_]{0,47}$.

        :stability: experimental
        '''
        result = self._values.get("endpoint_name")
        assert result is not None, "Required property 'endpoint_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_runtime_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of the agent runtime to use for this endpoint If not specified, the endpoint will point to version "1" of the runtime.

        Pattern: ^([1-9][0-9]{0,4})$

        :default: "1"

        :stability: experimental
        '''
        result = self._values.get("agent_runtime_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional description for the agent runtime endpoint Length Minimum: 1 ,  Maximum: 256.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Tags for the agent runtime endpoint A list of key:value pairs of tags to apply to this RuntimeEndpoint resource Pattern: ^[a-zA-Z0-9\\s._:/=+@-]*$.

        :default: {} - no tags

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuntimeEndpointProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RuntimeNetworkConfiguration(
    NetworkConfiguration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.RuntimeNetworkConfiguration",
):
    '''(experimental) Network configuration for the Runtime.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        repository = ecr.Repository(self, "TestRepository",
            repository_name="test-agent-runtime"
        )
        agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")
        
        # Create or use an existing VPC
        vpc = ec2.Vpc(self, "MyVpc",
            max_azs=2
        )
        
        # Configure runtime with VPC
        runtime = agentcore.Runtime(self, "MyAgentRuntime",
            runtime_name="myAgent",
            agent_runtime_artifact=agent_runtime_artifact,
            network_configuration=agentcore.RuntimeNetworkConfiguration.using_vpc(self,
                vpc=vpc,
                vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
            )
        )
    '''

    def __init__(
        self,
        mode: builtins.str,
        scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Creates a new network configuration.

        :param mode: - the network mode to use for the tool.
        :param scope: -
        :param vpc: (experimental) The VPC to deploy the resource to.
        :param allow_all_outbound: (experimental) Whether to allow the resource to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the resource to connect to network targets. Do not specify this property if the ``securityGroups`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param security_groups: (experimental) The list of security groups to associate with the resource's network interfaces. Only used if 'vpc' is supplied. Default: - If the resource is placed within a VPC and a security group is not specified by this prop, a dedicated security group will be created for this resource.
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3fca872b84d08855284949a94ef7ceab6679568661613e4224125dbf7add5d5)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        vpc_config = VpcConfigProps(
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [mode, scope, vpc_config])

    @jsii.member(jsii_name="usingPublicNetwork")
    @builtins.classmethod
    def using_public_network(cls) -> "RuntimeNetworkConfiguration":
        '''(experimental) Creates a public network configuration.

        PUBLIC is the default network mode.

        :return:

        A RuntimeNetworkConfiguration.
        Run the runtime in a public environment with internet access, suitable for less sensitive or open-use scenarios.

        :stability: experimental
        '''
        return typing.cast("RuntimeNetworkConfiguration", jsii.sinvoke(cls, "usingPublicNetwork", []))

    @jsii.member(jsii_name="usingVpc")
    @builtins.classmethod
    def using_vpc(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "RuntimeNetworkConfiguration":
        '''(experimental) Creates a network configuration from a VPC configuration.

        :param scope: - The construct scope for creating resources.
        :param vpc: (experimental) The VPC to deploy the resource to.
        :param allow_all_outbound: (experimental) Whether to allow the resource to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the resource to connect to network targets. Do not specify this property if the ``securityGroups`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param security_groups: (experimental) The list of security groups to associate with the resource's network interfaces. Only used if 'vpc' is supplied. Default: - If the resource is placed within a VPC and a security group is not specified by this prop, a dedicated security group will be created for this resource.
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Default: - the Vpc default strategy if not specified

        :return: A RuntimeNetworkConfiguration.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b65f23ce4df9170ab1ea5e330f24e42113b36afa69e504b887bda27e2e0919b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        vpc_config = VpcConfigProps(
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("RuntimeNetworkConfiguration", jsii.sinvoke(cls, "usingVpc", [scope, vpc_config]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.RuntimeProps",
    jsii_struct_bases=[],
    name_mapping={
        "agent_runtime_artifact": "agentRuntimeArtifact",
        "runtime_name": "runtimeName",
        "authorizer_configuration": "authorizerConfiguration",
        "description": "description",
        "environment_variables": "environmentVariables",
        "execution_role": "executionRole",
        "network_configuration": "networkConfiguration",
        "protocol_configuration": "protocolConfiguration",
        "tags": "tags",
    },
)
class RuntimeProps:
    def __init__(
        self,
        *,
        agent_runtime_artifact: AgentRuntimeArtifact,
        runtime_name: builtins.str,
        authorizer_configuration: typing.Optional[RuntimeAuthorizerConfiguration] = None,
        description: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_configuration: typing.Optional[RuntimeNetworkConfiguration] = None,
        protocol_configuration: typing.Optional[ProtocolType] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''(experimental) Properties for creating a Bedrock Agent Core Runtime resource.

        :param agent_runtime_artifact: (experimental) The artifact configuration for the agent runtime Contains the container configuration with ECR URI.
        :param runtime_name: (experimental) The name of the agent runtime Valid characters are a-z, A-Z, 0-9, _ (underscore) Must start with a letter and can be up to 48 characters long Pattern: ^[a-zA-Z][a-zA-Z0-9_]{0,47}$.
        :param authorizer_configuration: (experimental) Authorizer configuration for the agent runtime Use RuntimeAuthorizerConfiguration static methods to create the configuration. Default: - RuntimeAuthorizerConfiguration.iam() (IAM authentication)
        :param description: (experimental) Optional description for the agent runtime. Default: - No description Length Minimum: 1 , Maximum: 1200
        :param environment_variables: (experimental) Environment variables for the agent runtime - Maximum 50 environment variables - Key: Must be 1-100 characters, start with letter or underscore, contain only letters, numbers, and underscores - Value: Must be 0-2048 characters (per CloudFormation specification). Default: - No environment variables
        :param execution_role: (experimental) The IAM role that provides permissions for the agent runtime If not provided, a role will be created automatically. Default: - A new role will be created
        :param network_configuration: (experimental) Network configuration for the agent runtime. Default: - RuntimeNetworkConfiguration.usingPublicNetwork()
        :param protocol_configuration: (experimental) Protocol configuration for the agent runtime. Default: - ProtocolType.HTTP
        :param tags: (experimental) Tags for the agent runtime A list of key:value pairs of tags to apply to this Runtime resource. Default: {} - no tags

        :stability: experimental
        :exampleMetadata: infused

        Example::

            repository = ecr.Repository(self, "TestRepository",
                repository_name="test-agent-runtime"
            )
            agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")
            
            runtime = agentcore.Runtime(self, "MyAgentRuntime",
                runtime_name="myAgent",
                agent_runtime_artifact=agent_runtime_artifact,
                authorizer_configuration=agentcore.RuntimeAuthorizerConfiguration.using_oAuth("https://github.com/.well-known/openid-configuration", "oauth_client_123")
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e60d912f60dcec4a97a088e67e9b6da136fd8fbd51038c0380995a1946e1724f)
            check_type(argname="argument agent_runtime_artifact", value=agent_runtime_artifact, expected_type=type_hints["agent_runtime_artifact"])
            check_type(argname="argument runtime_name", value=runtime_name, expected_type=type_hints["runtime_name"])
            check_type(argname="argument authorizer_configuration", value=authorizer_configuration, expected_type=type_hints["authorizer_configuration"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument environment_variables", value=environment_variables, expected_type=type_hints["environment_variables"])
            check_type(argname="argument execution_role", value=execution_role, expected_type=type_hints["execution_role"])
            check_type(argname="argument network_configuration", value=network_configuration, expected_type=type_hints["network_configuration"])
            check_type(argname="argument protocol_configuration", value=protocol_configuration, expected_type=type_hints["protocol_configuration"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "agent_runtime_artifact": agent_runtime_artifact,
            "runtime_name": runtime_name,
        }
        if authorizer_configuration is not None:
            self._values["authorizer_configuration"] = authorizer_configuration
        if description is not None:
            self._values["description"] = description
        if environment_variables is not None:
            self._values["environment_variables"] = environment_variables
        if execution_role is not None:
            self._values["execution_role"] = execution_role
        if network_configuration is not None:
            self._values["network_configuration"] = network_configuration
        if protocol_configuration is not None:
            self._values["protocol_configuration"] = protocol_configuration
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def agent_runtime_artifact(self) -> AgentRuntimeArtifact:
        '''(experimental) The artifact configuration for the agent runtime Contains the container configuration with ECR URI.

        :stability: experimental
        '''
        result = self._values.get("agent_runtime_artifact")
        assert result is not None, "Required property 'agent_runtime_artifact' is missing"
        return typing.cast(AgentRuntimeArtifact, result)

    @builtins.property
    def runtime_name(self) -> builtins.str:
        '''(experimental) The name of the agent runtime Valid characters are a-z, A-Z, 0-9, _ (underscore) Must start with a letter and can be up to 48 characters long Pattern: ^[a-zA-Z][a-zA-Z0-9_]{0,47}$.

        :stability: experimental
        '''
        result = self._values.get("runtime_name")
        assert result is not None, "Required property 'runtime_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorizer_configuration(
        self,
    ) -> typing.Optional[RuntimeAuthorizerConfiguration]:
        '''(experimental) Authorizer configuration for the agent runtime Use RuntimeAuthorizerConfiguration static methods to create the configuration.

        :default: - RuntimeAuthorizerConfiguration.iam() (IAM authentication)

        :stability: experimental
        '''
        result = self._values.get("authorizer_configuration")
        return typing.cast(typing.Optional[RuntimeAuthorizerConfiguration], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional description for the agent runtime.

        :default:

        - No description
        Length Minimum: 1 , Maximum: 1200

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment_variables(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Environment variables for the agent runtime - Maximum 50 environment variables - Key: Must be 1-100 characters, start with letter or underscore, contain only letters, numbers, and underscores - Value: Must be 0-2048 characters (per CloudFormation specification).

        :default: - No environment variables

        :stability: experimental
        '''
        result = self._values.get("environment_variables")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The IAM role that provides permissions for the agent runtime If not provided, a role will be created automatically.

        :default: - A new role will be created

        :stability: experimental
        '''
        result = self._values.get("execution_role")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], result)

    @builtins.property
    def network_configuration(self) -> typing.Optional[RuntimeNetworkConfiguration]:
        '''(experimental) Network configuration for the agent runtime.

        :default: - RuntimeNetworkConfiguration.usingPublicNetwork()

        :stability: experimental
        '''
        result = self._values.get("network_configuration")
        return typing.cast(typing.Optional[RuntimeNetworkConfiguration], result)

    @builtins.property
    def protocol_configuration(self) -> typing.Optional[ProtocolType]:
        '''(experimental) Protocol configuration for the agent runtime.

        :default: - ProtocolType.HTTP

        :stability: experimental
        '''
        result = self._values.get("protocol_configuration")
        return typing.cast(typing.Optional[ProtocolType], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Tags for the agent runtime A list of key:value pairs of tags to apply to this Runtime resource.

        :default: {} - no tags

        :stability: experimental
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuntimeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IMemoryStrategy)
class SelfManagedMemoryStrategy(
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.SelfManagedMemoryStrategy",
):
    '''(experimental) Use AgentCore memory for event storage with custom triggers.

    Define memory processing logic in your own environment.

    :stability: experimental
    :exampleMetadata: fixture=default infused

    Example::

        bucket = s3.Bucket(self, "memoryBucket",
            bucket_name="test-memory",
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        topic = sns.Topic(self, "topic")
        
        # Create a custom semantic memory strategy
        self_managed_strategy = agentcore.MemoryStrategy.using_self_managed(
            name="selfManagedStrategy",
            description="self managed memory strategy",
            historical_context_window_size=5,
            invocation_configuration=agentcore.InvocationConfiguration(
                topic=topic,
                s3_location=s3.Location(
                    bucket_name=bucket.bucket_name,
                    object_key="memory/"
                )
            ),
            trigger_conditions=agentcore.TriggerConditions(
                message_based_trigger=1,
                time_based_trigger=cdk.Duration.seconds(10),
                token_based_trigger=100
            )
        )
        
        # Create memory with custom strategy
        memory = agentcore.Memory(self, "MyMemory",
            memory_name="my-custom-memory",
            description="Memory with custom strategy",
            expiration_duration=cdk.Duration.days(90),
            memory_strategies=[self_managed_strategy]
        )
    '''

    def __init__(
        self,
        strategy_type: MemoryStrategyType,
        *,
        invocation_configuration: typing.Union[InvocationConfiguration, typing.Dict[builtins.str, typing.Any]],
        historical_context_window_size: typing.Optional[jsii.Number] = None,
        trigger_conditions: typing.Optional[typing.Union["TriggerConditions", typing.Dict[builtins.str, typing.Any]]] = None,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param strategy_type: The type of memory strategy.
        :param invocation_configuration: (experimental) Invocation configuration for self managed memory strategy.
        :param historical_context_window_size: (experimental) Define the number of previous events to be included when processing memory. A larger history window provides more context from past conversations. Default: 4
        :param trigger_conditions: (experimental) Trigger conditions for self managed memory strategy. Default: - undefined
        :param name: (experimental) The name for the strategy.
        :param description: (experimental) The description of the strategy. Default: - No description

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__188ac6000401e2d39206f8bbeab856bca92c12af2135f85632e30611238f3ea6)
            check_type(argname="argument strategy_type", value=strategy_type, expected_type=type_hints["strategy_type"])
        props = SelfManagedStrategyProps(
            invocation_configuration=invocation_configuration,
            historical_context_window_size=historical_context_window_size,
            trigger_conditions=trigger_conditions,
            name=name,
            description=description,
        )

        jsii.create(self.__class__, self, [strategy_type, props])

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.Grant]:
        '''(experimental) Grants the necessary permissions to the role.

        :param grantee: - The grantee to grant permissions to.

        :return: The Grant object for chaining

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f97328d30e65eff0ed4b3734cf9226ca12826a94fecee765dbba85c70b4b3635)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.Grant], jsii.invoke(self, "grant", [grantee]))

    @jsii.member(jsii_name="render")
    def render(
        self,
    ) -> _aws_cdk_aws_bedrockagentcore_ceddda9d.CfnMemory.MemoryStrategyProperty:
        '''(experimental) Renders internal attributes to CloudFormation.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_bedrockagentcore_ceddda9d.CfnMemory.MemoryStrategyProperty, jsii.invoke(self, "render", []))

    @builtins.property
    @jsii.member(jsii_name="historicalContextWindowSize")
    def historical_context_window_size(self) -> jsii.Number:
        '''(experimental) Historical context window size for self managed memory strategy.

        :stability: experimental
        '''
        return typing.cast(jsii.Number, jsii.get(self, "historicalContextWindowSize"))

    @builtins.property
    @jsii.member(jsii_name="invocationConfiguration")
    def invocation_configuration(self) -> InvocationConfiguration:
        '''(experimental) Invocation configuration for self managed memory strategy.

        :stability: experimental
        '''
        return typing.cast(InvocationConfiguration, jsii.get(self, "invocationConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the memory strategy.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="strategyType")
    def strategy_type(self) -> MemoryStrategyType:
        '''(experimental) The type of memory strategy.

        :stability: experimental
        '''
        return typing.cast(MemoryStrategyType, jsii.get(self, "strategyType"))

    @builtins.property
    @jsii.member(jsii_name="triggerConditions")
    def trigger_conditions(self) -> "TriggerConditions":
        '''(experimental) Trigger conditions for self managed memory strategy.

        :stability: experimental
        '''
        return typing.cast("TriggerConditions", jsii.get(self, "triggerConditions"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the memory strategy.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.SelfManagedStrategyProps",
    jsii_struct_bases=[MemoryStrategyCommonProps],
    name_mapping={
        "name": "name",
        "description": "description",
        "invocation_configuration": "invocationConfiguration",
        "historical_context_window_size": "historicalContextWindowSize",
        "trigger_conditions": "triggerConditions",
    },
)
class SelfManagedStrategyProps(MemoryStrategyCommonProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        invocation_configuration: typing.Union[InvocationConfiguration, typing.Dict[builtins.str, typing.Any]],
        historical_context_window_size: typing.Optional[jsii.Number] = None,
        trigger_conditions: typing.Optional[typing.Union["TriggerConditions", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Configuration parameters for a self managed memory strategy existing built-in default prompts/models.

        :param name: (experimental) The name for the strategy.
        :param description: (experimental) The description of the strategy. Default: - No description
        :param invocation_configuration: (experimental) Invocation configuration for self managed memory strategy.
        :param historical_context_window_size: (experimental) Define the number of previous events to be included when processing memory. A larger history window provides more context from past conversations. Default: 4
        :param trigger_conditions: (experimental) Trigger conditions for self managed memory strategy. Default: - undefined

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            bucket = s3.Bucket(self, "memoryBucket",
                bucket_name="test-memory",
                removal_policy=cdk.RemovalPolicy.DESTROY,
                auto_delete_objects=True
            )
            
            topic = sns.Topic(self, "topic")
            
            # Create a custom semantic memory strategy
            self_managed_strategy = agentcore.MemoryStrategy.using_self_managed(
                name="selfManagedStrategy",
                description="self managed memory strategy",
                historical_context_window_size=5,
                invocation_configuration=agentcore.InvocationConfiguration(
                    topic=topic,
                    s3_location=s3.Location(
                        bucket_name=bucket.bucket_name,
                        object_key="memory/"
                    )
                ),
                trigger_conditions=agentcore.TriggerConditions(
                    message_based_trigger=1,
                    time_based_trigger=cdk.Duration.seconds(10),
                    token_based_trigger=100
                )
            )
            
            # Create memory with custom strategy
            memory = agentcore.Memory(self, "MyMemory",
                memory_name="my-custom-memory",
                description="Memory with custom strategy",
                expiration_duration=cdk.Duration.days(90),
                memory_strategies=[self_managed_strategy]
            )
        '''
        if isinstance(invocation_configuration, dict):
            invocation_configuration = InvocationConfiguration(**invocation_configuration)
        if isinstance(trigger_conditions, dict):
            trigger_conditions = TriggerConditions(**trigger_conditions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbcf3bdd0c9f8eaadddbc029d9f0a9dece8550883bffe0164f389e25d3629630)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument invocation_configuration", value=invocation_configuration, expected_type=type_hints["invocation_configuration"])
            check_type(argname="argument historical_context_window_size", value=historical_context_window_size, expected_type=type_hints["historical_context_window_size"])
            check_type(argname="argument trigger_conditions", value=trigger_conditions, expected_type=type_hints["trigger_conditions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "invocation_configuration": invocation_configuration,
        }
        if description is not None:
            self._values["description"] = description
        if historical_context_window_size is not None:
            self._values["historical_context_window_size"] = historical_context_window_size
        if trigger_conditions is not None:
            self._values["trigger_conditions"] = trigger_conditions

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name for the strategy.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the strategy.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def invocation_configuration(self) -> InvocationConfiguration:
        '''(experimental) Invocation configuration for self managed memory strategy.

        :stability: experimental
        '''
        result = self._values.get("invocation_configuration")
        assert result is not None, "Required property 'invocation_configuration' is missing"
        return typing.cast(InvocationConfiguration, result)

    @builtins.property
    def historical_context_window_size(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Define the number of previous events to be included when processing memory.

        A larger history window provides more context from past conversations.

        :default: 4

        :stability: experimental
        '''
        result = self._values.get("historical_context_window_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def trigger_conditions(self) -> typing.Optional["TriggerConditions"]:
        '''(experimental) Trigger conditions for self managed memory strategy.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("trigger_conditions")
        return typing.cast(typing.Optional["TriggerConditions"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SelfManagedStrategyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.TriggerConditions",
    jsii_struct_bases=[],
    name_mapping={
        "message_based_trigger": "messageBasedTrigger",
        "time_based_trigger": "timeBasedTrigger",
        "token_based_trigger": "tokenBasedTrigger",
    },
)
class TriggerConditions:
    def __init__(
        self,
        *,
        message_based_trigger: typing.Optional[jsii.Number] = None,
        time_based_trigger: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        token_based_trigger: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Trigger conditions for self managed memory strategy When first condition is met, batched payloads are sent to specified S3 bucket.

        :param message_based_trigger: (experimental) Triggers memory processing when specified number of new messages is reached. Default: 1
        :param time_based_trigger: (experimental) Triggers memory processing when the session has been idle for the specified duration. Value in seconds. Default: - 10 seconds
        :param token_based_trigger: (experimental) Triggers memory processing when the token size reaches the specified threshold. Default: 100

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            bucket = s3.Bucket(self, "memoryBucket",
                bucket_name="test-memory",
                removal_policy=cdk.RemovalPolicy.DESTROY,
                auto_delete_objects=True
            )
            
            topic = sns.Topic(self, "topic")
            
            # Create a custom semantic memory strategy
            self_managed_strategy = agentcore.MemoryStrategy.using_self_managed(
                name="selfManagedStrategy",
                description="self managed memory strategy",
                historical_context_window_size=5,
                invocation_configuration=agentcore.InvocationConfiguration(
                    topic=topic,
                    s3_location=s3.Location(
                        bucket_name=bucket.bucket_name,
                        object_key="memory/"
                    )
                ),
                trigger_conditions=agentcore.TriggerConditions(
                    message_based_trigger=1,
                    time_based_trigger=cdk.Duration.seconds(10),
                    token_based_trigger=100
                )
            )
            
            # Create memory with custom strategy
            memory = agentcore.Memory(self, "MyMemory",
                memory_name="my-custom-memory",
                description="Memory with custom strategy",
                expiration_duration=cdk.Duration.days(90),
                memory_strategies=[self_managed_strategy]
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__effa7c1822f5dd9bca17e2aca728718fe021317ef7ef3e7d41d4ea4fa5f2112a)
            check_type(argname="argument message_based_trigger", value=message_based_trigger, expected_type=type_hints["message_based_trigger"])
            check_type(argname="argument time_based_trigger", value=time_based_trigger, expected_type=type_hints["time_based_trigger"])
            check_type(argname="argument token_based_trigger", value=token_based_trigger, expected_type=type_hints["token_based_trigger"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if message_based_trigger is not None:
            self._values["message_based_trigger"] = message_based_trigger
        if time_based_trigger is not None:
            self._values["time_based_trigger"] = time_based_trigger
        if token_based_trigger is not None:
            self._values["token_based_trigger"] = token_based_trigger

    @builtins.property
    def message_based_trigger(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Triggers memory processing when specified number of new messages is reached.

        :default: 1

        :stability: experimental
        '''
        result = self._values.get("message_based_trigger")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def time_based_trigger(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) Triggers memory processing when the session has been idle for the specified duration.

        Value in seconds.

        :default: - 10 seconds

        :stability: experimental
        '''
        result = self._values.get("time_based_trigger")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], result)

    @builtins.property
    def token_based_trigger(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Triggers memory processing when the token size reaches the specified threshold.

        :default: 100

        :stability: experimental
        '''
        result = self._values.get("token_based_trigger")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TriggerConditions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.VpcConfigProps",
    jsii_struct_bases=[],
    name_mapping={
        "vpc": "vpc",
        "allow_all_outbound": "allowAllOutbound",
        "security_groups": "securityGroups",
        "vpc_subnets": "vpcSubnets",
    },
)
class VpcConfigProps:
    def __init__(
        self,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) VPC configuration properties.

        Only used when network mode is VPC.

        :param vpc: (experimental) The VPC to deploy the resource to.
        :param allow_all_outbound: (experimental) Whether to allow the resource to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the resource to connect to network targets. Do not specify this property if the ``securityGroups`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param security_groups: (experimental) The list of security groups to associate with the resource's network interfaces. Only used if 'vpc' is supplied. Default: - If the resource is placed within a VPC and a security group is not specified by this prop, a dedicated security group will be created for this resource.
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Default: - the Vpc default strategy if not specified

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            vpc = ec2.Vpc(self, "testVPC")
            
            code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
                code_interpreter_custom_name="my_sandbox_interpreter",
                description="Code interpreter with isolated network access",
                network_configuration=agentcore.BrowserNetworkConfiguration.using_vpc(self,
                    vpc=vpc
                )
            )
            
            code_interpreter.connections.add_security_group(ec2.SecurityGroup(self, "AdditionalGroup", vpc=vpc))
        '''
        if isinstance(vpc_subnets, dict):
            vpc_subnets = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**vpc_subnets)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2116ad0a264d69770800f27d273a661a955fcb5c6c066f36456e9178f63d742d)
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument allow_all_outbound", value=allow_all_outbound, expected_type=type_hints["allow_all_outbound"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "vpc": vpc,
        }
        if allow_all_outbound is not None:
            self._values["allow_all_outbound"] = allow_all_outbound
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets

    @builtins.property
    def vpc(self) -> _aws_cdk_aws_ec2_ceddda9d.IVpc:
        '''(experimental) The VPC to deploy the resource to.

        :stability: experimental
        '''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.IVpc, result)

    @builtins.property
    def allow_all_outbound(self) -> typing.Optional[builtins.bool]:
        '''(experimental) Whether to allow the resource to send all network traffic (except ipv6).

        If set to false, you must individually add traffic rules to allow the
        resource to connect to network targets.

        Do not specify this property if the ``securityGroups`` property is set.
        Instead, configure ``allowAllOutbound`` directly on the security group.

        :default: true

        :stability: experimental
        '''
        result = self._values.get("allow_all_outbound")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''(experimental) The list of security groups to associate with the resource's network interfaces.

        Only used if 'vpc' is supplied.

        :default:

        - If the resource is placed within a VPC and a security group is
        not specified by this prop, a dedicated security
        group will be created for this resource.

        :stability: experimental
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def vpc_subnets(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]:
        '''(experimental) Where to place the network interfaces within the VPC.

        This requires ``vpc`` to be specified in order for interfaces to actually be
        placed in the subnets. If ``vpc`` is not specify, this will raise an error.

        :default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VpcConfigProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IBrowserCustom)
class BrowserCustomBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.BrowserCustomBase",
):
    '''(experimental) Abstract base class for a Browser.

    Contains methods and attributes valid for Browsers either created with CDK or imported.

    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c77d9cceeabf2dd05d534145778ab3e1e597cf25fdabc7bdbdbc642c412f2435)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants IAM actions to the IAM Principal.

        :param grantee: - The IAM principal to grant permissions to.
        :param actions: - The actions to grant.

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6facf14dce62b7f6f12e4abaf4eb022dff3a45f4068e5f45350aab6e10355a0)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read permissions on this browser to an IAM principal.

        This includes both read permissions on the specific browser and list permissions on all browsers.

        :param grantee: - The IAM principal to grant read permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:GetBrowser', 'bedrock-agentcore:GetBrowserSession'] on this.browserArn
        - actions: ['bedrock-agentcore:ListBrowsers', 'bedrock-agentcore:ListBrowserSessions'] on all resources (*)

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d32eecca999e221fe7baaea3ba395ddee5578ec83675efa9efdbea664213da2)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantUse")
    def grant_use(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant invoke permissions on this browser to an IAM principal.

        :param grantee: - The IAM principal to grant invoke permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:StartBrowserSession', 'bedrock-agentcore:UpdateBrowserStream', 'bedrock-agentcore:StopBrowserSession']
        - resourceArns: [this.browserArn]

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9186b5df0e333eb3469e897ab73dc50dee27c22f707afd8f3645295ca9d00d55)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantUse", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this browser.

        By default, the metric will be calculated as a sum over a period of 5 minutes.
        You can customize this by using the ``statistic`` and ``period`` properties.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8d3ed248b0e1fbb8321d56521a7d7da90f0d2609d7149da6e1d786cbb7e8af8)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, dimensions, props]))

    @jsii.member(jsii_name="metricErrorsForApiOperation")
    def metric_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser errors.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Errors

        :return: A CloudWatch Metric configured for browser errors

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78f3dfb28f4dc0851b8a333b577550c3ed04b83619039f5923124cdcbed267cd)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricForApiOperation")
    def metric_for_api_operation(
        self,
        metric_name: builtins.str,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser api operations..

        :param metric_name: -
        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: metricName
        - dimensionsMap: { BrowserId: this.browserId }

        :return: A CloudWatch Metric configured for browser api operations

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44ddd5de65d8344be82e751ad250cc43e9faa11ea964e6b229c0a4d1ec72d5f7)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricForApiOperation", [metric_name, operation, props]))

    @jsii.member(jsii_name="metricInvocationsForApiOperation")
    def metric_invocations_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser invocations.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Invocations

        :return: A CloudWatch Metric configured for browser latencies

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad4dce28a348ae0a4ea1f8be12576c56d15cb4cfabe63fa3ad38edc91bd2674d)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocationsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricLatencyForApiOperation")
    def metric_latency_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser latencies.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Latency

        :return: A CloudWatch Metric configured for browser latencies

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__def70821036fc28a14280760ae0b74a0fece9251b8de279a7787b620952b96f2)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatencyForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricSessionDuration")
    def metric_session_duration(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser session duration.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Duration

        :return: A CloudWatch Metric configured for browser session duration

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSessionDuration", [props]))

    @jsii.member(jsii_name="metricSystemErrorsForApiOperation")
    def metric_system_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser system errors.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: SystemErrors

        :return: A CloudWatch Metric configured for browser system errors

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35a69ebb2bb4842640813061b2ac17af0959c464410a959b014b4c88834032a5)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSystemErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricTakeOverCount")
    def metric_take_over_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser user takeovers.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: TakeOverCount

        :return: A CloudWatch Metric configured for browser user takeovers

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTakeOverCount", [props]))

    @jsii.member(jsii_name="metricTakeOverDuration")
    def metric_take_over_duration(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser user takeovers duration.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: TakeOverDuration

        :return: A CloudWatch Metric configured for browser user takeovers duration

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTakeOverDuration", [props]))

    @jsii.member(jsii_name="metricTakeOverReleaseCount")
    def metric_take_over_release_count(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser user takeovers released.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: TakeOverReleaseCount

        :return: A CloudWatch Metric configured for browser user takeovers released

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricTakeOverReleaseCount", [props]))

    @jsii.member(jsii_name="metricThrottlesForApiOperation")
    def metric_throttles_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser throttles.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Throttles

        :return: A CloudWatch Metric configured for browser throttles

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__945c10dd6a920f679edb8ab070a635638c847e8d49d196a218ff5b77cdf8d742)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricThrottlesForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricUserErrorsForApiOperation")
    def metric_user_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking browser user errors.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: UserErrors

        :return: A CloudWatch Metric configured for browser user errors

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a2ee85b94b08620ec9b5951320326c2a5e06e58d8c74143b59faaa569c5db5a)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricUserErrorsForApiOperation", [operation, props]))

    @builtins.property
    @jsii.member(jsii_name="browserArn")
    @abc.abstractmethod
    def browser_arn(self) -> builtins.str:
        '''(experimental) The ARN of the browser resource.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="browserId")
    @abc.abstractmethod
    def browser_id(self) -> builtins.str:
        '''(experimental) The id of the browser.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) An accessor for the Connections object that will fail if this Browser does not have a VPC configured.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    @abc.abstractmethod
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the browser to access AWS services.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    @abc.abstractmethod
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    @abc.abstractmethod
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the browser was created.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    @abc.abstractmethod
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the browser was last updated.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="status")
    @abc.abstractmethod
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the browser.

        :stability: experimental
        '''
        ...


class _BrowserCustomBaseProxy(
    BrowserCustomBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="browserArn")
    def browser_arn(self) -> builtins.str:
        '''(experimental) The ARN of the browser resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "browserArn"))

    @builtins.property
    @jsii.member(jsii_name="browserId")
    def browser_id(self) -> builtins.str:
        '''(experimental) The id of the browser.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "browserId"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the browser to access AWS services.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the browser was created.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the browser was last updated.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the browser.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BrowserCustomBase).__jsii_proxy_class__ = lambda : _BrowserCustomBaseProxy


class BrowserNetworkConfiguration(
    NetworkConfiguration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.BrowserNetworkConfiguration",
):
    '''(experimental) Network configuration for the Browser tool.

    :stability: experimental
    :exampleMetadata: fixture=default infused

    Example::

        vpc = ec2.Vpc(self, "testVPC")
        
        code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
            code_interpreter_custom_name="my_sandbox_interpreter",
            description="Code interpreter with isolated network access",
            network_configuration=agentcore.BrowserNetworkConfiguration.using_vpc(self,
                vpc=vpc
            )
        )
        
        code_interpreter.connections.add_security_group(ec2.SecurityGroup(self, "AdditionalGroup", vpc=vpc))
    '''

    def __init__(
        self,
        mode: builtins.str,
        scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Creates a new network configuration.

        :param mode: - the network mode to use for the tool.
        :param scope: -
        :param vpc: (experimental) The VPC to deploy the resource to.
        :param allow_all_outbound: (experimental) Whether to allow the resource to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the resource to connect to network targets. Do not specify this property if the ``securityGroups`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param security_groups: (experimental) The list of security groups to associate with the resource's network interfaces. Only used if 'vpc' is supplied. Default: - If the resource is placed within a VPC and a security group is not specified by this prop, a dedicated security group will be created for this resource.
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a61932e41a10c1b55eb12421708f57f6f8fa7f51c4a52602ae921332f603e4bc)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        vpc_config = VpcConfigProps(
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [mode, scope, vpc_config])

    @jsii.member(jsii_name="usingPublicNetwork")
    @builtins.classmethod
    def using_public_network(cls) -> "BrowserNetworkConfiguration":
        '''(experimental) Creates a public network configuration.

        PUBLIC is the default network mode.

        :return:

        A BrowserNetworkConfiguration.
        Run this tool to operate in a public environment with internet access, suitable for less sensitive or open-use scenarios.

        :stability: experimental
        '''
        return typing.cast("BrowserNetworkConfiguration", jsii.sinvoke(cls, "usingPublicNetwork", []))

    @jsii.member(jsii_name="usingVpc")
    @builtins.classmethod
    def using_vpc(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "BrowserNetworkConfiguration":
        '''(experimental) Creates a network configuration from a VPC configuration.

        :param scope: -
        :param vpc: (experimental) The VPC to deploy the resource to.
        :param allow_all_outbound: (experimental) Whether to allow the resource to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the resource to connect to network targets. Do not specify this property if the ``securityGroups`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param security_groups: (experimental) The list of security groups to associate with the resource's network interfaces. Only used if 'vpc' is supplied. Default: - If the resource is placed within a VPC and a security group is not specified by this prop, a dedicated security group will be created for this resource.
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Default: - the Vpc default strategy if not specified

        :return: A BrowserNetworkConfiguration.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffadf1618c1ccf9e7f800598ace60f876ef2c866dfa2193de733904aef830531)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        vpc_config = VpcConfigProps(
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("BrowserNetworkConfiguration", jsii.sinvoke(cls, "usingVpc", [scope, vpc_config]))


@jsii.implements(ICodeInterpreterCustom)
class CodeInterpreterCustomBase(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.CodeInterpreterCustomBase",
):
    '''(experimental) Abstract base class for a Code Interpreter.

    Contains methods and attributes valid for Code Interpreters either created with CDK or imported.

    :stability: experimental
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3ba04960e2402fcf93e24376e08d3027678d856540da250157c6e19f1dc1862)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="grant")
    def grant(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        *actions: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grants IAM actions to the IAM Principal.

        :param grantee: - The IAM principal to grant permissions to.
        :param actions: - The actions to grant.

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1788c6502070824895d3503d450005bb1c205c4d74bb8738add0bf26f3de4904)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
            check_type(argname="argument actions", value=actions, expected_type=typing.Tuple[type_hints["actions"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grant", [grantee, *actions]))

    @jsii.member(jsii_name="grantInvoke")
    def grant_invoke(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant invoke permissions on this code interpreter to an IAM principal.

        :param grantee: - The IAM principal to grant invoke permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:InvokeCodeInterpreter']
        - resourceArns: [this.codeInterpreterArn]

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2db493ce830ccc0f4897a55b53f8cb527c29ca1faf55e5ef17c8df1975c84db)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantInvoke", [grantee]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read permissions on this code interpreter to an IAM principal.

        This includes both read permissions on the specific code interpreter and list permissions on all code interpreters.

        :param grantee: - The IAM principal to grant read permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:GetCodeInterpreter', 'bedrock-agentcore:GetCodeInterpreterSession'] on this.codeInterpreterArn
        - actions: ['bedrock-agentcore:ListCodeInterpreters', 'bedrock-agentcore:ListCodeInterpreterSessions'] on all resources (*)

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49cb39b73910ca0e9b10fd69d88ba3c962540e3ffe52e4af83aa081763523e1e)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [grantee]))

    @jsii.member(jsii_name="grantUse")
    def grant_use(
        self,
        grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant invoke permissions on this code interpreter to an IAM principal.

        :param grantee: - The IAM principal to grant invoke permissions to.

        :default:

        - Default grant configuration:
        - actions: ['bedrock-agentcore:StartCodeInterpreterSession', 'bedrock-agentcore:InvokeCodeInterpreter', 'bedrock-agentcore:StopCodeInterpreterSession']
        - resourceArns: [this.codeInterpreterArn]

        :return: An IAM Grant object representing the granted permissions

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4d919318556058b051ce30963bb88b3ea857942f805b6da65b497596bc8e39b)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantUse", [grantee]))

    @jsii.member(jsii_name="metric")
    def metric(
        self,
        metric_name: builtins.str,
        dimensions: typing.Mapping[builtins.str, builtins.str],
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Return the given named metric for this code interpreter.

        By default, the metric will be calculated as a sum over a period of 5 minutes.
        You can customize this by using the ``statistic`` and ``period`` properties.

        :param metric_name: -
        :param dimensions: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e89914064bfd399d5233c80170ff40fe971de7b840aeca4ac822fd1fcaf4c53)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument dimensions", value=dimensions, expected_type=type_hints["dimensions"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metric", [metric_name, dimensions, props]))

    @jsii.member(jsii_name="metricErrorsForApiOperation")
    def metric_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking code interpreter errors.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Errors

        :return: A CloudWatch Metric configured for code interpreter errors

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a96b5df243162f6e4ccc604d71ceff9d4907e1fb21c4bdc077b17e437bad6d1e)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricForApiOperation")
    def metric_for_api_operation(
        self,
        metric_name: builtins.str,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking code interpreter api operations..

        :param metric_name: -
        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: metricName
        - dimensionsMap: { CodeInterpreterId: this.codeInterpreterId }

        :return: A CloudWatch Metric configured for code interpreter api operations

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__601c512b2394720d7f44430e54e52ac9b991b7aa673c58633b67406ae999ec8a)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricForApiOperation", [metric_name, operation, props]))

    @jsii.member(jsii_name="metricInvocationsForApiOperation")
    def metric_invocations_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking code interpreter invocations.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Invocations

        :return: A CloudWatch Metric configured for code interpreter invocations

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da0ad6292c612c8f34d7b641b68c10de89777fe2d41763b66d9ea6f7c878c4a6)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricInvocationsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricLatencyForApiOperation")
    def metric_latency_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking code interpreter latencies.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Latency

        :return: A CloudWatch Metric configured for code interpreter latencies

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72deaefdc0ab67927aa48a7e5dbfb70a9004b85dab32f68b95be249b26066bd0)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricLatencyForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricSessionDuration")
    def metric_session_duration(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking code interpreter session duration.

        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Duration

        :return: A CloudWatch Metric configured for code interpreter session duration

        :stability: experimental
        '''
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSessionDuration", [props]))

    @jsii.member(jsii_name="metricSystemErrorsForApiOperation")
    def metric_system_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking code interpreter system errors.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: SystemErrors

        :return: A CloudWatch Metric configured for code interpreter system errors

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65d0b839015fe6a1c368d562bdee51b93c69cb5b759c1f1173dc2758a1413968)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricSystemErrorsForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricThrottlesForApiOperation")
    def metric_throttles_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking code interpreter throttles.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: Throttles

        :return: A CloudWatch Metric configured for code interpreter throttles

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a56c641c8e2af33eb396292b7658955fbae3d77a1c0a87985f4020dfe2e45f2)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricThrottlesForApiOperation", [operation, props]))

    @jsii.member(jsii_name="metricUserErrorsForApiOperation")
    def metric_user_errors_for_api_operation(
        self,
        operation: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        color: typing.Optional[builtins.str] = None,
        dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        label: typing.Optional[builtins.str] = None,
        period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        region: typing.Optional[builtins.str] = None,
        stack_account: typing.Optional[builtins.str] = None,
        stack_region: typing.Optional[builtins.str] = None,
        statistic: typing.Optional[builtins.str] = None,
        unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
        visible: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_cloudwatch_ceddda9d.Metric:
        '''(experimental) Creates a CloudWatch metric for tracking code interpreter user errors.

        :param operation: -
        :param account: Account which this metric comes from. Default: - Deployment account.
        :param color: The hex color code, prefixed with '#' (e.g. '#00ff00'), to use when this metric is rendered on a graph. The ``Color`` class has a set of standard colors that can be used here. Default: - Automatic color
        :param dimensions_map: Dimensions of the metric. Default: - No dimensions.
        :param id: Unique identifier for this metric when used in dashboard widgets. The id can be used as a variable to represent this metric in math expressions. Valid characters are letters, numbers, and underscore. The first character must be a lowercase letter. Default: - No ID
        :param label: Label for this metric when added to a Graph in a Dashboard. You can use `dynamic labels <https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/graph-dynamic-labels.html>`_ to show summary information about the entire displayed time series in the legend. For example, if you use:: [max: ${MAX}] MyMetric As the metric label, the maximum value in the visible range will be shown next to the time series name in the graph's legend. Default: - No label
        :param period: The period over which the specified statistic is applied. Default: Duration.minutes(5)
        :param region: Region which this metric comes from. Default: - Deployment region.
        :param stack_account: Account of the stack this metric is attached to. Default: - Deployment account.
        :param stack_region: Region of the stack this metric is attached to. Default: - Deployment region.
        :param statistic: What function to use for aggregating. Use the ``aws_cloudwatch.Stats`` helper class to construct valid input strings. Can be one of the following: - "Minimum" | "min" - "Maximum" | "max" - "Average" | "avg" - "Sum" | "sum" - "SampleCount | "n" - "pNN.NN" - "tmNN.NN" | "tm(NN.NN%:NN.NN%)" - "iqm" - "wmNN.NN" | "wm(NN.NN%:NN.NN%)" - "tcNN.NN" | "tc(NN.NN%:NN.NN%)" - "tsNN.NN" | "ts(NN.NN%:NN.NN%)" Default: Average
        :param unit: Unit used to filter the metric stream. Only refer to datums emitted to the metric stream with the given unit and ignore all others. Only useful when datums are being emitted to the same metric stream under different units. The default is to use all matric datums in the stream, regardless of unit, which is recommended in nearly all cases. CloudWatch does not honor this property for graphs. Default: - All metric datums in the given metric stream
        :param visible: Whether this metric should be visible in dashboard graphs. Setting this to false is useful when you want to hide raw metrics that are used in math expressions, and show only the expression results. Default: true

        :default:

        - Default metric configuration:
        - namespace: 'AWS/Bedrock-AgentCore'
        - metricName: UserErrors

        :return: A CloudWatch Metric configured for code interpreter user errors

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9be097202746caca62d9d0d7831461e673cceaf8e528a88286bd03a9c0c5b694)
            check_type(argname="argument operation", value=operation, expected_type=type_hints["operation"])
        props = _aws_cdk_aws_cloudwatch_ceddda9d.MetricOptions(
            account=account,
            color=color,
            dimensions_map=dimensions_map,
            id=id,
            label=label,
            period=period,
            region=region,
            stack_account=stack_account,
            stack_region=stack_region,
            statistic=statistic,
            unit=unit,
            visible=visible,
        )

        return typing.cast(_aws_cdk_aws_cloudwatch_ceddda9d.Metric, jsii.invoke(self, "metricUserErrorsForApiOperation", [operation, props]))

    @builtins.property
    @jsii.member(jsii_name="codeInterpreterArn")
    @abc.abstractmethod
    def code_interpreter_arn(self) -> builtins.str:
        '''(experimental) The ARN of the code interpreter resource.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="codeInterpreterId")
    @abc.abstractmethod
    def code_interpreter_id(self) -> builtins.str:
        '''(experimental) The id of the code interpreter.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="connections")
    def connections(self) -> _aws_cdk_aws_ec2_ceddda9d.Connections:
        '''(experimental) An accessor for the Connections object that will fail if this Browser does not have a VPC configured.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_ec2_ceddda9d.Connections, jsii.get(self, "connections"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    @abc.abstractmethod
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the code interpreter to access AWS services.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    @abc.abstractmethod
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    @abc.abstractmethod
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the code interpreter was created.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    @abc.abstractmethod
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the code interpreter was last updated.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="status")
    @abc.abstractmethod
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the code interpreter.

        :stability: experimental
        '''
        ...


class _CodeInterpreterCustomBaseProxy(
    CodeInterpreterCustomBase,
    jsii.proxy_for(_aws_cdk_ceddda9d.Resource), # type: ignore[misc]
):
    @builtins.property
    @jsii.member(jsii_name="codeInterpreterArn")
    def code_interpreter_arn(self) -> builtins.str:
        '''(experimental) The ARN of the code interpreter resource.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "codeInterpreterArn"))

    @builtins.property
    @jsii.member(jsii_name="codeInterpreterId")
    def code_interpreter_id(self) -> builtins.str:
        '''(experimental) The id of the code interpreter.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "codeInterpreterId"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the code interpreter to access AWS services.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the code interpreter was created.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) Timestamp when the code interpreter was last updated.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the code interpreter.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, CodeInterpreterCustomBase).__jsii_proxy_class__ = lambda : _CodeInterpreterCustomBaseProxy


class CodeInterpreterNetworkConfiguration(
    NetworkConfiguration,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.CodeInterpreterNetworkConfiguration",
):
    '''(experimental) Network configuration for the Code Interpreter tool.

    :stability: experimental
    :exampleMetadata: fixture=default infused

    Example::

        # Create a custom execution role
        execution_role = iam.Role(self, "CodeInterpreterExecutionRole",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com")
        )
        
        # Create code interpreter with custom execution role
        code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
            code_interpreter_custom_name="my_code_interpreter",
            description="Code interpreter with custom execution role",
            network_configuration=agentcore.CodeInterpreterNetworkConfiguration.using_public_network(),
            execution_role=execution_role
        )
    '''

    def __init__(
        self,
        mode: builtins.str,
        scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Creates a new network configuration.

        :param mode: - the network mode to use for the tool.
        :param scope: -
        :param vpc: (experimental) The VPC to deploy the resource to.
        :param allow_all_outbound: (experimental) Whether to allow the resource to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the resource to connect to network targets. Do not specify this property if the ``securityGroups`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param security_groups: (experimental) The list of security groups to associate with the resource's network interfaces. Only used if 'vpc' is supplied. Default: - If the resource is placed within a VPC and a security group is not specified by this prop, a dedicated security group will be created for this resource.
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Default: - the Vpc default strategy if not specified

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5abf274e5386aff6188eb410a31a1f9a74e1ef0c691c2c7886dd26347a9bbcc6)
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        vpc_config = VpcConfigProps(
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
        )

        jsii.create(self.__class__, self, [mode, scope, vpc_config])

    @jsii.member(jsii_name="usingPublicNetwork")
    @builtins.classmethod
    def using_public_network(cls) -> "CodeInterpreterNetworkConfiguration":
        '''(experimental) Creates a public network configuration.

        :return:

        A CodeInterpreterNetworkConfiguration.
        Run this tool to operate in a public environment with internet access, suitable for less sensitive or open-use scenarios.

        :stability: experimental
        '''
        return typing.cast("CodeInterpreterNetworkConfiguration", jsii.sinvoke(cls, "usingPublicNetwork", []))

    @jsii.member(jsii_name="usingSandboxNetwork")
    @builtins.classmethod
    def using_sandbox_network(cls) -> "CodeInterpreterNetworkConfiguration":
        '''(experimental) Creates a sandbox network configuration.

        :return:

        A CodeInterpreterNetworkConfiguration.
        Run this tool in a restricted environment with limited Permissions and Encryption to enhance safety and reduce potential risks.

        :stability: experimental
        '''
        return typing.cast("CodeInterpreterNetworkConfiguration", jsii.sinvoke(cls, "usingSandboxNetwork", []))

    @jsii.member(jsii_name="usingVpc")
    @builtins.classmethod
    def using_vpc(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        *,
        vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> "CodeInterpreterNetworkConfiguration":
        '''(experimental) Creates a network configuration from a VPC configuration.

        :param scope: -
        :param vpc: (experimental) The VPC to deploy the resource to.
        :param allow_all_outbound: (experimental) Whether to allow the resource to send all network traffic (except ipv6). If set to false, you must individually add traffic rules to allow the resource to connect to network targets. Do not specify this property if the ``securityGroups`` property is set. Instead, configure ``allowAllOutbound`` directly on the security group. Default: true
        :param security_groups: (experimental) The list of security groups to associate with the resource's network interfaces. Only used if 'vpc' is supplied. Default: - If the resource is placed within a VPC and a security group is not specified by this prop, a dedicated security group will be created for this resource.
        :param vpc_subnets: (experimental) Where to place the network interfaces within the VPC. This requires ``vpc`` to be specified in order for interfaces to actually be placed in the subnets. If ``vpc`` is not specify, this will raise an error. Default: - the Vpc default strategy if not specified

        :return: A CodeInterpreterNetworkConfiguration.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38e59bc603de9e405a37067fca444858724ba4a5692828408586100c7172d14d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
        vpc_config = VpcConfigProps(
            vpc=vpc,
            allow_all_outbound=allow_all_outbound,
            security_groups=security_groups,
            vpc_subnets=vpc_subnets,
        )

        return typing.cast("CodeInterpreterNetworkConfiguration", jsii.sinvoke(cls, "usingVpc", [scope, vpc_config]))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.ManagedStrategyProps",
    jsii_struct_bases=[MemoryStrategyCommonProps],
    name_mapping={
        "name": "name",
        "description": "description",
        "namespaces": "namespaces",
        "custom_consolidation": "customConsolidation",
        "custom_extraction": "customExtraction",
    },
)
class ManagedStrategyProps(MemoryStrategyCommonProps):
    def __init__(
        self,
        *,
        name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        namespaces: typing.Sequence[builtins.str],
        custom_consolidation: typing.Optional[typing.Union[OverrideConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        custom_extraction: typing.Optional[typing.Union[OverrideConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Configuration parameters for a memory strategy that can override existing built-in default prompts/models.

        :param name: (experimental) The name for the strategy.
        :param description: (experimental) The description of the strategy. Default: - No description
        :param namespaces: (experimental) The namespaces for the strategy Represents a namespace for organizing memory data Use a hierarchical format separated by forward slashes (/). Use a hierarchical format separated by forward slashes (/) to organize namespaces logically. You can include these defined variables: - {sessionId} - the user identifier to be created in the CreateEvent API - {memoryStrategyId} - an identifier for an extraction strategy - {sessionId} - an identifier for each session Example namespace path: /strategies/{memoryStrategyId}/actions/{actionId}/sessions/{sessionId} After memory creation, this namespace might look like: /actor/actor-3afc5aa8fef9/strategy/summarization-fy5c5fwc7/session/session-qj7tpd1kvr8
        :param custom_consolidation: (experimental) The configuration for the custom consolidation. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction
        :param custom_extraction: (experimental) The configuration for the custom extraction. This configuration provides customization to how the model identifies and extracts relevant information for memory storage. Default: - No custom extraction

        :stability: experimental
        :exampleMetadata: fixture=default infused

        Example::

            # Create memory with built-in strategies
            memory = agentcore.Memory(self, "MyMemory",
                memory_name="my_memory",
                description="Memory with built-in strategies",
                expiration_duration=cdk.Duration.days(90),
                memory_strategies=[
                    agentcore.MemoryStrategy.using_user_preference(
                        name="CustomerPreferences",
                        namespaces=["support/customer/{actorId}/preferences"]
                    ),
                    agentcore.MemoryStrategy.using_semantic(
                        name="CustomerSupportSemantic",
                        namespaces=["support/customer/{actorId}/semantic"]
                    )
                ]
            )
        '''
        if isinstance(custom_consolidation, dict):
            custom_consolidation = OverrideConfig(**custom_consolidation)
        if isinstance(custom_extraction, dict):
            custom_extraction = OverrideConfig(**custom_extraction)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb47cf6cb64f16941e24867573f447a6c7700a0e548c605ab3a6c79766903dd3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument namespaces", value=namespaces, expected_type=type_hints["namespaces"])
            check_type(argname="argument custom_consolidation", value=custom_consolidation, expected_type=type_hints["custom_consolidation"])
            check_type(argname="argument custom_extraction", value=custom_extraction, expected_type=type_hints["custom_extraction"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "namespaces": namespaces,
        }
        if description is not None:
            self._values["description"] = description
        if custom_consolidation is not None:
            self._values["custom_consolidation"] = custom_consolidation
        if custom_extraction is not None:
            self._values["custom_extraction"] = custom_extraction

    @builtins.property
    def name(self) -> builtins.str:
        '''(experimental) The name for the strategy.

        :stability: experimental
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the strategy.

        :default: - No description

        :stability: experimental
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespaces(self) -> typing.List[builtins.str]:
        '''(experimental) The namespaces for the strategy Represents a namespace for organizing memory data Use a hierarchical format separated by forward slashes (/).

        Use a hierarchical format separated by forward slashes (/) to organize namespaces logically.
        You can include these defined variables:

        - {sessionId} - the user identifier to be created in the CreateEvent API
        - {memoryStrategyId} - an identifier for an extraction strategy
        - {sessionId} - an identifier for each session

        Example namespace path:
        /strategies/{memoryStrategyId}/actions/{actionId}/sessions/{sessionId}

        After memory creation, this namespace might look like:
        /actor/actor-3afc5aa8fef9/strategy/summarization-fy5c5fwc7/session/session-qj7tpd1kvr8

        :stability: experimental
        '''
        result = self._values.get("namespaces")
        assert result is not None, "Required property 'namespaces' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def custom_consolidation(self) -> typing.Optional[OverrideConfig]:
        '''(experimental) The configuration for the custom consolidation.

        This configuration provides customization to how the model identifies
        and extracts relevant information for memory storage.

        :default: - No custom extraction

        :stability: experimental
        '''
        result = self._values.get("custom_consolidation")
        return typing.cast(typing.Optional[OverrideConfig], result)

    @builtins.property
    def custom_extraction(self) -> typing.Optional[OverrideConfig]:
        '''(experimental) The configuration for the custom extraction.

        This configuration provides customization to how the model identifies
        and extracts relevant information for memory storage.

        :default: - No custom extraction

        :stability: experimental
        '''
        result = self._values.get("custom_extraction")
        return typing.cast(typing.Optional[OverrideConfig], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedStrategyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Memory(
    MemoryBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.Memory",
):
    '''(experimental) Long-term memory store for extracted insights like user preferences, semantic facts and summaries.

    Enables knowledge retention across sessions by storing user preferences (e.g. coding style),
    semantic facts (e.g. learned info) and interaction summaries for context optimization.

    :see: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html
    :stability: experimental
    :resource: AWS::BedrockAgentCore::Memory
    :exampleMetadata: fixture=default infused

    Example::

        # Create a custom execution role
        execution_role = iam.Role(self, "MemoryExecutionRole",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockAgentCoreMemoryBedrockModelInferenceExecutionRolePolicy")
            ]
        )
        
        # Create memory with custom execution role
        memory = agentcore.Memory(self, "MyMemory",
            memory_name="my_memory",
            description="Memory with custom execution role",
            expiration_duration=cdk.Duration.days(90),
            execution_role=execution_role
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        memory_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        expiration_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        memory_strategies: typing.Optional[typing.Sequence[IMemoryStrategy]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param memory_name: (experimental) The name of the memory Valid characters are a-z, A-Z, 0-9, _ (underscore) The name must start with a letter and can be up to 48 characters long Pattern: [a-zA-Z][a-zA-Z0-9_]{0,47}.
        :param description: (experimental) Optional description for the memory Valid characters are a-z, A-Z, 0-9, _ (underscore), - (hyphen) and spaces The description can have up to 200 characters. Default: - No description
        :param execution_role: (experimental) The IAM role that provides permissions for the memory to access AWS services when using custom strategies. Default: - A new role will be created.
        :param expiration_duration: (experimental) Short-term memory expiration in days (between 7 and 365). Sets the short-term (raw event) memory retention. Events older than the specified duration will expire and no longer be stored. Default: - 90 days
        :param kms_key: (experimental) Custom KMS key to use for encryption. Default: - Your data is encrypted with a key that AWS owns and manages for you
        :param memory_strategies: (experimental) If you need long-term memory for context recall across sessions, you can setup memory extraction strategies to extract the relevant memory from the raw events. Default: - No extraction strategies (short term memory only)
        :param tags: (experimental) Tags (optional) A list of key:value pairs of tags to apply to this memory resource. Default: - no tags

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e76fa6dc189b8b63815ed558f95c760b00a4f52735d77ee7738d05646cb0f60)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = MemoryProps(
            memory_name=memory_name,
            description=description,
            execution_role=execution_role,
            expiration_duration=expiration_duration,
            kms_key=kms_key,
            memory_strategies=memory_strategies,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromMemoryAttributes")
    @builtins.classmethod
    def from_memory_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        memory_arn: builtins.str,
        role_arn: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        kms_key_arn: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        updated_at: typing.Optional[builtins.str] = None,
    ) -> IMemory:
        '''(experimental) Creates an Memory reference from an existing memory's attributes.

        :param scope: - The construct scope.
        :param id: - Identifier of the construct.
        :param memory_arn: (experimental) The ARN of the memory.
        :param role_arn: (experimental) The ARN of the IAM role associated to the memory.
        :param created_at: (experimental) The created timestamp of the memory. Default: undefined - No created timestamp is provided
        :param kms_key_arn: (experimental) Optional KMS encryption key associated with this memory. Default: undefined - An AWS managed key is used
        :param status: (experimental) The status of the memory. Default: undefined - No status is provided
        :param updated_at: (experimental) When this memory was last updated. Default: undefined - No last updated timestamp is provided

        :return: An IBrowserCustom reference to the existing browser

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d1ef3ab147d318f2cfae70c86258d2aaae60999cbf091f81112ab74f9a797f8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = MemoryAttributes(
            memory_arn=memory_arn,
            role_arn=role_arn,
            created_at=created_at,
            kms_key_arn=kms_key_arn,
            status=status,
            updated_at=updated_at,
        )

        return typing.cast(IMemory, jsii.sinvoke(cls, "fromMemoryAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addMemoryStrategy")
    def add_memory_strategy(self, memory_strategy: IMemoryStrategy) -> None:
        '''(experimental) Add memory strategy to the memory.

        :param memory_strategy: -

        :default: - No memory strategies.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d88d525f5db5bcf500ab4eef917307847de4249de07b49c2ddf92dd64065092b)
            check_type(argname="argument memory_strategy", value=memory_strategy, expected_type=type_hints["memory_strategy"])
        return typing.cast(None, jsii.invoke(self, "addMemoryStrategy", [memory_strategy]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="memoryArn")
    def memory_arn(self) -> builtins.str:
        '''(experimental) The ARN of the memory resource.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "memoryArn"))

    @builtins.property
    @jsii.member(jsii_name="memoryId")
    def memory_id(self) -> builtins.str:
        '''(experimental) The id of the memory.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "memoryId"))

    @builtins.property
    @jsii.member(jsii_name="memoryName")
    def memory_name(self) -> builtins.str:
        '''(experimental) The name of the memory.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "memoryName"))

    @builtins.property
    @jsii.member(jsii_name="memoryStrategies")
    def memory_strategies(self) -> typing.List[IMemoryStrategy]:
        '''(experimental) The memory strategies used by the memory.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.List[IMemoryStrategy], jsii.get(self, "memoryStrategies"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The created timestamp of the memory.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the memory.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole]:
        '''(experimental) The execution role of the memory.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole], jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="expirationDuration")
    def expiration_duration(self) -> typing.Optional[_aws_cdk_ceddda9d.Duration]:
        '''(experimental) The expiration days of the memory.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.Duration], jsii.get(self, "expirationDuration"))

    @builtins.property
    @jsii.member(jsii_name="failureReason")
    def failure_reason(self) -> typing.Optional[builtins.str]:
        '''(experimental) The failure reason of the browser.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "failureReason"))

    @builtins.property
    @jsii.member(jsii_name="kmsKey")
    def kms_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) The KMS key used to encrypt the memory.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "kmsKey"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the memory.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Tags applied to this browser resource A map of key-value pairs for resource tagging.

        :default: - No tags applied

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The updated at timestamp of the memory.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updatedAt"))


class Runtime(
    RuntimeBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.Runtime",
):
    '''(experimental) Bedrock Agent Core Runtime Enables running containerized agents with specific network configurations, security settings, and runtime artifacts.

    :see: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime.html
    :stability: experimental
    :resource: AWS::BedrockAgentCore::Runtime
    :exampleMetadata: infused

    Example::

        repository = ecr.Repository(self, "TestRepository",
            repository_name="test-agent-runtime"
        )
        agent_runtime_artifact = agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")
        
        runtime = agentcore.Runtime(self, "MyAgentRuntime",
            runtime_name="myAgent",
            agent_runtime_artifact=agent_runtime_artifact,
            authorizer_configuration=agentcore.RuntimeAuthorizerConfiguration.using_oAuth("https://github.com/.well-known/openid-configuration", "oauth_client_123")
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        agent_runtime_artifact: AgentRuntimeArtifact,
        runtime_name: builtins.str,
        authorizer_configuration: typing.Optional[RuntimeAuthorizerConfiguration] = None,
        description: typing.Optional[builtins.str] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_configuration: typing.Optional[RuntimeNetworkConfiguration] = None,
        protocol_configuration: typing.Optional[ProtocolType] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param agent_runtime_artifact: (experimental) The artifact configuration for the agent runtime Contains the container configuration with ECR URI.
        :param runtime_name: (experimental) The name of the agent runtime Valid characters are a-z, A-Z, 0-9, _ (underscore) Must start with a letter and can be up to 48 characters long Pattern: ^[a-zA-Z][a-zA-Z0-9_]{0,47}$.
        :param authorizer_configuration: (experimental) Authorizer configuration for the agent runtime Use RuntimeAuthorizerConfiguration static methods to create the configuration. Default: - RuntimeAuthorizerConfiguration.iam() (IAM authentication)
        :param description: (experimental) Optional description for the agent runtime. Default: - No description Length Minimum: 1 , Maximum: 1200
        :param environment_variables: (experimental) Environment variables for the agent runtime - Maximum 50 environment variables - Key: Must be 1-100 characters, start with letter or underscore, contain only letters, numbers, and underscores - Value: Must be 0-2048 characters (per CloudFormation specification). Default: - No environment variables
        :param execution_role: (experimental) The IAM role that provides permissions for the agent runtime If not provided, a role will be created automatically. Default: - A new role will be created
        :param network_configuration: (experimental) Network configuration for the agent runtime. Default: - RuntimeNetworkConfiguration.usingPublicNetwork()
        :param protocol_configuration: (experimental) Protocol configuration for the agent runtime. Default: - ProtocolType.HTTP
        :param tags: (experimental) Tags for the agent runtime A list of key:value pairs of tags to apply to this Runtime resource. Default: {} - no tags

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d3c75c162a496b2457c5b16d4ab318237dd0f6028aaaa787f5968728ad5bea40)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RuntimeProps(
            agent_runtime_artifact=agent_runtime_artifact,
            runtime_name=runtime_name,
            authorizer_configuration=authorizer_configuration,
            description=description,
            environment_variables=environment_variables,
            execution_role=execution_role,
            network_configuration=network_configuration,
            protocol_configuration=protocol_configuration,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromAgentRuntimeAttributes")
    @builtins.classmethod
    def from_agent_runtime_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        agent_runtime_arn: builtins.str,
        agent_runtime_id: builtins.str,
        agent_runtime_name: builtins.str,
        role_arn: builtins.str,
        agent_runtime_version: typing.Optional[builtins.str] = None,
        agent_status: typing.Optional[builtins.str] = None,
        created_at: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        last_updated_at: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    ) -> IBedrockAgentRuntime:
        '''(experimental) Import an existing Agent Runtime using attributes This allows you to reference an Agent Runtime that was created outside of CDK.

        :param scope: The construct scope.
        :param id: The construct id.
        :param agent_runtime_arn: (experimental) The ARN of the agent runtime.
        :param agent_runtime_id: (experimental) The ID of the agent runtime.
        :param agent_runtime_name: (experimental) The name of the agent runtime.
        :param role_arn: (experimental) The IAM role ARN.
        :param agent_runtime_version: (experimental) The version of the agent runtime When importing a runtime and this is not specified or undefined, endpoints created on this runtime will point to version "1" unless explicitly overridden. Default: - undefined
        :param agent_status: (experimental) The current status of the agent runtime. Default: - Status not available
        :param created_at: (experimental) The time at which the runtime was created. Default: - Creation time not available
        :param description: (experimental) The description of the agent runtime. Default: - No description
        :param last_updated_at: (experimental) The time at which the runtime was last updated. Default: - Last update time not available
        :param security_groups: (experimental) The security groups for this runtime, if in a VPC. Default: - By default, the runtime is not in a VPC.

        :return: An IBedrockAgentRuntime instance representing the imported runtime

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05959bcf4b4bc641f8cd5e6663c98667c22ec794751ac633e033ccabebf69312)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = AgentRuntimeAttributes(
            agent_runtime_arn=agent_runtime_arn,
            agent_runtime_id=agent_runtime_id,
            agent_runtime_name=agent_runtime_name,
            role_arn=role_arn,
            agent_runtime_version=agent_runtime_version,
            agent_status=agent_status,
            created_at=created_at,
            description=description,
            last_updated_at=last_updated_at,
            security_groups=security_groups,
        )

        return typing.cast(IBedrockAgentRuntime, jsii.sinvoke(cls, "fromAgentRuntimeAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="addEndpoint")
    def add_endpoint(
        self,
        endpoint_name: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> "RuntimeEndpoint":
        '''(experimental) Add an endpoint to this runtime This is a convenience method that creates a RuntimeEndpoint associated with this runtime.

        :param endpoint_name: The name of the endpoint.
        :param description: (experimental) Description for the endpoint, Must be between 1 and 1200 characters. Default: - No description
        :param version: (experimental) Override the runtime version for this endpoint. Default: 1

        :return: The created RuntimeEndpoint

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c9f210c62e6b8a9cc9f91d2223cadcf66989308f610a152e24937c2e6f75fea)
            check_type(argname="argument endpoint_name", value=endpoint_name, expected_type=type_hints["endpoint_name"])
        options = AddEndpointOptions(description=description, version=version)

        return typing.cast("RuntimeEndpoint", jsii.invoke(self, "addEndpoint", [endpoint_name, options]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent runtime.

        :return: a token representing the ARN of this agent runtime

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeArn"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArtifact")
    def agent_runtime_artifact(self) -> AgentRuntimeArtifact:
        '''(experimental) The artifact configuration for the agent runtime.

        :stability: experimental
        '''
        return typing.cast(AgentRuntimeArtifact, jsii.get(self, "agentRuntimeArtifact"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeId")
    def agent_runtime_id(self) -> builtins.str:
        '''(experimental) The unique identifier of the agent runtime.

        :return: a token representing the ID of this agent runtime

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeId"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeName")
    def agent_runtime_name(self) -> builtins.str:
        '''(experimental) The name of the agent runtime.

        :return: a token representing the name of this agent runtime

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeName"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the agent runtime.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeVersion")
    def agent_runtime_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The version of the agent runtime.

        :return: a token representing the version of this agent runtime

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentRuntimeVersion"))

    @builtins.property
    @jsii.member(jsii_name="agentStatus")
    def agent_status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the agent runtime.

        :return: a token representing the status of this agent runtime

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentStatus"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The timestamp when the agent runtime was created.

        :return: a token representing the creation timestamp of this agent runtime

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional description for the agent runtime.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The timestamp when the agent runtime was last updated.

        :return: a token representing the last update timestamp of this agent runtime

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))


class RuntimeEndpoint(
    RuntimeEndpointBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.RuntimeEndpoint",
):
    '''(experimental) Bedrock Agent Core Runtime Endpoint Provides a stable endpoint for invoking agent runtimes with versioning support.

    :see: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-endpoint.html
    :stability: experimental
    :resource: AWS::BedrockAgentCore::RuntimeEndpoint
    :exampleMetadata: infused

    Example::

        repository = ecr.Repository(self, "TestRepository",
            repository_name="test-agent-runtime"
        )
        
        runtime = agentcore.Runtime(self, "MyAgentRuntime",
            runtime_name="myAgent",
            agent_runtime_artifact=agentcore.AgentRuntimeArtifact.from_ecr_repository(repository, "v1.0.0")
        )
        
        prod_endpoint = runtime.add_endpoint("production",
            version="1",
            description="Stable production endpoint - pinned to v1"
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        agent_runtime_id: builtins.str,
        endpoint_name: builtins.str,
        agent_runtime_version: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param agent_runtime_id: (experimental) The ID of the agent runtime to associate with this endpoint This is the unique identifier of the runtime resource Pattern: ^[a-zA-Z][a-zA-Z0-9_]{0,99}-[a-zA-Z0-9]{10}$.
        :param endpoint_name: (experimental) The name of the agent runtime endpoint Valid characters are a-z, A-Z, 0-9, _ (underscore) Must start with a letter and can be up to 48 characters long Pattern: ^[a-zA-Z][a-zA-Z0-9_]{0,47}$.
        :param agent_runtime_version: (experimental) The version of the agent runtime to use for this endpoint If not specified, the endpoint will point to version "1" of the runtime. Pattern: ^([1-9][0-9]{0,4})$ Default: "1"
        :param description: (experimental) Optional description for the agent runtime endpoint Length Minimum: 1 , Maximum: 256. Default: - No description
        :param tags: (experimental) Tags for the agent runtime endpoint A list of key:value pairs of tags to apply to this RuntimeEndpoint resource Pattern: ^[a-zA-Z0-9\\s._:/=+@-]*$. Default: {} - no tags

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c08f9203e17afcdac6a5a193e263989301ad529a8b9defc871c88e757bc1f18a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RuntimeEndpointProps(
            agent_runtime_id=agent_runtime_id,
            endpoint_name=endpoint_name,
            agent_runtime_version=agent_runtime_version,
            description=description,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromRuntimeEndpointAttributes")
    @builtins.classmethod
    def from_runtime_endpoint_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        agent_runtime_arn: builtins.str,
        agent_runtime_endpoint_arn: builtins.str,
        endpoint_name: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        endpoint_id: typing.Optional[builtins.str] = None,
        last_updated_at: typing.Optional[builtins.str] = None,
        live_version: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        target_version: typing.Optional[builtins.str] = None,
    ) -> IRuntimeEndpoint:
        '''(experimental) Import an existing Agent Runtime Endpoint using attributes This allows you to reference an Agent Runtime Endpoint that was created outside of CDK.

        :param scope: The construct scope.
        :param id: The construct id.
        :param agent_runtime_arn: (experimental) The ARN of the parent agent runtime.
        :param agent_runtime_endpoint_arn: (experimental) The ARN of the runtime endpoint.
        :param endpoint_name: (experimental) The name of the runtime endpoint.
        :param created_at: (experimental) When the endpoint was created. Default: - Creation time not available
        :param description: (experimental) The description of the runtime endpoint. Default: - No description
        :param endpoint_id: (experimental) The unique identifier of the runtime endpoint. Default: - Endpoint ID not available
        :param last_updated_at: (experimental) When the endpoint was last updated. Default: - Last update time not available
        :param live_version: (experimental) The live version of the agent runtime that is currently serving requests. Default: - Live version not available
        :param status: (experimental) The current status of the runtime endpoint. Default: - Status not available
        :param target_version: (experimental) The target version the endpoint is transitioning to (during updates). Default: - Target version not available

        :return: An IRuntimeEndpoint instance representing the imported endpoint

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7aac4684398202199ff45b016211ef025a54472a69d037cfafe89eaa76bac9ac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = RuntimeEndpointAttributes(
            agent_runtime_arn=agent_runtime_arn,
            agent_runtime_endpoint_arn=agent_runtime_endpoint_arn,
            endpoint_name=endpoint_name,
            created_at=created_at,
            description=description,
            endpoint_id=endpoint_id,
            last_updated_at=last_updated_at,
            live_version=live_version,
            status=status,
            target_version=target_version,
        )

        return typing.cast(IRuntimeEndpoint, jsii.sinvoke(cls, "fromRuntimeEndpointAttributes", [scope, id, attrs]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeArn")
    def agent_runtime_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent runtime associated with this endpoint.

        :return: a token representing the ARN of the agent runtime

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeArn"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeEndpointArn")
    def agent_runtime_endpoint_arn(self) -> builtins.str:
        '''(experimental) The ARN of the agent runtime endpoint.

        :return: a token representing the ARN of this agent runtime endpoint

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeEndpointArn"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeId")
    def agent_runtime_id(self) -> builtins.str:
        '''(experimental) The ID of the agent runtime associated with this endpoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeId"))

    @builtins.property
    @jsii.member(jsii_name="agentRuntimeVersion")
    def agent_runtime_version(self) -> builtins.str:
        '''(experimental) The version of the agent runtime used by this endpoint.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "agentRuntimeVersion"))

    @builtins.property
    @jsii.member(jsii_name="endpointId")
    def endpoint_id(self) -> builtins.str:
        '''(experimental) The unique identifier of the runtime endpoint.

        :return: a token representing the ID of this endpoint

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointId"))

    @builtins.property
    @jsii.member(jsii_name="endpointName")
    def endpoint_name(self) -> builtins.str:
        '''(experimental) The name of the endpoint.

        :return: a token representing the name of this endpoint

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "endpointName"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The timestamp when the endpoint was created.

        :return: a token representing the creation timestamp of this endpoint

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) Optional description for the endpoint.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) When this endpoint was last updated.

        :return: a token representing the last update timestamp of this endpoint

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))

    @builtins.property
    @jsii.member(jsii_name="liveVersion")
    def live_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The live version of the endpoint.

        :return: a token representing the live version of this endpoint

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "liveVersion"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the endpoint.

        :return: a token representing the status of this endpoint

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="targetVersion")
    def target_version(self) -> typing.Optional[builtins.str]:
        '''(experimental) The target version of the endpoint.

        :return: a token representing the target version of this endpoint

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetVersion"))


class BrowserCustom(
    BrowserCustomBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.BrowserCustom",
):
    '''(experimental) Browser resource for AWS Bedrock Agent Core.

    Provides a browser environment for web automation and interaction.

    :see: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser.html
    :stability: experimental
    :resource: AWS::BedrockAgentCore::BrowserCustom
    :exampleMetadata: fixture=default infused

    Example::

        # Create a custom execution role
        execution_role = iam.Role(self, "BrowserExecutionRole",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockAgentCoreBrowserExecutionRolePolicy")
            ]
        )
        
        # Create browser with custom execution role
        browser = agentcore.BrowserCustom(self, "MyBrowser",
            browser_custom_name="my_browser",
            description="Browser with custom execution role",
            network_configuration=agentcore.BrowserNetworkConfiguration.using_public_network(),
            execution_role=execution_role
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        browser_custom_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_configuration: typing.Optional[BrowserNetworkConfiguration] = None,
        recording_config: typing.Optional[typing.Union[RecordingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param browser_custom_name: (experimental) The name of the browser Valid characters are a-z, A-Z, 0-9, _ (underscore) The name must start with a letter and can be up to 48 characters long Pattern: [a-zA-Z][a-zA-Z0-9_]{0,47}.
        :param description: (experimental) Optional description for the browser Valid characters are a-z, A-Z, 0-9, _ (underscore), - (hyphen) and spaces The description can have up to 200 characters. Default: - No description
        :param execution_role: (experimental) The IAM role that provides permissions for the browser to access AWS services. Default: - A new role will be created
        :param network_configuration: (experimental) Network configuration for browser. Default: - PUBLIC network mode
        :param recording_config: (experimental) Recording configuration for browser. Default: - No recording configuration
        :param tags: (experimental) Tags (optional) A list of key:value pairs of tags to apply to this Browser resource. Default: {} - no tags

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1158b103a85cbce3d28e980992f8b82595d918f92538cc576de16ed55fbc4071)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BrowserCustomProps(
            browser_custom_name=browser_custom_name,
            description=description,
            execution_role=execution_role,
            network_configuration=network_configuration,
            recording_config=recording_config,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromBrowserCustomAttributes")
    @builtins.classmethod
    def from_browser_custom_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        browser_arn: builtins.str,
        role_arn: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        last_updated_at: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> IBrowserCustom:
        '''(experimental) Creates an Browser Custom reference from an existing browser's attributes.

        :param scope: - The construct scope.
        :param id: - Identifier of the construct.
        :param browser_arn: (experimental) The ARN of the agent.
        :param role_arn: (experimental) The ARN of the IAM role associated to the browser.
        :param created_at: (experimental) The created timestamp of the browser. Default: undefined - No created timestamp is provided
        :param last_updated_at: (experimental) When this browser was last updated. Default: undefined - No last updated timestamp is provided
        :param security_groups: (experimental) The security groups for this browser, if in a VPC. Default: - By default, the browser is not in a VPC.
        :param status: (experimental) The status of the browser. Default: undefined - No status is provided

        :return: An IBrowserCustom reference to the existing browser

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e143bea37e02f65f29c3f3dfd523e8452322bb7ee9d57f98ab6bd947e40e261)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = BrowserCustomAttributes(
            browser_arn=browser_arn,
            role_arn=role_arn,
            created_at=created_at,
            last_updated_at=last_updated_at,
            security_groups=security_groups,
            status=status,
        )

        return typing.cast(IBrowserCustom, jsii.sinvoke(cls, "fromBrowserCustomAttributes", [scope, id, attrs]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="browserArn")
    def browser_arn(self) -> builtins.str:
        '''(experimental) The ARN of the browser resource.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "browserArn"))

    @builtins.property
    @jsii.member(jsii_name="browserId")
    def browser_id(self) -> builtins.str:
        '''(experimental) The id of the browser.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "browserId"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role associated to the browser.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the browser.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="networkConfiguration")
    def network_configuration(self) -> BrowserNetworkConfiguration:
        '''(experimental) The network configuration of the browser.

        :stability: experimental
        '''
        return typing.cast(BrowserNetworkConfiguration, jsii.get(self, "networkConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The created timestamp of the browser.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the browser.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="failureReason")
    def failure_reason(self) -> typing.Optional[builtins.str]:
        '''(experimental) The failure reason of the browser.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "failureReason"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The last updated timestamp of the browser.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))

    @builtins.property
    @jsii.member(jsii_name="recordingConfig")
    def recording_config(self) -> typing.Optional[RecordingConfig]:
        '''(experimental) The recording configuration of the browser.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[RecordingConfig], jsii.get(self, "recordingConfig"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the browser.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Tags applied to this browser resource A map of key-value pairs for resource tagging.

        :default: - No tags applied

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))


class CodeInterpreterCustom(
    CodeInterpreterCustomBase,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-bedrock-agentcore-alpha.CodeInterpreterCustom",
):
    '''(experimental) Custom code interpreter resource for AWS Bedrock Agent Core.

    Provides a sandboxed environment for code execution with configurable network access.

    :see: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter.html
    :stability: experimental
    :resource: AWS::BedrockAgentCore::CodeInterpreterCustom
    :exampleMetadata: fixture=default infused

    Example::

        # Create a custom execution role
        execution_role = iam.Role(self, "CodeInterpreterExecutionRole",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com")
        )
        
        # Create code interpreter with custom execution role
        code_interpreter = agentcore.CodeInterpreterCustom(self, "MyCodeInterpreter",
            code_interpreter_custom_name="my_code_interpreter",
            description="Code interpreter with custom execution role",
            network_configuration=agentcore.CodeInterpreterNetworkConfiguration.using_public_network(),
            execution_role=execution_role
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        code_interpreter_custom_name: builtins.str,
        description: typing.Optional[builtins.str] = None,
        execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        network_configuration: typing.Optional[CodeInterpreterNetworkConfiguration] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param code_interpreter_custom_name: (experimental) The name of the code interpreter Valid characters are a-z, A-Z, 0-9, _ (underscore) The name must start with a letter and can be up to 48 characters long Pattern: [a-zA-Z][a-zA-Z0-9_]{0,47}.
        :param description: (experimental) Optional description for the code interpreter Valid characters are a-z, A-Z, 0-9, _ (underscore), - (hyphen) and spaces The description can have up to 200 characters. Default: - No description
        :param execution_role: (experimental) The IAM role that provides permissions for the code interpreter to access AWS services. Default: - A new role will be created.
        :param network_configuration: (experimental) Network configuration for code interpreter. Default: - PUBLIC network mode
        :param tags: (experimental) Tags (optional) A list of key:value pairs of tags to apply to this Code Interpreter resource. Default: {} - no tags

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97059670dcd4750424fbb12f68be0e5fc4005cf0b64c6621aff517561009ef5a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CodeInterpreterCustomProps(
            code_interpreter_custom_name=code_interpreter_custom_name,
            description=description,
            execution_role=execution_role,
            network_configuration=network_configuration,
            tags=tags,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromCodeInterpreterCustomAttributes")
    @builtins.classmethod
    def from_code_interpreter_custom_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        code_interpreter_arn: builtins.str,
        role_arn: builtins.str,
        created_at: typing.Optional[builtins.str] = None,
        last_updated_at: typing.Optional[builtins.str] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        status: typing.Optional[builtins.str] = None,
    ) -> ICodeInterpreterCustom:
        '''(experimental) Creates an Code Interpreter Custom reference from an existing code interpreter's attributes.

        :param scope: - The construct scope.
        :param id: - Identifier of the construct.
        :param code_interpreter_arn: (experimental) The ARN of the agent.
        :param role_arn: (experimental) The ARN of the IAM role associated to the code interpreter.
        :param created_at: (experimental) The created timestamp of the code interpreter. Default: undefined - No created timestamp is provided
        :param last_updated_at: (experimental) When this code interpreter was last updated. Default: undefined - No last updated timestamp is provided
        :param security_groups: (experimental) The security groups for this code interpreter, if in a VPC. Default: - By default, the code interpreter is not in a VPC.
        :param status: (experimental) The status of the code interpreter. Default: undefined - No status is provided

        :return: An ICodeInterpreterCustom reference to the existing code interpreter

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da00b980caf9bfd0b84d4f7c4ec856774682fff062a743c88616a5a9368f2a09)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = CodeInterpreterCustomAttributes(
            code_interpreter_arn=code_interpreter_arn,
            role_arn=role_arn,
            created_at=created_at,
            last_updated_at=last_updated_at,
            security_groups=security_groups,
            status=status,
        )

        return typing.cast(ICodeInterpreterCustom, jsii.sinvoke(cls, "fromCodeInterpreterCustomAttributes", [scope, id, attrs]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="codeInterpreterArn")
    def code_interpreter_arn(self) -> builtins.str:
        '''(experimental) The ARN of the code interpreter resource.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "codeInterpreterArn"))

    @builtins.property
    @jsii.member(jsii_name="codeInterpreterId")
    def code_interpreter_id(self) -> builtins.str:
        '''(experimental) The id of the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "codeInterpreterId"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''(experimental) The IAM role that provides permissions for the code interpreter to access AWS services.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> _aws_cdk_aws_iam_ceddda9d.IPrincipal:
        '''(experimental) The principal to grant permissions to.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IPrincipal, jsii.get(self, "grantPrincipal"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        '''(experimental) The name of the code interpreter.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="networkConfiguration")
    def network_configuration(self) -> CodeInterpreterNetworkConfiguration:
        '''(experimental) The network configuration of the code interpreter.

        :stability: experimental
        '''
        return typing.cast(CodeInterpreterNetworkConfiguration, jsii.get(self, "networkConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The created timestamp of the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        '''(experimental) The description of the code interpreter.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="failureReason")
    def failure_reason(self) -> typing.Optional[builtins.str]:
        '''(experimental) The failure reason of the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "failureReason"))

    @builtins.property
    @jsii.member(jsii_name="lastUpdatedAt")
    def last_updated_at(self) -> typing.Optional[builtins.str]:
        '''(experimental) The last updated timestamp of the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "lastUpdatedAt"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> typing.Optional[builtins.str]:
        '''(experimental) The status of the code interpreter.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''(experimental) Tags applied to this code interpreter resource A map of key-value pairs for resource tagging.

        :default: - No tags applied

        :stability: experimental
        '''
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tags"))


__all__ = [
    "AddEndpointOptions",
    "AgentRuntimeArtifact",
    "AgentRuntimeAttributes",
    "BrowserCustom",
    "BrowserCustomAttributes",
    "BrowserCustomBase",
    "BrowserCustomProps",
    "BrowserNetworkConfiguration",
    "CodeInterpreterCustom",
    "CodeInterpreterCustomAttributes",
    "CodeInterpreterCustomBase",
    "CodeInterpreterCustomProps",
    "CodeInterpreterNetworkConfiguration",
    "IBedrockAgentRuntime",
    "IBrowserCustom",
    "ICodeInterpreterCustom",
    "IMemory",
    "IMemoryStrategy",
    "IRuntimeEndpoint",
    "InvocationConfiguration",
    "ManagedMemoryStrategy",
    "ManagedStrategyProps",
    "Memory",
    "MemoryAttributes",
    "MemoryBase",
    "MemoryProps",
    "MemoryStrategy",
    "MemoryStrategyCommonProps",
    "MemoryStrategyType",
    "NetworkConfiguration",
    "OverrideConfig",
    "ProtocolType",
    "RecordingConfig",
    "Runtime",
    "RuntimeAuthorizerConfiguration",
    "RuntimeBase",
    "RuntimeEndpoint",
    "RuntimeEndpointAttributes",
    "RuntimeEndpointBase",
    "RuntimeEndpointProps",
    "RuntimeNetworkConfiguration",
    "RuntimeProps",
    "SelfManagedMemoryStrategy",
    "SelfManagedStrategyProps",
    "TriggerConditions",
    "VpcConfigProps",
]

publication.publish()

def _typecheckingstub__175b1aee490f549cb19d8945b728786765752ce863f0a55d8732e6f777128e9b(
    *,
    description: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__604d365a86a290247af7992e6be98b47b27307a51f5ffdb436c6c1ea4019453a(
    directory: builtins.str,
    *,
    asset_name: typing.Optional[builtins.str] = None,
    build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    build_secrets: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    build_ssh: typing.Optional[builtins.str] = None,
    cache_disabled: typing.Optional[builtins.bool] = None,
    cache_from: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]]] = None,
    cache_to: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerCacheOption, typing.Dict[builtins.str, typing.Any]]] = None,
    display_name: typing.Optional[builtins.str] = None,
    file: typing.Optional[builtins.str] = None,
    invalidation: typing.Optional[typing.Union[_aws_cdk_aws_ecr_assets_ceddda9d.DockerImageAssetInvalidationOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    network_mode: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.NetworkMode] = None,
    outputs: typing.Optional[typing.Sequence[builtins.str]] = None,
    platform: typing.Optional[_aws_cdk_aws_ecr_assets_ceddda9d.Platform] = None,
    target: typing.Optional[builtins.str] = None,
    extra_hash: typing.Optional[builtins.str] = None,
    exclude: typing.Optional[typing.Sequence[builtins.str]] = None,
    follow_symlinks: typing.Optional[_aws_cdk_ceddda9d.SymlinkFollowMode] = None,
    ignore_mode: typing.Optional[_aws_cdk_ceddda9d.IgnoreMode] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5378ad450d2e50130983bd4e4c0d41f7ddc7b25ef75b63e107cdace81383db49(
    repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    tag: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bedccb351eb2d100e954ac8354c709d22031237b55a8c9439b4fa56a9c488298(
    scope: _constructs_77d1e7e8.Construct,
    runtime: Runtime,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__521eb5a43c1809da91e6b913f83fa6446f5b8ac2c440a565fa2764b3cd9f4ad8(
    *,
    agent_runtime_arn: builtins.str,
    agent_runtime_id: builtins.str,
    agent_runtime_name: builtins.str,
    role_arn: builtins.str,
    agent_runtime_version: typing.Optional[builtins.str] = None,
    agent_status: typing.Optional[builtins.str] = None,
    created_at: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    last_updated_at: typing.Optional[builtins.str] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14ea7632e5df00d60970b59a9a4cb5f38d208fd7a26740e3444fd2b1e4b432ba(
    *,
    browser_arn: builtins.str,
    role_arn: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    last_updated_at: typing.Optional[builtins.str] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    status: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c723ceb06d7434df1c72a1865f418037daeeda29f30194820f0872da7d50bbe8(
    *,
    browser_custom_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_configuration: typing.Optional[BrowserNetworkConfiguration] = None,
    recording_config: typing.Optional[typing.Union[RecordingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f96ed57c1afc648e15cebfa320e03f93dc4c161c09d253072930e4b7d4e4ed24(
    *,
    code_interpreter_arn: builtins.str,
    role_arn: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    last_updated_at: typing.Optional[builtins.str] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    status: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e75974384deaaee0d0812c3570b15b1adf0a19fbd67095aea1229a4d3d5c5c05(
    *,
    code_interpreter_custom_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_configuration: typing.Optional[CodeInterpreterNetworkConfiguration] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b1a5766ae93ba39d5e7df12bdfc35c2a7d298375e7689fbc39a3c76d50d2639(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3208bdcc07b3a3b3b7ac0ed80c7b033074eab2659722a2dec0d8400cf5da5af8(
    actions: typing.Sequence[builtins.str],
    resources: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e4ed0dc7cd812fb1d50239f33a79cd0a5de1be6488c8ee24a3b016a546ef94b(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e37d3744eaf4f98404f5daccedff6e7a637774c39193ceadfd0f88c7aa16d50(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b28241dea68e79093525ede5e9deed8adeda944e89126bbcebe733fd16561495(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3beecc1a8cde07edfff6ed6fa9c6deb0e5c35524c1b4ca5bc87c39f95ca1f565(
    metric_name: builtins.str,
    dimensions: typing.Mapping[builtins.str, builtins.str],
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4826f7478acda3a04d53cc2e00e999d28d4b6af89d40b4863b0007b08c0b26bf(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da9382b030a7d475c5afa4286f7e177b609a5f61d4d9d40b1767f5c1e99b8815(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd8850bcf1d06baf4b66c051e33ef652a6c75bc169744326c9d541535c3f3ca7(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efd83ae8402a4ac91c4d9cee61087a64dc24f53da2f48b59aa2cc85cde883b29(
    metric_name: builtins.str,
    dimensions: typing.Mapping[builtins.str, builtins.str],
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9182d2fd8511b983f694d71df771315bd2911e5e5d9482b933161a628210ec54(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e825fd71c16a04ffa07fa3e9ff9d61d6e478bdf2f90788eba67bba76e9f38ccb(
    metric_name: builtins.str,
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cf7f7691dff5fcb719882b3a76ff7b4a55b686f01244cf9ab3c1ee39a4dd4fc(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6be7d90ffdb2f66b76b997f0926ae3ff14c53cc65c008f5a0591e3f4676265a(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfb1295c98675d8b1f487abc85bf1d69ec7ac709035de1d15c83e328863a23ec(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea0c6d4b07cd9212bb39f789638d8a9a6af30cbc0157a19bcd58f6b94d852755(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1768ca682c2fd421a544ff8111e6e6985b07e3d62cdc62c35ef9cee5896ce2e(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04274b315577b6819dda4346fc076850f28656449a559f5561ca7d53df97f5e3(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ec65ea8e752705bafc58f0d6cacd39d556973c472ffb0789fa4af3ebcce4bcc(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d24a36658edbfd7ecf76e5be971a6012fc93c641f1a510d1ddfd95730be1d7db(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4df790d3e336e48159d1eef607374eaf8f903928d69bd2620e375c4794e4fb3(
    metric_name: builtins.str,
    dimensions: typing.Mapping[builtins.str, builtins.str],
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eedad4c7938113f5f34f301a9b648ae40f5400a9e4de351b0186137052a65fab(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__669e8f3a0db7a0b0e3787f22af4e559b8709590c28a9b79f240d11855cd87a11(
    metric_name: builtins.str,
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5ade6561c63063084b2bd832a2df3362c624482ddaf7b7207ebec55d3e5431b(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79fd1126b940aa58648080ebef78a6ecac9291a3f4e257a9e9b8a3b62fb84e5a(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b950226f77f1b8ff84aba977a1f05f62ed459462976db6648d94a67e1e1ef8cf(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4e3175daf088ea941aee60546645fc39148e3a11ab2b2e5d897a48eff09f4e0(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e9e3e47628eaf2b6a4ffa31b2d7904f6d5438386a823eeca9d34b97f6f484df(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1ba6d29d64132509e28874cca93c8505709d69d09be77f6f547e643a9774030(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a457d9a5a92b2c5dd54c5d40968692e34fd532950d041ea5bfd0de913373be6(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c3efca2cc63cffb669b48299f658d617bda63982dc81fa5aa921c81c38ca079(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7fcbbdfb908085fece3b62e0ffaf13f969e5bedd85b66a5c13523ce5bbee646(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__525b2d326cfe421d9a86d322af9dc60a4ed2bb6edc363fe98cfa6d82ff3adc06(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af17b3916084293603368124beefd4ec59dde44dc47b240d7c9a1ec0f2f5ffa5(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__783d0a6fd1dc20ff0f9527e5c3a52633d4321b96341e6b9bc5d3fa0e92dc5dfe(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9f0a0f5b7fbecabe02b1b20a8835379801ca7f66484f1dd2ef68046ff8b462f(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c589e19a59d911709d856e20382d97b619ddb3a73bbe0dee0153bfc97d443b7c(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94eb3e104c0dd678b10cd6541492be79335617ce87b76c7e823bbc387f58660e(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9345c8520d55c1b82df6b4c9358835ed22ef5781b504459d222e3fc6908b84c7(
    metric_name: builtins.str,
    dimensions: typing.Mapping[builtins.str, builtins.str],
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22ff2e593babb16dbf3ae7775b5b673ea5bc68bba3e2e5317817e4a1a5206a17(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a0a57ceae64fde7d7d2cfe0668f54aa401bbf9dcd02a1c202ab70648e8cda21(
    metric_name: builtins.str,
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e61b20f12b812c882b8260200f86a0153fe5fbde4437c6d474693246202a1b9(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9002a7efe6fb5cf7e675e605de960b66ee27aeceb3ef6161eac905e343326468(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__934b8b491b04ba3c7c4ab4f5bc06c324dbefd303c41cbc2cfa977906701fa994(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa543deca8fc3f65b1c914de7ff1c671f34fc56d017dd3a14ead3387b906c0c4(
    *,
    s3_location: typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]],
    topic: _aws_cdk_aws_sns_ceddda9d.ITopic,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9656ac57c24ef4e4e75d86e1e22eccddbeda2a4c2f59b55521bc042a2350d17c(
    strategy_type: MemoryStrategyType,
    *,
    namespaces: typing.Sequence[builtins.str],
    custom_consolidation: typing.Optional[typing.Union[OverrideConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_extraction: typing.Optional[typing.Union[OverrideConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__026d68ecbae145c075bcc9aa152bf018434394cf6d580dcb55ada773bcffda7b(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6a086dd3c259b4f5133e8dcca3563182c7cc9f12c0de8e826898a8aa640669c(
    *,
    memory_arn: builtins.str,
    role_arn: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    kms_key_arn: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    updated_at: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__574392a6603a24fac59c9a505b5e2ff912c7921a0c811d31aaf821e33095a259(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80f21eef09775f5de00521f704cd0b377a899072ad12f31d3c102e3fcba11ff5(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c6e4dd70011581876e2bb5e8f8c08ac5c3444fd18ed45b7f0cff62c5076e299(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6789868eda605d017128a6c6f954d81b5ef91ae498ca9b98f70464d6766b7fdd(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22d835385ded311b3a50da18cd698dd96efa8b025c2ce811f6b2c37cf0dcfd7a(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e45f2d16955307339b561c5f88315e38b6e333658c3c42bf5a60ebfe2401865(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0ec9374ec0867626f333d6a0e1b2e28e0bdb667583aee6e3be29fed5279bb21(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be1c7af8fe6270d50b6d982667d42ab7e139c4f172018cd2035904bd5d7ff917(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebc2c8cd9c54c3d6983b81accbc7ae829b363a07574e1fe80dac1e83df78ac00(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75b65dac82aa42a649070040d4a89e636efd205f740e9648e93babd0b2fdeee2(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__590ba37ea58d7dff8c2d3fc8274cc9987427363e687967c1d3958d73cbc53039(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f53f70948f0d97aeb01fc6c9fd678ba05fbe2b91bfb844ed7ea119b30028142(
    metric_name: builtins.str,
    dimensions: typing.Mapping[builtins.str, builtins.str],
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9e54bcc7e67cf46e5411aaa6f13470ba871429e3c67f47fa25598bc844c2d35(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61fe7dbf381a793e49e0d24bad4f6af5b13e7d599048ff0dfa6bc01da7c285a9(
    metric_name: builtins.str,
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__285e37e135c8ed6622ae06a06eac22ac25d53d96ce2553b060d7ddf527d730b3(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec8b37ef906686d3aceb55dac9ac696a112df78300ecb5165e0f8c21d6c442b8(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12709904e77db162aec81a7042ff51a5ef06724c2d2a50b65427d8cc3d0a4513(
    *,
    memory_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    expiration_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    memory_strategies: typing.Optional[typing.Sequence[IMemoryStrategy]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33bd2546f76cfe4b81d759a553b1092fab937231ba1d88a09e69aed7c50ee949(
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1156fe37fe7149a4f863e83246fb36b82ce35366fd78287a7abd74852fa9ecd(
    mode: builtins.str,
    scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3dfe3652e8566d6eb013039b79337022b12d64febe65e86a809b46dff375947(
    *,
    append_to_prompt: builtins.str,
    model: _aws_cdk_aws_bedrock_alpha_3753ded9.IBedrockInvokable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__847016f3fc41e4cdc9b08f4aeed6b6521f23c2c1ef8b55de56db5d14f7dbdc82(
    *,
    enabled: typing.Optional[builtins.bool] = None,
    s3_location: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.Location, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b924023484b6dec8c84698f52f4e325bbda80efa65704ec656d07d774f0f360a(
    user_pool: _aws_cdk_aws_cognito_ceddda9d.IUserPool,
    user_pool_clients: typing.Sequence[_aws_cdk_aws_cognito_ceddda9d.IUserPoolClient],
    allowed_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ac01ece0cc4140cb0b2a31ed95c6b9e03284a2363131d8f59958f4506fdec5f(
    discovery_url: builtins.str,
    allowed_clients: typing.Optional[typing.Sequence[builtins.str]] = None,
    allowed_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0b8de9eb8f6b27c5ad0708ddadcf0e5e78987856a5b94b421cb1abbcc761229(
    discovery_url: builtins.str,
    client_id: builtins.str,
    allowed_audience: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16350f8e803148ae58824c157d92d6b5b360c3802a4018cc1e88f99466e7fa95(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7231f6dcdd2551159f4e644a7b39271f091fade67469f9bf285044a8c4c90b60(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87eb6e84d44b507957213f90c634b593ff68893ef29137a6154e73fa53e18e18(
    actions: typing.Sequence[builtins.str],
    resources: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f464dbb8ec8dc44c2f152bffa0fe6b7e25a72226db47d4575639ab76a3ee504b(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23262a416c2bde8ca6024d06971509afa97486440111e79dfae8c143d05ed9be(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__894ad60671ea950414fd0416fead36cee5e0bc1348fcb31b422ba8e37ea00c08(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6a2aba3c163e6d2d8cfa3127ef4170f55abf85a15cea83297552f1fe625776d(
    metric_name: builtins.str,
    dimensions: typing.Mapping[builtins.str, builtins.str],
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8f995850b550d0ef0b0c5967813f910df0c54b53b6273e50eef58f9c9a599ff(
    *,
    agent_runtime_arn: builtins.str,
    agent_runtime_endpoint_arn: builtins.str,
    endpoint_name: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    endpoint_id: typing.Optional[builtins.str] = None,
    last_updated_at: typing.Optional[builtins.str] = None,
    live_version: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    target_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07caa672d91c2d444bbd6350d0c5232e8b425f0f99ff16fa910ac554ef216410(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7edf14b5674c2c3647a66c54aa24ffa82abf23b571539cd8f02aa354e64da16a(
    *,
    agent_runtime_id: builtins.str,
    endpoint_name: builtins.str,
    agent_runtime_version: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3fca872b84d08855284949a94ef7ceab6679568661613e4224125dbf7add5d5(
    mode: builtins.str,
    scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b65f23ce4df9170ab1ea5e330f24e42113b36afa69e504b887bda27e2e0919b(
    scope: _constructs_77d1e7e8.Construct,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e60d912f60dcec4a97a088e67e9b6da136fd8fbd51038c0380995a1946e1724f(
    *,
    agent_runtime_artifact: AgentRuntimeArtifact,
    runtime_name: builtins.str,
    authorizer_configuration: typing.Optional[RuntimeAuthorizerConfiguration] = None,
    description: typing.Optional[builtins.str] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_configuration: typing.Optional[RuntimeNetworkConfiguration] = None,
    protocol_configuration: typing.Optional[ProtocolType] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__188ac6000401e2d39206f8bbeab856bca92c12af2135f85632e30611238f3ea6(
    strategy_type: MemoryStrategyType,
    *,
    invocation_configuration: typing.Union[InvocationConfiguration, typing.Dict[builtins.str, typing.Any]],
    historical_context_window_size: typing.Optional[jsii.Number] = None,
    trigger_conditions: typing.Optional[typing.Union[TriggerConditions, typing.Dict[builtins.str, typing.Any]]] = None,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f97328d30e65eff0ed4b3734cf9226ca12826a94fecee765dbba85c70b4b3635(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbcf3bdd0c9f8eaadddbc029d9f0a9dece8550883bffe0164f389e25d3629630(
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    invocation_configuration: typing.Union[InvocationConfiguration, typing.Dict[builtins.str, typing.Any]],
    historical_context_window_size: typing.Optional[jsii.Number] = None,
    trigger_conditions: typing.Optional[typing.Union[TriggerConditions, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__effa7c1822f5dd9bca17e2aca728718fe021317ef7ef3e7d41d4ea4fa5f2112a(
    *,
    message_based_trigger: typing.Optional[jsii.Number] = None,
    time_based_trigger: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    token_based_trigger: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2116ad0a264d69770800f27d273a661a955fcb5c6c066f36456e9178f63d742d(
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c77d9cceeabf2dd05d534145778ab3e1e597cf25fdabc7bdbdbc642c412f2435(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6facf14dce62b7f6f12e4abaf4eb022dff3a45f4068e5f45350aab6e10355a0(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d32eecca999e221fe7baaea3ba395ddee5578ec83675efa9efdbea664213da2(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9186b5df0e333eb3469e897ab73dc50dee27c22f707afd8f3645295ca9d00d55(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8d3ed248b0e1fbb8321d56521a7d7da90f0d2609d7149da6e1d786cbb7e8af8(
    metric_name: builtins.str,
    dimensions: typing.Mapping[builtins.str, builtins.str],
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78f3dfb28f4dc0851b8a333b577550c3ed04b83619039f5923124cdcbed267cd(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44ddd5de65d8344be82e751ad250cc43e9faa11ea964e6b229c0a4d1ec72d5f7(
    metric_name: builtins.str,
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad4dce28a348ae0a4ea1f8be12576c56d15cb4cfabe63fa3ad38edc91bd2674d(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__def70821036fc28a14280760ae0b74a0fece9251b8de279a7787b620952b96f2(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35a69ebb2bb4842640813061b2ac17af0959c464410a959b014b4c88834032a5(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__945c10dd6a920f679edb8ab070a635638c847e8d49d196a218ff5b77cdf8d742(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a2ee85b94b08620ec9b5951320326c2a5e06e58d8c74143b59faaa569c5db5a(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a61932e41a10c1b55eb12421708f57f6f8fa7f51c4a52602ae921332f603e4bc(
    mode: builtins.str,
    scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffadf1618c1ccf9e7f800598ace60f876ef2c866dfa2193de733904aef830531(
    scope: _constructs_77d1e7e8.Construct,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3ba04960e2402fcf93e24376e08d3027678d856540da250157c6e19f1dc1862(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1788c6502070824895d3503d450005bb1c205c4d74bb8738add0bf26f3de4904(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    *actions: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2db493ce830ccc0f4897a55b53f8cb527c29ca1faf55e5ef17c8df1975c84db(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49cb39b73910ca0e9b10fd69d88ba3c962540e3ffe52e4af83aa081763523e1e(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4d919318556058b051ce30963bb88b3ea857942f805b6da65b497596bc8e39b(
    grantee: _aws_cdk_aws_iam_ceddda9d.IGrantable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e89914064bfd399d5233c80170ff40fe971de7b840aeca4ac822fd1fcaf4c53(
    metric_name: builtins.str,
    dimensions: typing.Mapping[builtins.str, builtins.str],
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a96b5df243162f6e4ccc604d71ceff9d4907e1fb21c4bdc077b17e437bad6d1e(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__601c512b2394720d7f44430e54e52ac9b991b7aa673c58633b67406ae999ec8a(
    metric_name: builtins.str,
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da0ad6292c612c8f34d7b641b68c10de89777fe2d41763b66d9ea6f7c878c4a6(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72deaefdc0ab67927aa48a7e5dbfb70a9004b85dab32f68b95be249b26066bd0(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65d0b839015fe6a1c368d562bdee51b93c69cb5b759c1f1173dc2758a1413968(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a56c641c8e2af33eb396292b7658955fbae3d77a1c0a87985f4020dfe2e45f2(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9be097202746caca62d9d0d7831461e673cceaf8e528a88286bd03a9c0c5b694(
    operation: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    color: typing.Optional[builtins.str] = None,
    dimensions_map: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    label: typing.Optional[builtins.str] = None,
    period: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    region: typing.Optional[builtins.str] = None,
    stack_account: typing.Optional[builtins.str] = None,
    stack_region: typing.Optional[builtins.str] = None,
    statistic: typing.Optional[builtins.str] = None,
    unit: typing.Optional[_aws_cdk_aws_cloudwatch_ceddda9d.Unit] = None,
    visible: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5abf274e5386aff6188eb410a31a1f9a74e1ef0c691c2c7886dd26347a9bbcc6(
    mode: builtins.str,
    scope: typing.Optional[_constructs_77d1e7e8.Construct] = None,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38e59bc603de9e405a37067fca444858724ba4a5692828408586100c7172d14d(
    scope: _constructs_77d1e7e8.Construct,
    *,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    allow_all_outbound: typing.Optional[builtins.bool] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    vpc_subnets: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb47cf6cb64f16941e24867573f447a6c7700a0e548c605ab3a6c79766903dd3(
    *,
    name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    namespaces: typing.Sequence[builtins.str],
    custom_consolidation: typing.Optional[typing.Union[OverrideConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    custom_extraction: typing.Optional[typing.Union[OverrideConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e76fa6dc189b8b63815ed558f95c760b00a4f52735d77ee7738d05646cb0f60(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    memory_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    expiration_duration: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
    kms_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    memory_strategies: typing.Optional[typing.Sequence[IMemoryStrategy]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d1ef3ab147d318f2cfae70c86258d2aaae60999cbf091f81112ab74f9a797f8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    memory_arn: builtins.str,
    role_arn: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    kms_key_arn: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    updated_at: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d88d525f5db5bcf500ab4eef917307847de4249de07b49c2ddf92dd64065092b(
    memory_strategy: IMemoryStrategy,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d3c75c162a496b2457c5b16d4ab318237dd0f6028aaaa787f5968728ad5bea40(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    agent_runtime_artifact: AgentRuntimeArtifact,
    runtime_name: builtins.str,
    authorizer_configuration: typing.Optional[RuntimeAuthorizerConfiguration] = None,
    description: typing.Optional[builtins.str] = None,
    environment_variables: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_configuration: typing.Optional[RuntimeNetworkConfiguration] = None,
    protocol_configuration: typing.Optional[ProtocolType] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05959bcf4b4bc641f8cd5e6663c98667c22ec794751ac633e033ccabebf69312(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    agent_runtime_arn: builtins.str,
    agent_runtime_id: builtins.str,
    agent_runtime_name: builtins.str,
    role_arn: builtins.str,
    agent_runtime_version: typing.Optional[builtins.str] = None,
    agent_status: typing.Optional[builtins.str] = None,
    created_at: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    last_updated_at: typing.Optional[builtins.str] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c9f210c62e6b8a9cc9f91d2223cadcf66989308f610a152e24937c2e6f75fea(
    endpoint_name: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c08f9203e17afcdac6a5a193e263989301ad529a8b9defc871c88e757bc1f18a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    agent_runtime_id: builtins.str,
    endpoint_name: builtins.str,
    agent_runtime_version: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7aac4684398202199ff45b016211ef025a54472a69d037cfafe89eaa76bac9ac(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    agent_runtime_arn: builtins.str,
    agent_runtime_endpoint_arn: builtins.str,
    endpoint_name: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    endpoint_id: typing.Optional[builtins.str] = None,
    last_updated_at: typing.Optional[builtins.str] = None,
    live_version: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    target_version: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1158b103a85cbce3d28e980992f8b82595d918f92538cc576de16ed55fbc4071(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    browser_custom_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_configuration: typing.Optional[BrowserNetworkConfiguration] = None,
    recording_config: typing.Optional[typing.Union[RecordingConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e143bea37e02f65f29c3f3dfd523e8452322bb7ee9d57f98ab6bd947e40e261(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    browser_arn: builtins.str,
    role_arn: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    last_updated_at: typing.Optional[builtins.str] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    status: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97059670dcd4750424fbb12f68be0e5fc4005cf0b64c6621aff517561009ef5a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    code_interpreter_custom_name: builtins.str,
    description: typing.Optional[builtins.str] = None,
    execution_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
    network_configuration: typing.Optional[CodeInterpreterNetworkConfiguration] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da00b980caf9bfd0b84d4f7c4ec856774682fff062a743c88616a5a9368f2a09(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    code_interpreter_arn: builtins.str,
    role_arn: builtins.str,
    created_at: typing.Optional[builtins.str] = None,
    last_updated_at: typing.Optional[builtins.str] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    status: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

for cls in [IBedrockAgentRuntime, IBrowserCustom, ICodeInterpreterCustom, IMemory, IMemoryStrategy, IRuntimeEndpoint]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
