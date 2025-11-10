#!/usr/bin/env python3
"""
Test script for embedding model support in ModelServer.
"""

import json

import pandas as pd

from modelhub.serving.inference_types import (
    InferenceDetector,
    InferenceType,
    InputTransformer,
    OutputTransformer,
)


def test_embedding_detection():
    """Test that embedding requests are properly detected."""
    print("Testing embedding detection...")

    # Test data matching embedding format
    embedding_request = {
        "texts": ["this is my proc and diagnosis desc", "another text"],
        "model_name": "bge_base",
    }

    detected_type = InferenceDetector.detect_type(embedding_request)
    print(f"Detected type: {detected_type}")
    assert (
        detected_type == InferenceType.EMBEDDING
    ), f"Expected EMBEDDING, got {detected_type}"
    print("✓ Embedding detection passed")


def test_embedding_input_transform():
    """Test that embedding input is properly transformed to DataFrame."""
    print("\nTesting embedding input transformation...")

    embedding_request = {
        "texts": ["this is my proc and diagnosis desc", "another text"],
        "model_name": "bge_base",
    }

    df, metadata = InputTransformer.transform(
        embedding_request, InferenceType.EMBEDDING
    )

    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {df.columns.tolist()}")
    print(f"DataFrame content:\n{df}")
    print(f"Metadata: {metadata}")

    assert "texts" in df.columns, "DataFrame should have 'texts' column"
    assert df.shape[0] == 1, "DataFrame should have 1 row"
    assert isinstance(df.at[0, "texts"], list), "texts should be a list"
    assert len(df.at[0, "texts"]) == 2, "texts list should have 2 items"
    assert metadata.get("model_name") == "bge_base", "model_name should be in metadata"

    print("✓ Embedding input transformation passed")


def test_embedding_output_transform():
    """Test that embedding output is properly formatted."""
    print("\nTesting embedding output transformation...")

    # Simulate model output as DataFrame with embeddings
    embeddings_data = [
        [0.1, 0.2, 0.3, 0.4],  # First text embedding
        [0.5, 0.6, 0.7, 0.8],  # Second text embedding
    ]

    # Test case 1: DataFrame with 'embeddings' column
    df_result = pd.DataFrame({"embeddings": [embeddings_data]})
    metadata = {"inference_type": InferenceType.EMBEDDING.value}

    output = OutputTransformer.transform(df_result, metadata=metadata)
    print(f"Output format test 1: {output}")
    assert output == {
        "prediction": embeddings_data
    }, f"Expected {{'prediction': {embeddings_data}}}, got {output}"
    print("✓ DataFrame output format passed")

    # Test case 2: Dict result with embeddings
    dict_result = {"embeddings": embeddings_data}
    output = OutputTransformer.transform(dict_result, metadata=metadata)
    print(f"Output format test 2: {output}")
    assert output == {
        "prediction": embeddings_data
    }, f"Expected {{'prediction': {embeddings_data}}}, got {output}"
    print("✓ Dict output format passed")

    # Test case 3: DataFrame with 'prediction' column (alternative name)
    df_result2 = pd.DataFrame({"prediction": [embeddings_data]})
    output = OutputTransformer.transform(df_result2, metadata=metadata)
    print(f"Output format test 3: {output}")
    assert output == {
        "prediction": embeddings_data
    }, f"Expected {{'prediction': {embeddings_data}}}, got {output}"
    print("✓ Alternative column name passed")

    # Test case 4: JSON string in DataFrame
    df_result3 = pd.DataFrame({"embeddings": [json.dumps(embeddings_data)]})
    output = OutputTransformer.transform(df_result3, metadata=metadata)
    print(f"Output format test 4: {output}")
    assert output == {
        "prediction": embeddings_data
    }, f"Expected {{'prediction': {embeddings_data}}}, got {output}"
    print("✓ JSON string parsing passed")


def main():
    """Run all tests."""
    print("Testing embedding model support in ModelServer\n")

    try:
        test_embedding_detection()
        test_embedding_input_transform()
        test_embedding_output_transform()

        print("\n✅ All tests passed!")
        print("\nThe ModelServer now supports embedding models with:")
        print(
            '- Request format: {"texts": ["text1", "text2"], "model_name": "bge_base"}'
        )
        print('- Response format: {"prediction": [[...], [...], ...]}')

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
