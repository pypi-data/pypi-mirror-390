"""Tests for KServe V2 protocol implementation."""

import numpy as np

from modelhub.serving.protocol import (
    DataType,
    InferInputTensor,
    InferOutputTensor,
    InferRequest,
    InferResponse,
    deserialize_request,
    numpy_to_infer_tensor,
    serialize_request,
    serialize_response,
)


class TestProtocolTypes:
    """Test protocol data types and structures."""

    def test_infer_input_tensor(self):
        """Test InferInputTensor creation."""
        tensor = InferInputTensor(
            name="input",
            shape=[2, 3],
            datatype=DataType.FP32,
            data=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        )

        assert tensor.name == "input"
        assert tensor.shape == [2, 3]
        assert tensor.datatype == DataType.FP32
        assert len(tensor.data) == 6

    def test_infer_request(self):
        """Test InferRequest creation."""
        tensor = InferInputTensor(
            name="input",
            shape=[1, 5],
            datatype=DataType.FP32,
            data=[1.0, 2.0, 3.0, 4.0, 5.0],
        )

        request = InferRequest(
            model_name="test-model", model_version="1", id="test-123", inputs=[tensor]
        )

        assert request.model_name == "test-model"
        assert request.model_version == "1"
        assert request.id == "test-123"
        assert len(request.inputs) == 1

    def test_serialize_request(self):
        """Test request serialization."""
        tensor = InferInputTensor(
            name="input", shape=[2, 2], datatype=DataType.INT32, data=[1, 2, 3, 4]
        )

        request = InferRequest(model_name="test-model", inputs=[tensor])

        serialized = serialize_request(request)

        assert serialized["model_name"] == "test-model"
        assert len(serialized["inputs"]) == 1
        assert serialized["inputs"][0]["name"] == "input"
        assert serialized["inputs"][0]["shape"] == [2, 2]
        assert serialized["inputs"][0]["datatype"] == DataType.INT32

    def test_deserialize_request(self):
        """Test request deserialization."""
        data = {
            "model_name": "test-model",
            "model_version": "2",
            "inputs": [
                {
                    "name": "input",
                    "shape": [3],
                    "datatype": "FP64",
                    "data": [1.1, 2.2, 3.3],
                }
            ],
        }

        request = deserialize_request(data)

        assert request.model_name == "test-model"
        assert request.model_version == "2"
        assert len(request.inputs) == 1
        assert request.inputs[0].name == "input"
        assert request.inputs[0].shape == [3]
        assert request.inputs[0].datatype == "FP64"
        assert request.inputs[0].data == [1.1, 2.2, 3.3]

    def test_serialize_response(self):
        """Test response serialization."""
        output = InferOutputTensor(
            name="output", shape=[2, 1], datatype=DataType.FP32, data=[0.8, 0.2]
        )

        response = InferResponse(
            model_name="test-model", model_version="1", outputs=[output]
        )

        serialized = serialize_response(response)

        assert serialized["model_name"] == "test-model"
        assert serialized["model_version"] == "1"
        assert len(serialized["outputs"]) == 1
        assert serialized["outputs"][0]["name"] == "output"

    def test_numpy_to_infer_tensor(self):
        """Test numpy array conversion."""
        # Test float32 array
        arr = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        tensor = numpy_to_infer_tensor("test", arr)

        assert tensor.name == "test"
        assert tensor.shape == [2, 2]
        assert tensor.datatype == DataType.FP32
        assert tensor.data == [1.0, 2.0, 3.0, 4.0]

        # Test int64 array
        arr = np.array([1, 2, 3], dtype=np.int64)
        tensor = numpy_to_infer_tensor("test", arr)

        assert tensor.datatype == DataType.INT64
        assert tensor.shape == [3]
        assert tensor.data == [1, 2, 3]

    def test_bytes_tensor(self):
        """Test bytes data handling."""
        # Create tensor with bytes data
        tensor = InferInputTensor(
            name="image", shape=[1], datatype=DataType.BYTES, data=[b"fake-image-data"]
        )

        assert tensor.datatype == DataType.BYTES
        assert tensor.data[0] == b"fake-image-data"

    def test_parameters(self):
        """Test parameter handling."""
        tensor = InferInputTensor(
            name="input",
            shape=[1, 10],
            datatype=DataType.FP32,
            data=[0.0] * 10,
            parameters={"temperature": 0.7, "max_tokens": 100},
        )

        assert tensor.parameters["temperature"] == 0.7
        assert tensor.parameters["max_tokens"] == 100

        request = InferRequest(
            model_name="test", inputs=[tensor], parameters={"timeout": 30}
        )

        assert request.parameters["timeout"] == 30
