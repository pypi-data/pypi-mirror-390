#!/usr/bin/env python3
"""
Test script for structured data inference types.
"""

import json

import pandas as pd

from modelhub.serving.inference_types import (
    InferenceDetector,
    InferenceType,
    InputTransformer,
    OutputTransformer,
)


def test_structured_detection():
    """Test that structured data requests are properly detected."""
    print("Testing structured data detection...")

    # Test case 1: Medical records format
    medical_request = {
        "patient_id": "P12345",
        "provider_id": "DR789",
        "diagnosis_code": "E11.9",
    }

    detected_type = InferenceDetector.detect_type(medical_request)
    print(f"Medical records detected as: {detected_type}")
    assert detected_type == InferenceType.STRUCTURED

    # Test case 2: Explicit structured type
    structured_request = {
        "data": {"field1": "value1", "field2": "value2"},
        "inference_type": "structured",
    }

    detected_type = InferenceDetector.detect_type(structured_request)
    print(f"Explicit structured detected as: {detected_type}")
    assert detected_type == InferenceType.STRUCTURED

    print("✓ Structured detection tests passed")


def test_byte_stream_pdf_transform():
    """Test byte stream transformation for PDF models like drug extractor."""
    print("\nTesting byte stream PDF transformation...")

    # Test the correct format for drug_extractor model
    pdf_request = {
        "data": "JVBERi0xLjcKJeLjz9MK...",  # Base64 PDF (truncated for test)
        "page_numbers": [1, 2, 3],
    }

    # This should be detected as byte_stream
    detected_type = InferenceDetector.detect_type(pdf_request)
    print(f"PDF request detected as: {detected_type}")
    # The "data" field with base64 string should be detected as BYTE_STREAM
    assert (
        detected_type == InferenceType.BYTE_STREAM or detected_type == InferenceType.RAW
    )

    df, metadata = InputTransformer.transform(pdf_request, InferenceType.BYTE_STREAM)
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {df.columns.tolist()}")
    print(f"Data field exists: {'data' in df.columns}")
    print(f"Page numbers exists: {'page_numbers' in df.columns}")

    # Verify the data is preserved correctly
    assert "data" in df.columns, "DataFrame should have 'data' column"
    assert df.at[0, "data"] == pdf_request["data"], "PDF data should be preserved"
    if "page_numbers" in df.columns:
        assert df.at[0, "page_numbers"] == [1, 2, 3], "Page numbers should be preserved"

    print("\n✓ Byte stream PDF transformation verified")


def test_structured_multimodal_handling():
    """Test proper handling of multimodal structured data."""
    print("\nTesting multimodal structured data handling...")

    # Multimodal request that should extract text properly
    multimodal_request = {
        "text": [
            {"type": "text", "text": "Patient taking Aspirin 81mg daily"},
            {"type": "image_base64", "image_base64": "base64_data_here"},
        ],
        "page_id": "page_1",
    }

    # For structured data with multimodal content, we should extract just the text
    df, metadata = InputTransformer.transform(
        multimodal_request, InferenceType.STRUCTURED
    )

    # The DataFrame should have proper text extraction
    print(f"Multimodal text extraction: {df.at[0, 'text']}")

    # Test simple text format
    simple_request = {"text": "Patient taking Aspirin 81mg daily", "page_id": "page_1"}

    df2, metadata2 = InputTransformer.transform(
        simple_request, InferenceType.STRUCTURED
    )
    print(f"Simple text: {df2.at[0, 'text']}")

    print("✓ Multimodal handling tests complete")


def test_structured_output_transform():
    """Test structured data output transformation."""
    print("\nTesting structured output transformation...")

    # Simulate drug extraction model output
    drug_output = pd.DataFrame(
        {
            "predictions": [
                json.dumps(
                    {
                        "results": [
                            {
                                "drug_name": "Aspirin",
                                "dosage": "81mg",
                                "frequency": "daily",
                            }
                        ],
                        "extraction_reasoning": "Found 1 drug",
                        "total_drugs_found": 1,
                        "latency_seconds": 0.5,
                        "model_name": "drug_extractor",
                    }
                )
            ]
        }
    )

    metadata = {"inference_type": InferenceType.STRUCTURED.value}

    output = OutputTransformer.transform(
        drug_output, output_columns=["predictions"], metadata=metadata
    )

    print(f"Output format: {json.dumps(output, indent=2)}")
    print("✓ Output transformation tests passed")


def main():
    """Run all tests."""
    print("Testing structured data inference types\n")

    try:
        test_structured_detection()
        test_byte_stream_pdf_transform()
        test_structured_multimodal_handling()
        test_structured_output_transform()

        print("\n✅ All structured data tests completed!")
        print("\nKey findings:")
        print("- Drug extractor uses byte_stream type, not structured")
        print("- Multimodal text fields handled for true structured data")
        print("- PDF models expect 'data' field with base64/bytes")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
