# ModelHub Model Serving Guide

This guide covers all aspects of model serving with ModelHub SDK, including deployment through KServe, automatic model type detection, and streamlined deployment using a generic inference container.

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Base Model Service](#base-model-service)
   - [Supported Model Types](#supported-model-types)
   - [Input Formats](#input-formats)
4. [Specialized Model Services](#specialized-model-services)
   - [Text Models](#text-models)
   - [Image Models](#image-models)
   - [Tabular Models](#tabular-models)
5. [Custom Model Extensions](#custom-model-extensions)
6. [Deployment with KServe](#deployment-with-kserve)
7. [Working with Multiple Models](#working-with-multiple-models)
8. [Examples](#examples)
9. [Best Practices](#best-practices)

## Overview

ModelHub SDK provides a streamlined approach to model serving with automatic model type detection and KServe V2 protocol compliance. The new architecture offers:

- **Protocol Compliance**: Full KServe V2 protocol support without requiring KServe as a dependency
- **Automatic Model Detection**: Automatically detects and handles different model types (text, image, PDF, tabular)
- **Generic Container**: Single Docker image that can serve any MLflow model
- **Flexible Deployment**: Works standalone with FastAPI or as a KServe InferenceService
- **Multi-Model Support**: Serve multiple models in a single container
- **No Dependency Conflicts**: Eliminates httpx version conflicts with KServe

## Quick Start

### 1. Install ModelHub SDK

```bash
# Basic serving capabilities
pip install autonomize-model-sdk

# With serving extras (includes FastAPI, uvicorn)
pip install "autonomize-model-sdk[serving]"
```

### 2. Deploy Any Model with One Command

```bash
# Using model run ID
MODEL_URI="runs:/abc123/model" python -m modelhub.serving.server

# Using model registry
MODEL_NAME_REGISTRY="my-model" MODEL_VERSION="2" python -m modelhub.serving.server
```

### 3. Deploy with Docker

```bash
# Build generic inference container
docker build -t modelhub-inference examples/serving/

# Run with model URI
docker run -p 8080:8080 \
  -e MODEL_URI="runs:/abc123/model" \
  -e MODELHUB_BASE_URL="https://api.modelhub.com" \
  -e CLIENT_ID="your-client-id" \
  -e CLIENT_SECRET="your-secret" \
  modelhub-inference
```

## Architecture

### Protocol-Compliant Design

The new serving architecture implements KServe V2 protocol without requiring KServe as a dependency:

```python
from modelhub.serving import AutoModelPredictor, ModelServer

# Create a predictor that automatically detects model type
predictor = AutoModelPredictor(
    name="my-model",
    model_uri="runs:/abc123/model"  # or use model_name="registered-model"
)

# Create and start server
server = ModelServer(models=[predictor])
server.start()  # Serves on http://localhost:8080
```

### V2 Protocol Endpoints

- `GET /v2/health/live` - Liveness check
- `GET /v2/health/ready` - Readiness check
- `GET /v2/models` - List available models
- `GET /v2/models/{model}/ready` - Model-specific readiness
- `POST /v2/models/{model}/infer` - Inference endpoint

### Automatic Model Type Detection

The `AutoModelPredictor` automatically detects and handles different input types based on the request:

- **Text**: Detected by presence of `text` field
- **Images**: Detected by `image` or `images` field
- **PDF**: Detected by `pdf_file` or `byte_stream` field
- **Tabular**: Detected by `data` field with records
- **V2 Protocol**: Detected by presence of `inputs` array

No need to specify model type - it's automatically determined from the input!

## Input Formats

### V2 Protocol Format (Recommended)

For maximum compatibility with KServe and other inference servers:

```json
{
  "inputs": [{
    "name": "input",
    "shape": [1, 3],
    "datatype": "FP32",
    "data": [1.0, 2.0, 3.0]
  }]
}
```

### Binary File Upload (PDF, Images)

You can upload binary files directly using `Content-Type: application/octet-stream`:

```bash
# Upload a PDF file
curl -X POST http://localhost:8080/v2/models/my-model/infer \
  -H "Content-Type: application/octet-stream" \
  --data-binary @document.pdf

# Upload an image with type override
curl -X POST "http://localhost:8080/v2/models/my-model/infer?inference_type=image" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @image.jpg
```

The server automatically wraps binary uploads in the unified format with the `data` field.

### Legacy Format (Backward Compatible)

1. **Text Input**
   ```json
   {"text": "This is a sample text for classification"}
   ```

2. **Tabular Data**: JSON with a `"data"` field containing records
   ```json
   {"data": [{"feature1": 1.0, "feature2": 2.0}, {"feature1": 3.0, "feature2": 4.0}]}
   ```

3. **Image Input**: Binary image data or base64-encoded image
   ```json
   {"image": "<binary-data-or-base64>"}
   ```

4. **Multiple Images**: List of image data
   ```json
   {"images": ["<image1-data>", "<image2-data>"]}
   ```

5. **PDF Input**: Binary PDF data
   ```json
   {"pdf_file": "<binary-pdf-data>"}
   ```

## Generic Inference Container

### Single Container for All Models

The generic inference container can serve any MLflow model without code changes:

```dockerfile
# Use the pre-built container
FROM your-registry/modelhub-inference:latest

# Or build from examples
FROM python:3.12-slim
RUN pip install autonomize-model-sdk[serving]
COPY generic_serve.py /app/serve.py
CMD ["python", "/app/serve.py"]
```

### Environment Configuration

```bash
# Required
MODELHUB_BASE_URL=https://api.modelhub.com
CLIENT_ID=your-client-id
CLIENT_SECRET=your-secret

# Model specification (choose one)
MODEL_URI=runs:/abc123/model
# OR
MODEL_NAME_REGISTRY=my-model
MODEL_VERSION=2

# Optional
MODEL_NAME=custom-name  # defaults to "default-model"
LOG_LEVEL=INFO
PORT=8080
```

## Deployment Options

### Option 1: KServe InferenceService

Deploy to Kubernetes with KServe for production scale:

```python
from modelhub.serving import ModelhubModelService
from typing import Dict, Any, Optional

class CustomNLPModelService(ModelhubModelService):
    """Custom NLP model service with preprocessing and postprocessing."""

    def __init__(self, name: str, run_uri: str):
        super().__init__(name, run_uri, "pyfunc")
        self.labels = ["negative", "neutral", "positive"]

    def predict_text(self, request: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Override the text prediction method with custom logic."""
        text = request.get("text", "")

        # Custom preprocessing
        preprocessed_text = self._preprocess(text)

        # Prediction
        prediction = self.loaded_model.predict(preprocessed_text)

        # Custom postprocessing
        result = self._postprocess(prediction)

        return {
            "statusCode": 200,
            "data": result
        }

    def _preprocess(self, text: str) -> str:
        """Custom text preprocessing."""
        # Add your preprocessing steps here
        return text.lower().strip()

    def _postprocess(self, prediction) -> Dict[str, Any]:
        """Custom prediction postprocessing."""
        # Map numerical predictions to labels
        if isinstance(prediction, (int, float)):
            label_idx = min(int(prediction), len(self.labels) - 1)
            label = self.labels[label_idx]
        else:
            label = str(prediction)

        return {
            "prediction": label,
            "confidence": 0.95,  # Example
            "model_version": "v1.0"
        }
```

## Deployment with KServe

To deploy your model with KServe, create a container using your model's training image and add the serving code:

### 1. Create a serving script (app/main.py)

```python
from modelhub.serving import ModelhubModelService, ModelServer
import argparse

def main():
    parser = argparse.ArgumentParser(description="Model Service")
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--run", type=str, required=True)
    parser.add_argument("--model_type", type=str, default="pyfunc")
    args = parser.parse_args()

    model_service = ModelhubModelService(
        name=args.model_name,
        run_uri=args.run,
        model_type=args.model_type
    )
    model_service.load()
    ModelServer().start([model_service])

if __name__ == "__main__":
    main()
```

### 2. Create a Dockerfile

```dockerfile
# Use your existing pipeline image
FROM your-model-training-image:latest

# Install ModelHub SDK with appropriate extras
RUN pip install "autonomize-model-sdk[text-serving]"

# Set working directory
WORKDIR /app

# Copy serving code
COPY app /app

# Expose KServe port
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the server
ENTRYPOINT ["python", "app/main.py"]
```

### 3. Deploy with KServe

```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "text-classifier"
  namespace: "modelhub"
  labels:
    azure.workload.identity/use: "true"
spec:
  predictor:
    containers:
      - image: your-registry.io/text-classifier-serve:latest
        name: text-classifier
        resources:
          requests:
            cpu: 1
            memory: 2Gi
          limits:
            cpu: 2
            memory: 4Gi
        command: [
          "sh", "-c",
          "python app/main.py --model_name text-classifier --run runs:/abc123def456/model --model_type pyfunc"
        ]
        env:
          - name: MODELHUB_BASE_URL
            value: "https://api-modelhub.example.com"
          - name: MODELHUB_CLIENT_ID
            value: "client-id"
          - name: MODELHUB_CLIENT_SECRET
            value: "client-secret"
    serviceAccountName: "modelhub-service-account"
```

## Working with Multiple Models

You can serve multiple models in a single service:

```python
from modelhub.serving import ModelhubModelService, ModelServiceGroup, ModelServer

# Create model services
extraction_model = ModelhubModelService(
    name="extraction-model",
    run_uri="runs:/abc123/model"
)

classification_model = ModelhubModelService(
    name="classification-model",
    run_uri="runs:/def456/model"
)

# Create a group for convenience
model_group = ModelServiceGroup(models=[extraction_model, classification_model])
model_group.load_models()

# Start the server with both models
ModelServer().start([extraction_model, classification_model])
```

## Examples

### Text Classification Model

```python
from modelhub.serving import ModelhubModelService, ModelServer
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("text.classifier")

class TextClassifier(ModelhubModelService):
    def __init__(self, name, run_uri):
        super().__init__(name, run_uri, "pyfunc")
        self.labels = ["spam", "ham"]

    def predict_text(self, request, headers=None):
        text = request.get("text")
        if not text:
            return {"statusCode": 400, "message": "Missing text input"}

        logger.info(f"Processing text: {text[:50]}...")

        # Make prediction
        prediction = self.loaded_model.predict(text)

        # Post-process result
        if isinstance(prediction, (int, float)):
            label = self.labels[min(int(prediction), len(self.labels) - 1)]
        else:
            label = str(prediction)

        return {
            "statusCode": 200,
            "data": {
                "label": label,
                "original_prediction": prediction
            }
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--run", type=str, required=True)
    args = parser.parse_args()

    model = TextClassifier(args.model_name, args.run)
    model.load()
    ModelServer().start([model])

if __name__ == "__main__":
    main()
```

### Document Processing Model

```python
from modelhub.serving import ImageModelService, ModelServer
import argparse
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("document.processor")

class DocumentProcessor(ImageModelService):
    def __init__(self, name, run_uri):
        super().__init__(name, run_uri)

    def predict(self, request, headers=None):
        if not self.ready:
            return {"statusCode": 503, "message": "Model not loaded"}

        try:
            # Process PDF if provided
            pdf_file = request.get("pdf_file")
            images = request.get("images", [])

            if pdf_file:
                logger.info("Processing PDF input")
                # Process PDF to images
                from pdf2image import convert_from_bytes
                pdf_images = convert_from_bytes(pdf_file)
                logger.info(f"Converted PDF to {len(pdf_images)} images")
                images.extend(pdf_images)

            if not images:
                return {"statusCode": 400, "message": "No images or PDF provided"}

            # Process images to binary format for model
            img_binary_list = self._process_images(images)

            # Create dataframe for prediction
            df = pd.DataFrame({"image": img_binary_list})

            # Get prediction from model
            prediction = self.loaded_model.predict(df)

            # Format the results
            return {
                "statusCode": 200,
                "data": self._format_results(prediction)
            }

        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            return {"statusCode": 500, "message": f"Prediction error: {str(e)}"}

    def _process_images(self, images):
        # Implementation of image processing
        # ...
        return processed_images

    def _format_results(self, prediction):
        # Implementation of result formatting
        # ...
        return formatted_results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--run", type=str, required=True)
    args = parser.parse_args()

    model = DocumentProcessor(args.model_name, args.run)
    model.load()
    ModelServer().start([model])

if __name__ == "__main__":
    main()
```

## Handling Async Operations in MLflow Serving

When serving models that use async operations (e.g., calling external APIs, LLM services), special care must be taken to avoid event loop conflicts in MLflow's multi-threaded serving environment.

### The Problem

MLflow serving uses a thread pool for handling concurrent requests. Direct use of `asyncio.run()` in model prediction methods can lead to "Event loop is closed" errors because:
- Each thread may try to create its own event loop
- Event loops aren't thread-safe by default
- Lifecycle conflicts occur when multiple threads handle requests

### The Solution: AsyncExecutor

For models that need async operations, use the `AsyncExecutor` utility pattern:

```python
import asyncio
import queue
import threading
from typing import Any, Callable, Coroutine, Optional, TypeVar

T = TypeVar("T")

class AsyncExecutor:
    """Thread-safe executor for running async functions in sync contexts."""

    @staticmethod
    def run_async(
        async_func: Callable[..., Coroutine[Any, Any, T]],
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> T:
        """Execute async function in isolated event loop."""
        result_queue = queue.Queue()
        exception_queue = queue.Queue()

        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(async_func(*args, **kwargs))
                result_queue.put(result)
            except Exception as e:
                exception_queue.put(e)
            finally:
                loop.close()

        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            raise TimeoutError(f"Async operation timed out after {timeout} seconds")

        if not exception_queue.empty():
            raise exception_queue.get()

        return result_queue.get()
```

### Example: Model with Async LLM Calls

```python
import mlflow.pyfunc
import pandas as pd
from your_async_service import AsyncLLMService
from your_utils import AsyncExecutor

class AsyncLLMModel(mlflow.pyfunc.PythonModel):
    def __init__(self):
        self.llm_service = None

    def load_context(self, context):
        self.llm_service = AsyncLLMService()

    def predict(self, context, model_input: pd.DataFrame) -> pd.DataFrame:
        results = []

        for _, row in model_input.iterrows():
            # Convert async call to sync using AsyncExecutor
            result = AsyncExecutor.run_async(
                self.llm_service.generate,
                prompt=row['prompt'],
                timeout=30.0
            )
            results.append(result)

        return pd.DataFrame({"predictions": results})
```

### Best Practices for Async Models

1. **Always use AsyncExecutor** for async operations in MLflow models
2. **Set appropriate timeouts** to prevent hanging requests
3. **Handle exceptions gracefully** with fallback behavior
4. **Avoid global event loops** - create isolated loops per operation
5. **Test thoroughly** in multi-threaded environments

## Best Practices

1. **Resource Allocation**
   - Set appropriate resource requests and limits based on your model size
   - Allocate more memory for transformer models and large image models
   - Request GPUs only when needed for performance-critical models

2. **Model Loading**
   - Load models before starting the server to fail fast if there are issues
   - Consider lazy loading for multiple model services to reduce startup time
   - Use environment variables for configuration

3. **Error Handling**
   - Add comprehensive error handling for different input types
   - Log errors with enough context for debugging
   - Return meaningful error messages to clients

4. **Performance Optimization**
   - Use batching for high-throughput scenarios
   - Consider model quantization for faster inference
   - Optimize image processing operations for vision models

5. **Security Considerations**
   - Use service accounts with minimal permissions
   - Never log sensitive data or PII
   - Consider running containers as non-root users

6. **Monitoring and Observability**
   - Add logging for important events and prediction requests
   - Instrument services with metrics for monitoring
   - Consider adding health checks for model status

7. **Testing**
   - Test model service with realistic inputs before deployment
   - Validate all supported input formats
   - Benchmark performance with expected load patterns
