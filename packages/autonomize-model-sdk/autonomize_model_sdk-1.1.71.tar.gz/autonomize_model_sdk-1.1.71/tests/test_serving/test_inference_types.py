"""
Tests for inference type detection and transformation.
"""

from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest

from modelhub.serving.inference_types import (
    InferenceDetector,
    InferenceType,
    InputTransformer,
    OutputTransformer,
    create_unified_request,
    parse_unified_request,
)


class TestInferenceType:
    """Test InferenceType enum."""

    def test_inference_type_values(self):
        """Test all inference type values are accessible."""
        assert InferenceType.AUTO == "auto"
        assert InferenceType.TEXT == "text"
        assert InferenceType.IMAGE == "image"
        assert InferenceType.IMAGE_BASE64 == "image_base64"
        assert InferenceType.PDF_BYTES == "pdf_bytes"
        assert InferenceType.BYTE_STREAM == "byte_stream"
        assert InferenceType.OCR_TEXT == "ocr_text"
        assert InferenceType.STRUCTURED == "structured"
        assert InferenceType.RAW == "raw"
        assert InferenceType.TABULAR == "tabular"


class TestInferenceDetector:
    """Test InferenceDetector class."""

    def test_detect_text_input(self):
        """Test detection of text input."""
        data = {"text": "Hello, world!"}
        assert InferenceDetector.detect_type(data) == InferenceType.TEXT

    def test_detect_byte_stream(self):
        """Test detection of byte stream input."""
        data = {"byte_stream": b"PDF content"}
        assert InferenceDetector.detect_type(data) == InferenceType.BYTE_STREAM

        # With page numbers
        data = {"byte_stream": b"PDF content", "page_numbers": [1, 2, 3]}
        assert InferenceDetector.detect_type(data) == InferenceType.BYTE_STREAM

    def test_detect_image_base64(self):
        """Test detection of base64 encoded images."""
        data = {"image_base64": ["base64string1", "base64string2"]}
        assert InferenceDetector.detect_type(data) == InferenceType.IMAGE_BASE64

        # Single image
        data = {"image_base64": "base64string"}
        assert InferenceDetector.detect_type(data) == InferenceType.IMAGE_BASE64

    def test_detect_image(self):
        """Test detection of image input."""
        data = {"image": b"image bytes"}
        assert InferenceDetector.detect_type(data) == InferenceType.IMAGE

        data = {"images": [b"image1", b"image2"]}
        assert InferenceDetector.detect_type(data) == InferenceType.IMAGE

    def test_detect_ocr_text(self):
        """Test detection of OCR text input."""
        data = {
            "ocr_text_list": ["text1", "text2", "text3"],
            "page_number_list": [1, 2, 3],
        }
        assert InferenceDetector.detect_type(data) == InferenceType.OCR_TEXT

    def test_detect_tabular(self):
        """Test detection of tabular data."""
        # List of dicts = tabular data
        data = {"data": [{"col1": 1, "col2": 2}, {"col1": 3, "col2": 4}]}
        assert InferenceDetector.detect_type(data) == InferenceType.TABULAR

        # Single dict = structured data, not tabular
        data = {"data": {"col1": 1, "col2": 2}}
        assert InferenceDetector.detect_type(data) == InferenceType.STRUCTURED

    def test_detect_structured(self):
        """Test detection of structured data."""
        # Accumulator pattern
        data = {
            "hcpcs_code": "J1234",
            "rate": 100.50,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }
        assert InferenceDetector.detect_type(data) == InferenceType.STRUCTURED

        # Claims pattern
        data = {
            "contract_id": "C123",
            "member_id": "M456",
            "claim_id": "CL789",
            "other_field": "value",
        }
        assert InferenceDetector.detect_type(data) == InferenceType.STRUCTURED

        # Medical records pattern
        data = {"patient_id": "P123", "provider_id": "PR456", "diagnosis_code": "E11.9"}
        assert InferenceDetector.detect_type(data) == InferenceType.STRUCTURED

    def test_detect_raw_fallback(self):
        """Test fallback to raw type."""
        data = {"unknown_field": "some value"}
        assert InferenceDetector.detect_type(data) == InferenceType.RAW

        data = {}
        assert InferenceDetector.detect_type(data) == InferenceType.RAW

    def test_detection_priority(self):
        """Test that detection follows priority order."""
        # byte_stream should take priority over text
        data = {"byte_stream": b"data", "text": "hello"}
        assert InferenceDetector.detect_type(data) == InferenceType.BYTE_STREAM

        # image_base64 should take priority over image
        data = {"image_base64": "base64", "image": b"bytes"}
        assert InferenceDetector.detect_type(data) == InferenceType.IMAGE_BASE64

    def test_binary_content_type_detection(self):
        """Test binary content type detection using magic bytes."""
        # PNG magic bytes detection
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        data = {"data": png_bytes}
        assert InferenceDetector.detect_type(data) == InferenceType.IMAGE_BASE64

        # JPEG magic bytes detection
        jpeg_bytes = b"\xff\xd8\xff" + b"fake jpeg data"
        data = {"data": jpeg_bytes}
        assert InferenceDetector.detect_type(data) == InferenceType.IMAGE_BASE64

        # PDF magic bytes detection
        pdf_bytes = b"%PDF-1.4" + b"fake pdf data"
        data = {"data": pdf_bytes}
        assert InferenceDetector.detect_type(data) == InferenceType.BYTE_STREAM

        # GIF magic bytes detection
        gif_bytes = b"GIF87a" + b"fake gif data"
        data = {"data": gif_bytes}
        assert InferenceDetector.detect_type(data) == InferenceType.IMAGE_BASE64

        # BMP magic bytes detection
        bmp_bytes = b"BM" + b"fake bmp data"
        data = {"data": bmp_bytes}
        assert InferenceDetector.detect_type(data) == InferenceType.IMAGE_BASE64

        # Unknown binary format should fall back to BYTE_STREAM
        unknown_bytes = b"unknown binary format data"
        data = {"data": unknown_bytes}
        assert InferenceDetector.detect_type(data) == InferenceType.BYTE_STREAM

        # Short binary data should fall back to BYTE_STREAM
        short_bytes = b"abc"
        data = {"data": short_bytes}
        assert InferenceDetector.detect_type(data) == InferenceType.BYTE_STREAM


