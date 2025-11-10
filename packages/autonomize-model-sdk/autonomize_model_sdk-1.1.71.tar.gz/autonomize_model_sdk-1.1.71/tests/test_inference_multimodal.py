#!/usr/bin/env python3
"""
Test script for multimodal inference handling.
"""


from modelhub.serving.inference_types import (
    InferenceDetector,
    InferenceType,
    InputTransformer,
)


def test_multimodal_text_extraction():
    """Test extraction of text from multimodal content."""
    print("Testing multimodal text extraction...")

    # Test case 1: Single text part with image
    request1 = {
        "text": [
            {"type": "text", "text": "Patient taking Aspirin 81mg daily"},
            {"type": "image_base64", "image_base64": "base64_image_data"},
        ],
        "page_id": "page_1",
    }

    detected = InferenceDetector.detect_type(request1)
    # Note: After removing drug extraction patterns, this is now detected as TEXT
    assert detected == InferenceType.TEXT

    df, _ = InputTransformer.transform(request1, InferenceType.STRUCTURED)
    assert df.at[0, "text"] == "Patient taking Aspirin 81mg daily"
    print("✓ Single text part extracted correctly")

    # Test case 2: Multiple text parts
    request2 = {
        "text": [
            {"type": "text", "text": "Patient history:"},
            {"type": "image_base64", "image_base64": "base64_image_data"},
            {"type": "text", "text": "Taking Aspirin 81mg daily and Lisinopril 10mg"},
        ],
        "chunk_id": "chunk_456",
    }

    # Still test with STRUCTURED type to verify multimodal handling works
    df2, _ = InputTransformer.transform(request2, InferenceType.STRUCTURED)
    assert (
        df2.at[0, "text"]
        == "Patient history: Taking Aspirin 81mg daily and Lisinopril 10mg"
    )
    print("✓ Multiple text parts joined correctly")

    # Test case 3: Only images (no text)
    request3 = {
        "text": [
            {"type": "image_base64", "image_base64": "base64_image_data1"},
            {"type": "image_base64", "image_base64": "base64_image_data2"},
        ],
        "page_id": "page_2",
    }

    df3, _ = InputTransformer.transform(request3, InferenceType.STRUCTURED)
    assert df3.at[0, "text"] == ""
    print("✓ Empty string returned when no text parts")

    # Test case 4: Mixed content with unknown types
    request4 = {
        "text": [
            {"type": "text", "text": "Medications:"},
            {"type": "unknown", "data": "some_data"},
            {"type": "text", "text": "Aspirin"},
        ],
        "page_id": "page_3",
    }

    df4, _ = InputTransformer.transform(request4, InferenceType.STRUCTURED)
    assert df4.at[0, "text"] == "Medications: Aspirin"
    print("✓ Unknown types ignored, only text extracted")

    # Test case 5: Simple string text (non-multimodal)
    request5 = {"text": "Simple text content", "page_id": "page_4"}

    df5, _ = InputTransformer.transform(request5, InferenceType.STRUCTURED)
    assert df5.at[0, "text"] == "Simple text content"
    print("✓ Simple string text preserved as-is")

    print("\n✅ All multimodal text extraction tests passed!")


def test_edge_cases():
    """Test edge cases in multimodal handling."""
    print("\nTesting edge cases...")

    # Empty text list
    request1 = {"text": [], "page_id": "page_1"}
    df1, _ = InputTransformer.transform(request1, InferenceType.STRUCTURED)
    assert df1.at[0, "text"] == ""
    print("✓ Empty list handled correctly")

    # Malformed items
    request2 = {
        "text": [
            {"type": "text"},  # Missing text field
            {"text": "No type field"},  # Missing type field
            {"type": "text", "text": "Valid text"},
        ],
        "page_id": "page_2",
    }
    df2, _ = InputTransformer.transform(request2, InferenceType.STRUCTURED)
    # Debug print
    print(f"Debug - Extracted text: '{df2.at[0, 'text']}'")
    # Items without proper type="text" are ignored, empty text values are joined
    assert df2.at[0, "text"] == " Valid text" or df2.at[0, "text"] == "Valid text"
    print("✓ Malformed items handled gracefully")

    # Mixed types in text field
    request3 = {
        "text": "This should not happen",  # String instead of list
        "another_field": [{"type": "text", "text": "Should not extract"}],
    }
    df3, _ = InputTransformer.transform(request3, InferenceType.STRUCTURED)
    assert df3.at[0, "text"] == "This should not happen"
    # The another_field should be preserved as-is (list of dicts)
    assert isinstance(df3.at[0, "another_field"], list)
    assert df3.at[0, "another_field"][0]["text"] == "Should not extract"
    print("✓ Only 'text' field processed for multimodal extraction")

    print("\n✅ All edge case tests passed!")


def main():
    """Run all tests."""
    print("Testing multimodal inference handling\n")

    try:
        test_multimodal_text_extraction()
        test_edge_cases()

        print("\n🎉 All multimodal tests passed successfully!")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
