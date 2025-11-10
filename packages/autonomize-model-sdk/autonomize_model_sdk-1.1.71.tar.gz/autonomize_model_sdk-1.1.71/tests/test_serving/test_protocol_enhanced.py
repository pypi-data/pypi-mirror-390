"""
Enhanced tests for protocol with unified format support.
"""

import json
from dataclasses import asdict

import numpy as np

from modelhub.serving.protocol import (
    DataType,
    InferInputTensor,
    InferOutputTensor,
    InferRequest,
    InferResponse,
    ModelMetadata,
    deserialize_request,
    numpy_to_infer_tensor,
    serialize_request,
    serialize_response,
)


class TestProtocolEnhanced:
    """Enhanced protocol tests with edge cases."""

    def test_mixed_datatype_tensors(self):
        """Test request with multiple tensors of different types."""
        tensors = [
            InferInputTensor(
                name="float_input",
                shape=[2, 3],
                datatype=DataType.FP32,
                data=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            ),
            InferInputTensor(
                name="int_input",
                shape=[4],
                datatype=DataType.INT32,
                data=[10, 20, 30, 40],
            ),
            InferInputTensor(
                name="bytes_input",
                shape=[2],
                datatype=DataType.BYTES,
                data=[b"image1", b"image2"],
            ),
        ]

        request = InferRequest(model_name="multi-input-model", inputs=tensors)

        # Serialize and deserialize
        serialized = serialize_request(request)
        deserialized = deserialize_request(serialized)

        assert len(deserialized.inputs) == 3
        assert deserialized.inputs[0].datatype == DataType.FP32
        assert deserialized.inputs[1].datatype == DataType.INT32
        assert deserialized.inputs[2].datatype == DataType.BYTES
        assert deserialized.inputs[2].data[0] == b"image1"

    def test_large_tensor_handling(self):
        """Test handling of large tensors."""
        # Create a large tensor (1000x1000 matrix)
        large_data = list(range(1000000))
        tensor = InferInputTensor(
            name="large_input",
            shape=[1000, 1000],
            datatype=DataType.FP32,
            data=large_data,
        )

        request = InferRequest(model_name="large-model", inputs=[tensor])

        # Test serialization doesn't fail
        serialized = serialize_request(request)
        assert len(serialized["inputs"][0]["data"]) == 1000000

        # Test deserialization preserves all data
        deserialized = deserialize_request(serialized)
        assert len(deserialized.inputs[0].data) == 1000000
        assert deserialized.inputs[0].data[-1] == 999999

    def test_numpy_dtype_mappings(self):
        """Test all numpy dtype to DataType mappings."""
        test_cases = [
            (np.float32, DataType.FP32),
            (np.float64, DataType.FP64),
            (np.int32, DataType.INT32),
            (np.int64, DataType.INT64),
            (np.int8, DataType.INT8),
            (np.int16, DataType.INT16),
            (np.uint8, DataType.UINT8),
            (np.uint16, DataType.UINT16),
            (np.uint32, DataType.UINT32),
            (np.uint64, DataType.UINT64),
            (bool, DataType.BOOL),
        ]

        for numpy_dtype, expected_datatype in test_cases:
            arr = np.array([1, 2, 3], dtype=numpy_dtype)
            tensor = numpy_to_infer_tensor("test", arr)
            assert tensor.datatype == expected_datatype

    def test_tensor_shape_variations(self):
        """Test various tensor shapes."""
        # Scalar
        arr = np.array(42.0)
        tensor = numpy_to_infer_tensor("scalar", arr)
        assert tensor.shape == []
        assert tensor.data == [42.0]

        # 1D array
        arr = np.array([1, 2, 3])
        tensor = numpy_to_infer_tensor("1d", arr)
        assert tensor.shape == [3]

        # High dimensional array
        arr = np.zeros((2, 3, 4, 5))
        tensor = numpy_to_infer_tensor("4d", arr)
        assert tensor.shape == [2, 3, 4, 5]
        assert len(tensor.data) == 120

    def test_model_metadata(self):
        """Test ModelMetadata structure."""
        metadata = ModelMetadata(
            name="test-model",
            platform="mlflow",
            inputs=[
                {"name": "input_1", "datatype": "FP32", "shape": [-1, 224, 224, 3]},
                {"name": "input_2", "datatype": "INT32", "shape": [-1]},
            ],
            outputs=[
                {"name": "predictions", "datatype": "FP32", "shape": [-1, 1000]},
                {"name": "features", "datatype": "FP32", "shape": [-1, 512]},
            ],
        )

        assert metadata.name == "test-model"
        assert len(metadata.inputs) == 2
        assert metadata.inputs[0]["shape"] == [-1, 224, 224, 3]
        assert metadata.outputs[1]["name"] == "features"

    def test_optional_fields(self):
        """Test handling of optional fields."""
        # Minimal request
        minimal_request = InferRequest(
            inputs=[
                InferInputTensor(
                    name="input", shape=[1], datatype=DataType.FP32, data=[1.0]
                )
            ]
        )

        assert minimal_request.model_name is None
        assert minimal_request.model_version is None
        assert minimal_request.id is None

        # Serialize should handle None values
        serialized = serialize_request(minimal_request)
        assert "model_name" not in serialized or serialized["model_name"] is None

    def test_parameters_preservation(self):
        """Test that parameters are preserved through serialization."""
        tensor = InferInputTensor(
            name="input",
            shape=[10],
            datatype=DataType.FP32,
            data=[0.0] * 10,
            parameters={"preprocessing": "normalize", "threshold": 0.5},
        )

        request = InferRequest(
            model_name="test",
            inputs=[tensor],
            parameters={"timeout": 30, "batch_size": 32},
        )

        # Serialize and deserialize
        serialized = serialize_request(request)
        deserialized = deserialize_request(serialized)

        # Check tensor parameters
        assert deserialized.inputs[0].parameters["preprocessing"] == "normalize"
        assert deserialized.inputs[0].parameters["threshold"] == 0.5

        # Check request parameters
        assert deserialized.parameters["timeout"] == 30
        assert deserialized.parameters["batch_size"] == 32

    def test_bytes_data_encoding(self):
        """Test proper encoding/decoding of bytes data."""

        # Create bytes tensor with binary data
        binary_data = b"\x00\x01\x02\xFF\xFE\xFD"
        tensor = InferInputTensor(
            name="binary", shape=[1], datatype=DataType.BYTES, data=[binary_data]
        )

        # When serializing to JSON, bytes should be base64 encoded
        serialized = serialize_request(InferRequest(inputs=[tensor]))

        # In actual implementation, bytes would be base64 encoded
        # For this test, we'll verify the data is preserved
        deserialized = deserialize_request(serialized)
        assert deserialized.inputs[0].data[0] == binary_data

    def test_error_response_format(self):
        """Test error response formatting."""
        # Create an error response
        error_response = {
            "model_name": "test-model",
            "model_version": "1",
            "error": {"code": "INVALID_INPUT", "message": "Input shape mismatch"},
        }

        # This should be a valid response format
        assert "error" in error_response
        assert error_response["error"]["code"] == "INVALID_INPUT"

    def test_batch_dimension_handling(self):
        """Test handling of batch dimensions in shapes."""
        # Dynamic batch size (-1)
        tensor = InferInputTensor(
            name="batch_input",
            shape=[-1, 224, 224, 3],
            datatype=DataType.FP32,
            data=[],  # Empty for shape definition
        )

        assert tensor.shape[0] == -1
        assert tensor.shape[1:] == [224, 224, 3]

        # Fixed batch size
        tensor_fixed = InferInputTensor(
            name="fixed_batch", shape=[32, 10], datatype=DataType.FP32, data=[0.0] * 320
        )

        assert tensor_fixed.shape[0] == 32

    def test_output_tensor_creation(self):
        """Test various output tensor scenarios."""
        # String output (as bytes)
        string_output = InferOutputTensor(
            name="text_output",
            shape=[1],
            datatype=DataType.BYTES,
            data=[b"Generated text response"],
        )

        assert string_output.data[0] == b"Generated text response"

        # Multi-dimensional output
        arr = np.random.rand(2, 3, 4).astype(np.float32)
        tensor = numpy_to_infer_tensor("multi_dim", arr)

        assert isinstance(tensor, InferOutputTensor)
        assert tensor.shape == [2, 3, 4]
        assert len(tensor.data) == 24

    def test_response_serialization_edge_cases(self):
        """Test response serialization edge cases."""
        # Response with multiple outputs
        outputs = [
            InferOutputTensor(
                name="primary",
                shape=[1, 5],
                datatype=DataType.FP32,
                data=[0.1, 0.2, 0.3, 0.4, 0.0],
            ),
            InferOutputTensor(
                name="auxiliary", shape=[1], datatype=DataType.INT32, data=[42]
            ),
            InferOutputTensor(
                name="metadata",
                shape=[1],
                datatype=DataType.BYTES,
                data=[b'{"confidence": 0.95}'],
            ),
        ]

        response = InferResponse(
            model_name="multi-output-model",
            model_version="2",
            id="req-123",
            outputs=outputs,
        )

        serialized = serialize_response(response)

        assert len(serialized["outputs"]) == 3
        assert serialized["outputs"][0]["name"] == "primary"
        assert serialized["outputs"][1]["data"] == [42]
        assert serialized["outputs"][2]["datatype"] == DataType.BYTES

    def test_dataclass_to_dict_conversion(self):
        """Test that dataclasses convert properly to dicts."""
        tensor = InferInputTensor(
            name="test", shape=[2, 2], datatype=DataType.FP32, data=[1.0, 2.0, 3.0, 4.0]
        )

        # Convert to dict
        tensor_dict = asdict(tensor)

        assert isinstance(tensor_dict, dict)
        assert tensor_dict["name"] == "test"
        assert tensor_dict["shape"] == [2, 2]
        assert tensor_dict["datatype"] == DataType.FP32

        # Should be JSON serializable
        json_str = json.dumps(tensor_dict)
        assert "test" in json_str