class TestInputTransformer:
    """Test InputTransformer class."""

    def test_transform_text(self):
        """Test text input transformation."""
        data = {"text": "Hello, world!"}
        df, metadata = InputTransformer.transform(data, InferenceType.TEXT)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "text" in df.columns
        assert df.at[0, "text"] == "Hello, world!"
        assert metadata["inference_type"] == "text"

    def test_transform_byte_stream(self):
        """Test byte stream transformation."""
        data = {"byte_stream": b"PDF content"}
        df, metadata = InputTransformer.transform(data, InferenceType.BYTE_STREAM)

        assert isinstance(df, pd.DataFrame)
        assert "data" in df.columns
        assert df.at[0, "data"] == b"PDF content"

        # With page numbers
        data = {"byte_stream": b"PDF content", "page_numbers": [1, 2, 3]}
        df, metadata = InputTransformer.transform(data, InferenceType.BYTE_STREAM)

        assert "data" in df.columns
        assert "page_numbers" in df.columns
        assert df.at[0, "page_numbers"] == [1, 2, 3]

    def test_transform_image_base64(self):
        """Test base64 image transformation."""
        # List of images
        data = {"image_base64": ["img1", "img2", "img3"]}
        df, metadata = InputTransformer.transform(data, InferenceType.IMAGE_BASE64)

        assert len(df) == 3
        assert df.at[0, "data"] == "img1"
        assert df.at[2, "data"] == "img3"

        # Single image
        data = {"image_base64": "single_img"}
        df, metadata = InputTransformer.transform(data, InferenceType.IMAGE_BASE64)

        assert len(df) == 1
        assert df.at[0, "data"] == "single_img"

    @patch("modelhub.serving.inference_types.PDF_SUPPORT", True)
    @patch("PIL.Image")
    def test_transform_binary_image_data(self, mock_image_class):
        """Test transformation of binary image data detected as IMAGE_BASE64."""
        # Mock binary image data (PNG magic bytes)
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        data = {"data": png_bytes}

        # Mock PIL Image processing
        mock_img = Mock()
        mock_image_class.open.return_value = mock_img

        with patch.object(InputTransformer, "pil_image_to_base64_str") as mock_base64:
            mock_base64.return_value = "converted_base64_image"

            df, metadata = InputTransformer.transform(data, InferenceType.IMAGE_BASE64)

            assert len(df) == 1
            assert df.at[0, "data"] == "converted_base64_image"
            assert metadata["num_images"] == 1
            assert metadata["images_processed"] == True

            # Verify PIL Image was called with BytesIO
            mock_image_class.open.assert_called_once()
            mock_base64.assert_called_once_with(mock_img)

    @patch("modelhub.serving.inference_types.PDF_SUPPORT", True)
    @patch("PIL.Image")
    def test_transform_binary_image_data_error_handling(self, mock_image_class):
        """Test error handling when binary image processing fails."""
        # Mock binary image data
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        data = {"data": png_bytes}

        # Mock PIL Image to raise exception
        mock_image_class.open.side_effect = Exception("Image processing failed")

        with patch("modelhub.serving.inference_types.logger") as mock_logger:
            df, metadata = InputTransformer.transform(data, InferenceType.IMAGE_BASE64)

            # Should fall back to raw data
            assert len(df) == 1
            assert df.at[0, "data"] == png_bytes
            assert metadata["images_processed"] == False

            # Should log warning
            mock_logger.warning.assert_called_once()
            assert (
                "Binary image processing failed" in mock_logger.warning.call_args[0][0]
            )

    @patch("modelhub.serving.inference_types.PDF_SUPPORT", False)
    def test_transform_binary_image_data_no_pil_support(self):
        """Test binary image handling when PIL support is not available."""
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        data = {"data": png_bytes}

        df, metadata = InputTransformer.transform(data, InferenceType.IMAGE_BASE64)

        # Should fall back to raw data
        assert len(df) == 1
        assert df.at[0, "data"] == png_bytes
        assert metadata["images_processed"] == False

    def test_transform_image(self):
        """Test image transformation."""
        data = {"image": b"image bytes"}
        df, metadata = InputTransformer.transform(data, InferenceType.IMAGE)

        assert len(df) == 1
        assert df.at[0, "image"] == b"image bytes"

        # Multiple images
        data = {"images": [b"img1", b"img2"]}
        df, metadata = InputTransformer.transform(data, InferenceType.IMAGE)

        assert len(df) == 2
        assert df.at[0, "image"] == b"img1"
        assert df.at[1, "image"] == b"img2"

    def test_transform_ocr_text(self):
        """Test OCR text transformation."""
        data = {
            "ocr_text_list": ["page1 text", "page2 text"],
            "page_number_list": [1, 2],
        }
        df, metadata = InputTransformer.transform(data, InferenceType.OCR_TEXT)

        assert len(df) == 2
        assert df.at[0, "ocr_text"] == "page1 text"
        assert df.at[0, "page_number"] == 1
        assert df.at[1, "ocr_text"] == "page2 text"
        assert df.at[1, "page_number"] == 2

        # Without page numbers
        data = {"ocr_text_list": ["text1", "text2"]}
        df, metadata = InputTransformer.transform(data, InferenceType.OCR_TEXT)

        assert len(df) == 2
        assert "ocr_text" in df.columns
        assert "page_number" not in df.columns

    def test_transform_tabular(self):
        """Test tabular data transformation."""
        # List of records
        data = {"data": [{"a": 1, "b": 2}, {"a": 3, "b": 4}]}
        df, metadata = InputTransformer.transform(data, InferenceType.TABULAR)

        assert len(df) == 2
        assert df.at[0, "a"] == 1
        assert df.at[1, "b"] == 4

        # Single record
        data = {"data": {"a": 5, "b": 6}}
        df, metadata = InputTransformer.transform(data, InferenceType.TABULAR)

        assert len(df) == 1
        assert df.at[0, "a"] == 5

    def test_transform_structured(self):
        """Test structured data transformation."""
        data = {
            "hcpcs_code": "J1234",
            "rate": 100.50,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }
        df, metadata = InputTransformer.transform(data, InferenceType.STRUCTURED)

        assert len(df) == 1
        assert df.at[0, "hcpcs_code"] == "J1234"
        assert df.at[0, "rate"] == 100.50

    def test_transform_raw(self):
        """Test raw data transformation."""
        data = {"field1": "value1", "field2": 123}
        df, metadata = InputTransformer.transform(data, InferenceType.RAW)

        assert len(df) == 1
        assert df.at[0, "field1"] == "value1"
        assert df.at[0, "field2"] == 123

    def test_transform_with_parameters(self):
        """Test transformation with additional parameters."""
        data = {"text": "Hello", "parameters": {"temperature": 0.7, "max_tokens": 100}}
        df, metadata = InputTransformer.transform(data, InferenceType.TEXT)

        assert metadata["inference_type"] == "text"
        assert metadata["parameters"] == {"temperature": 0.7, "max_tokens": 100}


