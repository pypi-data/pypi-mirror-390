# ModelHub Pipeline Configuration Guide

This guide covers all scenarios for configuring pipelines in ModelHub, including resource management, node selection, artifact storage, and more.

## Table of Contents
1. [Basic Pipeline Structure](#basic-pipeline-structure)
2. [Resource Configuration](#resource-configuration)
3. [Node Scheduling](#node-scheduling)
4. [Blob Storage Integration](#blob-storage-integration)
5. [Stage Dependencies](#stage-dependencies)
6. [Environment Configuration](#environment-configuration)
7. [Advanced Scenarios](#advanced-scenarios)
8. [Workflow Artifacts](#workflow-artifacts)
9. [Pipeline Validation](#pipeline-validation)
10. [Authentication](#authentication)

## Basic Pipeline Structure

A pipeline is defined in YAML format with the following basic structure:

```yaml
name: "My Pipeline"
description: "Pipeline description"
experiment_id: "123"
image_tag: "my-image:1.0.0"
stages:
  - name: stage-1
    type: custom
    script: scripts/stage1.py
```

## Resource Configuration

### CPU and Memory Requests/Limits

Configure resource requests and limits for each stage:

```yaml
stages:
  - name: train
    type: custom
    script: scripts/train.py
    resources:
      requests:
        cpu: "1"
        memory: "2Gi"
      limits:
        cpu: "2"
        memory: "4Gi"
```

### GPU Resources

For GPU-enabled workloads:

```yaml
stages:
  - name: train
    type: custom
    script: scripts/train.py
    resources:
      requests:
        cpu: "2"
        memory: "8Gi"
        nvidia.com/gpu: "1"
      limits:
        cpu: "4"
        memory: "16Gi"
        nvidia.com/gpu: "1"
```

## Node Scheduling

### Node Selectors

Schedule pods on specific nodes using labels:

```yaml
stages:
  - name: gpu-train
    type: custom
    script: scripts/train.py
    node_selector:
      gpu: "true"
      instance-type: "gpu-optimized"
```

### Tolerations

Configure tolerations to schedule on tainted nodes:

```yaml
stages:
  - name: gpu-train
    type: custom
    script: scripts/train.py
    tolerations:
      - key: "gpu"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
```

Example for multiple tolerations:

```yaml
stages:
  - name: specialized-train
    type: custom
    script: scripts/train.py
    tolerations:
      - key: "gpu"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      - key: "instance-type"
        operator: "Equal"
        value: "gpu-optimized"
        effect: "NoSchedule"
```

## Blob Storage Integration

### Basic Blob Storage Mount

Mount blob storage as a volume in your pipeline stage:

```yaml
stages:
  - name: data-processing
    type: custom
    script: scripts/process.py
    blob_storage_config:
      container: "dataset-container"
      blob_url: "https://storage.blob.core.windows.net"
      mount_path: "/data"
```

### Multiple Storage Mounts

Example using multiple blob storage mounts:

```yaml
stages:
  - name: data-processing
    type: custom
    script: scripts/process.py
    blob_storage_config:
      - container: "raw-data"
        blob_url: "https://storage.blob.core.windows.net"
        mount_path: "/data/raw"
      - container: "processed-data"
        blob_url: "https://storage.blob.core.windows.net"
        mount_path: "/data/processed"
```

## Stage Dependencies

### Linear Dependencies

Configure stages to run sequentially:

```yaml
stages:
  - name: preprocess
    type: custom
    script: scripts/preprocess.py

  - name: train
    type: custom
    script: scripts/train.py
    depends_on: ["preprocess"]

  - name: evaluate
    type: custom
    script: scripts/evaluate.py
    depends_on: ["train"]
```

### Multiple Dependencies

Configure a stage that depends on multiple previous stages:

```yaml
stages:
  - name: data-prep-1
    type: custom
    script: scripts/prep1.py

  - name: data-prep-2
    type: custom
    script: scripts/prep2.py

  - name: train
    type: custom
    script: scripts/train.py
    depends_on: ["data-prep-1", "data-prep-2"]
```

## Environment Configuration

### Stage-specific Environment Variables

Set environment variables for specific stages:

```yaml
stages:
  - name: train
    type: custom
    script: scripts/train.py
    params:
      BATCH_SIZE: "32"
      LEARNING_RATE: "0.001"
      NUM_EPOCHS: "100"
```

### Shared Environment Variables

Environment variables shared across all stages are automatically provided:
- MODELHUB_BASE_URL
- MODELHUB_CLIENT_ID
- MODELHUB_CLIENT_SECRET
- MLFLOW_EXPERIMENT_ID

## Advanced Scenarios

### Combined Configuration Example

Here's an example combining multiple configuration options:

```yaml
name: "Advanced ML Pipeline"
description: "Complete pipeline with all configurations"
experiment_id: "123"
image_tag: "ml-pipeline:1.0.0"

stages:
  - name: data-prep
    type: custom
    script: scripts/prep.py
    resources:
      requests:
        cpu: "2"
        memory: "4Gi"
    blob_storage_config:
      container: "raw-data"
      blob_url: "https://storage.blob.core.windows.net"
      mount_path: "/data"

  - name: train
    type: custom
    script: scripts/train.py
    depends_on: ["data-prep"]
    resources:
      requests:
        cpu: "4"
        memory: "16Gi"
        nvidia.com/gpu: "1"
      limits:
        cpu: "8"
        memory: "32Gi"
        nvidia.com/gpu: "1"
    node_selector:
      gpu: "true"
    tolerations:
      - key: "gpu"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
    params:
      MODEL_TYPE: "transformer"
      BATCH_SIZE: "64"

  - name: evaluate
    type: custom
    script: scripts/evaluate.py
    depends_on: ["train"]
    resources:
      requests:
        cpu: "2"
        memory: "4Gi"
    blob_storage_config:
      container: "model-artifacts"
      blob_url: "https://storage.blob.core.windows.net"
      mount_path: "/artifacts"
```

## Workflow Artifacts

### Passing Data Between Stages

You can pass data between pipeline stages using Argo Workflow artifacts:

```yaml
stages:
  - name: preprocess
    type: custom
    script: scripts/preprocess.py
    artifacts:
      outputs:
        - name: processed-data
          path: /app/data/processed
          archive:
            none: {}  # No compression

  - name: train
    type: custom
    script: scripts/train.py
    depends_on: ["preprocess"]
    artifacts:
      inputs:
        - name: processed-data
          path: /app/data/input
      outputs:
        - name: model-artifacts
          path: /app/model
```

### Understanding Artifact Paths

When working with artifacts, it's important to understand how paths work:

1. **Output Paths**: In the producer stage, the `path` specifies the directory or file that will be captured as an artifact. Any files written to this location will be saved as part of the artifact.

2. **Input Paths**: In the consumer stage, the `path` specifies where the artifact will be mounted and made available to the stage.

Example:

```yaml
# Stage 1: Writing output
- name: data-generator
  artifacts:
    outputs:
      - name: training-data
        path: /outputs/training-data  # Your script should write files here

# Stage 2: Reading input
- name: model-training
  depends_on: ["data-generator"]
  artifacts:
    inputs:
      - name: training-data
        path: /inputs/data  # Your script will find the files here
```

In this example:
- The `data-generator` stage writes files to `/outputs/training-data/`
- The system captures everything in that directory as the `training-data` artifact
- In the `model-training` stage, the same files will be available at `/inputs/data/`

### Common Path Patterns

1. **Directory-to-Directory**: Most common approach where entire directories are passed between stages.
   ```yaml
   # Producer stage
   outputs:
     - name: dataset
       path: /app/outputs/dataset  # Directory containing multiple files

   # Consumer stage
   inputs:
     - name: dataset
       path: /app/inputs/dataset  # Same files now available here
   ```

2. **Single File**: For passing individual files.
   ```yaml
   # Producer stage
   outputs:
     - name: model-weights
       path: /app/outputs/model.h5  # Single file

   # Consumer stage
   inputs:
     - name: model-weights
       path: /app/inputs/pretrained.h5  # Same file with different name
   ```

### Best Practices for Artifact Paths

1. **Use Absolute Paths**: Always use absolute paths for clarity.
2. **Consistent Path Structure**: Maintain a consistent path structure across stages (e.g., `/app/inputs/`, `/app/outputs/`).
3. **Descriptive Names**: Use descriptive artifact names that clearly indicate the contents.
4. **Path Organization**: Keep input and output paths organized to avoid confusion:
   ```yaml
   # Good organization
   outputs:
     - name: processed-images
       path: /app/outputs/images
     - name: metadata
       path: /app/outputs/metadata
   ```
5. **Validate File Existence**: Have your scripts validate that expected files exist at the input paths.

## Pipeline Validation

### Validating Pipeline Configuration

Before running your pipeline, you can validate the YAML configuration to catch common issues:

```bash
pipeline validate -f pipeline.yaml
```

This checks for:
- Proper YAML syntax
- Required fields
- Artifact dependency consistency
- Resource specification correctness

### Automatic Fixing of Dependency Issues

The validation tool can automatically fix certain issues, particularly missing dependencies between stages that share artifacts:

```bash
pipeline validate -f pipeline.yaml --fix
```

Example scenario:
1. Stage B needs an artifact produced by Stage A
2. You've defined the artifact connection but forgot to add Stage A to Stage B's `depends_on` list
3. The `--fix` option will automatically add this dependency

To save the fixed configuration to a new file:

```bash
pipeline validate -f pipeline.yaml --fix --output fixed-pipeline.yaml
```

### Understanding Validation Results

The validation output includes:

1. **Success confirmation** if everything is valid:
   ```
   ✅ Pipeline configuration is valid.
   ```

2. **Warnings** for potential issues that don't prevent execution:
   ```
   Warnings:
     1. Stage 'evaluate' uses large memory request (16Gi) which may cause scheduling delays.
   ```

3. **Errors** for critical issues that must be fixed:
   ```
   Errors:
     1. Stage 'train' requires artifact 'preprocessed-data' but no stage produces it.
     2. Stage 'evaluate' requires artifact 'model' but doesn't depend on the stage that produces it.
   ```

### Common Validation Errors and Solutions

1. **Missing Artifact Producer**
   ```
   Error: Stage 'train' requires artifact 'preprocessed-data' but no stage produces it.
   ```
   Solution: Ensure a previous stage has an output artifact with the same name.

2. **Missing Stage Dependency**
   ```
   Error: Stage 'evaluate' requires artifact 'model' but doesn't depend on the stage that produces it.
   ```
   Solution: Add the producer stage to the `depends_on` list (or use `--fix`).

3. **Invalid Resource Specification**
   ```
   Error: Invalid resource request format for CPU: "2cores" (should be "2").
   ```
   Solution: Follow Kubernetes resource specification format.

4. **Conflicting Stage Names**
   ```
   Error: Duplicate stage name 'train' found.
   ```
   Solution: Ensure all stage names are unique.

### Advanced Validation Options

Use JSON output format for programmatic processing:

```bash
pipeline validate -f pipeline.yaml --format json
```

Include pyproject.toml for local validation:

```bash
pipeline validate -f pipeline.yaml --pyproject pyproject.toml
```

### Validating Before Starting a Pipeline

You can validate a pipeline configuration as part of the start command:

```bash
pipeline start -f pipeline.yaml --validate
```

This will run validation checks before attempting to start the pipeline, preventing issues during execution.

## Authentication

### Using ModelhubCredential

The Pipeline Manager uses the new `ModelhubCredential` class for authentication. This is a more secure and flexible approach that centralizes credential management.

```python
from modelhub.core import ModelhubCredential
from modelhub.clients import PipelineManager

# Initialize the credential
credential = ModelhubCredential(
    modelhub_url="https://api-modelhub.example.com",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize the pipeline manager with the credential
pipeline_manager = PipelineManager(
    credential=credential,
    client_id="your_client_id",
)

# Start the pipeline
pipeline = pipeline_manager.start_pipeline("pipeline.yaml")
```

### Running with CLI

Local development mode:
```bash
pipeline start -f pipeline.yaml --mode local --pyproject pyproject.toml
```

CI/CD mode:
```bash
pipeline start -f pipeline.yaml --mode cicd
```

The CLI automatically uses environment variables for authentication:
- `MODELHUB_BASE_URL`
- `MODELHUB_CLIENT_ID`
- `MODELHUB_CLIENT_SECRET`
- `CLIENT_ID`

### Best Practices

1. Resource Requests/Limits
   - Always specify both requests and limits
   - Set realistic memory limits to avoid OOM kills
   - Request GPUs only when needed

2. Storage
   - Use appropriate mount paths
   - Ensure storage permissions are correctly configured
   - Consider read/write access requirements

3. Dependencies
   - Keep the dependency chain clear and minimal
   - Ensure proper error handling between stages
   - Use meaningful stage names

4. Environment
   - Use descriptive parameter names
   - Document required environment variables
   - Consider security implications of environment variables

5. Authentication
   - Use the ModelhubCredential class for consistent authentication
   - Keep credentials secure with environment variables or secure storage
   - Set proper timeouts and SSL verification settings

## Common Issues and Solutions

1. Pod Scheduling Issues
   ```yaml
   # Solution: Add appropriate tolerations
   tolerations:
     - key: "gpu"
       operator: "Equal"
       value: "true"
       effect: "NoSchedule"
   ```

2. Resource Constraints
   ```yaml
   # Solution: Adjust resource requests/limits
   resources:
     requests:
       cpu: "2"
       memory: "4Gi"
     limits:
       cpu: "4"
       memory: "8Gi"
   ```

3. Storage Access
   ```yaml
   # Solution: Verify blob storage configuration
   blob_storage_config:
     container: "data"
     blob_url: "https://storage.blob.core.windows.net"
     mount_path: "/data"
   ```

4. Authentication Failures
   ```python
   # Solution: Check SSL configuration
   pipeline_manager = PipelineManager(
       credential=credential,
       verify_ssl=False  # For development environments only
   )
   ```

5. Token Expiration
   ```python
   # Solution: The credential will automatically handle token refreshing
   credential = ModelhubCredential(
       modelhub_url="https://api-modelhub.example.com",
       client_id="your_client_id",
       client_secret="your_client_secret"
   )
   ```
