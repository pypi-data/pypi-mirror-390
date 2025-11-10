# Installation Guide for ModelHub SDK

ModelHub SDK is a comprehensive tool for orchestrating machine learning workflows, experiments, datasets, and deployments on Kubernetes. This guide walks you through setting up ModelHub SDK with its optional integrations for MLflow, Kubernetes model serving via KServe, and advanced pipeline management.

---

## Prerequisites

- **Python 3.9 or higher** is required.
- It is recommended to use a virtual environment. You may use either [Miniconda](https://docs.anaconda.com/miniconda/) or Python’s built-in `venv`.
- (Optional) A configured Kubernetes cluster and proper credentials if you plan to deploy models with KServe.

---

## Setting Up Your Environment

### Using Conda

```
conda create -n modelhub python=3.9
conda activate modelhub
```

### Using Virtualenv

```
python -m venv modelhub-env
source modelhub-env/bin/activate  # On Windows: modelhub-env\Scripts\activate
```

### Basic Installation

To install the core ModelHub SDK functionality, run:

```
pip install autonomize-model-sdk
```
This command installs the essential components for experiment logging, dataset management, and pipeline orchestration.

### Optional Dependencies

Enhance your ModelHub SDK experience by installing optional integrations:

### MLflow Integration

For full experiment tracking and run management support with MLflow, install:

```
pip install "autonomize-model-sdk[mlflow]"
```

### Pipeline Management and Dataset Extensions

For advanced pipeline orchestration and additional dataset utilities, install:

```
pip install "autonomize-model-sdk[pipeline]"
```

Note: Adjust the extra names (e.g., [mlflow], [kserve], [pipeline]) as needed if your package defines different names for its optional dependencies.

### Environment Configuration

Before using ModelHub SDK, ensure that you set the necessary environment variables. For example:

```
export MODELHUB_BASE_URL=https://api-modelhub.example.com
export MODELHUB_CLIENT_ID=your_client_id
export MODELHUB_CLIENT_SECRET=your_client_secret
export MLFLOW_EXPERIMENT_ID=your_experiment_id
```

Alternatively, you can create a .env file in your project root with the above variables.

### Verification

To verify your installation, run a simple test script:

```
from modelhub.clients import MLflowClient

client = MLflowClient(base_url="https://api-modelhub.example.com")
print("ModelHub SDK is installed and the client is initialized!")
```

### Troubleshooting

- Installation Issues:
Ensure you’re using Python 3.9+ and that your virtual environment is activated. Also, upgrade pip with:

```
pip install --upgrade pip
```

- Dependency Conflicts:
A fresh virtual environment can help avoid version conflicts.

For further assistance, refer to the ModelHub SDK documentation or open an issue on our GitHub repository.