class TestOutputTransformer:
    """Test OutputTransformer class."""

    def test_transform_dataframe_single_column(self):
        """Test transformation of DataFrame with single column extraction."""
        df = pd.DataFrame({"predictions": ['{"result": "success"}']})

        result = OutputTransformer.transform(
            df, extract_single_column="predictions", parse_json=True
        )

        assert result["status"] == 200
        assert result["data"] == {"result": "success"}
        assert result["error"] is None

    def test_transform_dataframe_multiple_columns(self):
        """Test transformation of DataFrame with multiple columns."""
        df = pd.DataFrame(
            {
                "prediction_page_level": ['{"page1": "data1"}'],
                "prediction_aggregated": ['{"total": 100}'],
                "other_column": ["ignored"],
            }
        )

        result = OutputTransformer.transform(
            df,
            output_columns=["prediction_page_level", "prediction_aggregated"],
            parse_json=True,
        )

        assert result["status"] == 200
        assert result["data"]["prediction_page_level"] == {"page1": "data1"}
        assert result["data"]["prediction_aggregated"] == {"total": 100}
        assert "other_column" not in result["data"]

    def test_transform_dataframe_known_columns(self):
        """Test transformation with all columns included when no output_columns specified."""
        df = pd.DataFrame(
            {
                "predictions": ["[1, 2, 3]"],
                "body": '{"status": "ok"}',
                "custom_column": "value",
            }
        )

        result = OutputTransformer.transform(df, parse_json=True)

        assert result["status"] == 200
        assert result["data"]["predictions"] == [1, 2, 3]
        assert result["data"]["body"] == {"status": "ok"}
        # When no output_columns specified, all columns are included
        assert result["data"]["custom_column"] == "value"

    def test_transform_dict_output(self):
        """Test transformation of dictionary output."""
        output = {"prediction": "result", "confidence": 0.95}

        result = OutputTransformer.transform(output)

        assert result["status"] == 200
        assert result["data"] == {"prediction": "result", "confidence": 0.95}

        # With body key
        output = {"body": {"message": "success"}, "other": "ignored"}
        result = OutputTransformer.transform(output)

        assert result["data"] == {"message": "success"}

    def test_transform_list_output(self):
        """Test transformation of list output."""
        output = [1, 2, 3, 4, 5]

        result = OutputTransformer.transform(output)

        assert result["status"] == 200
        assert result["data"] == {"predictions": [1, 2, 3, 4, 5]}

    def test_transform_numpy_array(self):
        """Test transformation of numpy array."""
        output = np.array([1.0, 2.0, 3.0])

        result = OutputTransformer.transform(output)

        assert result["status"] == 200
        assert result["data"] == {"predictions": [1.0, 2.0, 3.0]}

    def test_transform_scalar_output(self):
        """Test transformation of scalar values."""
        result = OutputTransformer.transform("single value")
        assert result["data"] == {"prediction": "single value"}

        result = OutputTransformer.transform(42)
        assert result["data"] == {"prediction": 42}

        result = OutputTransformer.transform(3.14)
        assert result["data"] == {"prediction": 3.14}

    def test_transform_with_metadata(self):
        """Test transformation with metadata."""
        output = {"result": "success"}
        metadata = {"inference_type": "text", "model_version": "1.0"}

        result = OutputTransformer.transform(output, metadata=metadata)

        assert result["status"] == 200
        assert result["data"] == {"result": "success"}
        assert result["metadata"] == metadata

    def test_transform_json_parsing_disabled(self):
        """Test transformation with JSON parsing disabled."""
        df = pd.DataFrame({"predictions": ['{"json": "string"}']})

        result = OutputTransformer.transform(
            df, extract_single_column="predictions", parse_json=False
        )

        assert result["data"] == '{"json": "string"}'

    def test_transform_error_handling(self):
        """Test error handling in transformation."""
        # Create a mock DataFrame that raises an exception
        mock_df = Mock(spec=pd.DataFrame)
        # Set up columns property that raises exception when iterated
        mock_columns = Mock()
        mock_columns.__iter__ = Mock(side_effect=Exception("Error accessing data"))
        mock_df.columns = mock_columns

        with patch("modelhub.serving.inference_types.logger") as mock_logger:
            result = OutputTransformer.transform(mock_df)

            assert result["status"] == 500
            assert "Error accessing data" in result["error"]
            mock_logger.error.assert_called_once()

    def test_transform_multi_row_dataframe(self):
        """Test transformation of multi-row DataFrame."""
        df = pd.DataFrame({"predictions": ["a", "b", "c"], "scores": [0.1, 0.2, 0.3]})

        result = OutputTransformer.transform(df)

        assert result["status"] == 200
        # Multi-row DataFrames should return lists for each column
        assert result["data"]["predictions"] == ["a", "b", "c"]
        assert result["data"]["scores"] == [0.1, 0.2, 0.3]