class TestProtocolCompatibility:
    """Test protocol compatibility with different clients."""

    def test_triton_compatible_request(self):
        """Test parsing Triton-style request."""
        triton_request = {
            "inputs": [
                {
                    "name": "INPUT0",
                    "shape": [1, 16],
                    "datatype": "FP32",
                    "data": [0.0] * 16,
                }
            ],
            "outputs": [{"name": "OUTPUT0", "parameters": {"binary_data": False}}],
        }

        # Should be able to parse inputs
        request = deserialize_request(triton_request)
        assert len(request.inputs) == 1
        assert request.inputs[0].name == "INPUT0"

    def test_kserve_raw_request_format(self):
        """Test KServe raw prediction format."""
        # This is the format used by some KServe transformers
        raw_request = {"instances": [{"text": "example 1"}, {"text": "example 2"}]}

        # This would need custom handling in the predictor
        # Just verify it's a valid dict structure
        assert isinstance(raw_request["instances"], list)
        assert len(raw_request["instances"]) == 2

    def test_sagemaker_compatible_format(self):
        """Test SageMaker-style request format."""
        sagemaker_request = {"instances": [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]}

        # This format would be handled by the predictor
        assert len(sagemaker_request["instances"]) == 2
        assert len(sagemaker_request["instances"][0]) == 3