class TestUnifiedRequestFunctions:
    """Test unified request helper functions."""

    def test_create_unified_request(self):
        """Test creation of unified request format."""
        inputs = {"text": "Hello"}

        # Without inference type
        request = create_unified_request(inputs)
        assert request == {"inputs": {"text": "Hello"}}

        # With inference type
        request = create_unified_request(inputs, inference_type="text")
        assert request == {"inputs": {"text": "Hello"}, "inference_type": "text"}

    def test_parse_unified_request(self):
        """Test parsing of unified request format."""
        # Unified format
        request = {"inputs": {"text": "Hello"}, "inference_type": "text"}
        inputs, inf_type = parse_unified_request(request)
        assert inputs == {"text": "Hello"}
        assert inf_type == "text"

        # Without inference type
        request = {"inputs": {"data": [1, 2, 3]}}
        inputs, inf_type = parse_unified_request(request)
        assert inputs == {"data": [1, 2, 3]}
        assert inf_type is None

        # Legacy format (no inputs key)
        request = {"text": "Hello", "other": "data"}
        inputs, inf_type = parse_unified_request(request)
        assert inputs == {"text": "Hello", "other": "data"}
        assert inf_type is None


@pytest.mark.parametrize(
    "input_data,expected_type",
    [
        ({"text": "hello"}, InferenceType.TEXT),
        ({"byte_stream": b"pdf"}, InferenceType.BYTE_STREAM),
        ({"image_base64": ["img1"]}, InferenceType.IMAGE_BASE64),
        ({"image": b"img"}, InferenceType.IMAGE),
        ({"images": [b"img1", b"img2"]}, InferenceType.IMAGE),
        ({"ocr_text_list": ["text"]}, InferenceType.OCR_TEXT),
        ({"data": [{"a": 1}]}, InferenceType.TABULAR),
        (
            {
                "hcpcs_code": "J1",
                "rate": 1.0,
                "start_date": "2024-01-01",
                "end_date": "2024-12-31",
            },
            InferenceType.STRUCTURED,
        ),
        ({"unknown": "value"}, InferenceType.RAW),
    ],
)
def test_inference_detection_parametrized(input_data, expected_type):
    """Parametrized test for inference type detection."""
    assert InferenceDetector.detect_type(input_data) == expected_type


class TestIntegrationScenarios:
    """Test integration scenarios combining detection and transformation."""

    def test_pdf_processing_workflow(self):
        """Test complete PDF processing workflow."""
        # Input
        pdf_bytes = b"PDF binary content"
        request = {"byte_stream": pdf_bytes, "page_numbers": [1, 2, 3]}

        # Detection
        inference_type = InferenceDetector.detect_type(request)
        assert inference_type == InferenceType.BYTE_STREAM

        # Transformation
        df, metadata = InputTransformer.transform(request, inference_type)
        assert df.at[0, "data"] == pdf_bytes
        assert df.at[0, "page_numbers"] == [1, 2, 3]

        # Mock model output
        model_output = pd.DataFrame(
            {
                "prediction_page_level": ['{"page1": "content1", "page2": "content2"}'],
                "prediction_aggregated": ['{"total_pages": 3}'],
            }
        )

        # Output transformation
        result = OutputTransformer.transform(
            model_output,
            output_columns=["prediction_page_level", "prediction_aggregated"],
            parse_json=True,
            metadata=metadata,
        )

        assert result["status"] == 200
        assert result["data"]["prediction_page_level"]["page1"] == "content1"
        assert result["data"]["prediction_aggregated"]["total_pages"] == 3
        assert result["metadata"]["inference_type"] == "byte_stream"

    def test_image_classification_workflow(self):
        """Test complete image classification workflow."""
        # Create base64 encoded "images"
        images_b64 = ["image1_base64", "image2_base64", "image3_base64"]
        request = {"image_base64": images_b64}

        # Detection
        inference_type = InferenceDetector.detect_type(request)
        assert inference_type == InferenceType.IMAGE_BASE64

        # Transformation
        df, metadata = InputTransformer.transform(request, inference_type)
        assert len(df) == 3
        assert list(df["data"]) == images_b64

        # Mock model output
        model_output = pd.DataFrame(
            {"predictions": ['{"class": "cat", "confidence": 0.95}']}
        )

        # Output transformation
        result = OutputTransformer.transform(
            model_output,
            extract_single_column="predictions",
            parse_json=True,
            metadata=metadata,
        )

        assert result["status"] == 200
        assert result["data"]["class"] == "cat"
        assert result["data"]["confidence"] == 0.95

    def test_structured_data_workflow(self):
        """Test structured data processing workflow."""
        # Medical billing data
        request = {
            "hcpcs_code": "J3490",
            "rate": 150.00,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "provider_npi": "1234567890",
        }

        # Detection
        inference_type = InferenceDetector.detect_type(request)
        assert inference_type == InferenceType.STRUCTURED

        # Transformation
        df, metadata = InputTransformer.transform(request, inference_type)
        assert len(df) == 1
        assert df.at[0, "hcpcs_code"] == "J3490"
        assert df.at[0, "rate"] == 150.00

        # Mock model output
        model_output = pd.DataFrame(
            {
                "approved": [True],
                "adjusted_rate": [145.50],
                "reason": ["Within acceptable range"],
            }
        )

        # Output transformation
        result = OutputTransformer.transform(model_output, metadata=metadata)

        assert result["status"] == 200
        assert result["data"]["approved"]
        assert result["data"]["adjusted_rate"] == 145.50
        assert result["data"]["reason"] == "Within acceptable range"
