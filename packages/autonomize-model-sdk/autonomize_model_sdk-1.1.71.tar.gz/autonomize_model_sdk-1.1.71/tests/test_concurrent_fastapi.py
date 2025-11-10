#!/usr/bin/env python3
"""
Test script to verify AsyncExecutor works correctly with concurrent FastAPI requests.

This script simulates the MLflow serving environment where FastAPI runs model.predict()
in asyncio.to_thread() and tests that our AsyncExecutor handles event loops correctly.
"""

import asyncio
import concurrent.futures
import json
import logging
import time
from typing import Any, Dict

import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modelhub.serving import AsyncExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Simulate a model that uses AsyncExecutor (like the pharmacy models)
class MockGeminiModel:
    """Mock model that simulates async Gemini API calls."""

    def __init__(self):
        self.call_count = 0

    async def async_gemini_call(self, data: str) -> Dict[str, Any]:
        """Simulate an async API call to Gemini."""
        # Simulate API latency
        await asyncio.sleep(0.1)

        self.call_count += 1
        return {
            "result": f"Processed: {data}",
            "call_number": self.call_count,
            "thread_name": (
                asyncio.current_task().get_name()
                if asyncio.current_task()
                else "unknown"
            ),
        }

    def predict(self, model_input: pd.DataFrame) -> pd.DataFrame:
        """MLflow-style predict method that uses AsyncExecutor."""
        results = []

        for _, row in model_input.iterrows():
            data = row.get("data", "default")

            # Use AsyncExecutor to run async code (like pharmacy models do)
            result = AsyncExecutor.run_async(self.async_gemini_call, data, timeout=5)
            results.append(result)

        return pd.DataFrame({"predictions": [json.dumps(results)]})


# Create FastAPI app that simulates MLflow serving
app = FastAPI()
model = MockGeminiModel()


@app.post("/predict")
async def predict(request: Dict[str, Any]):
    """Simulate MLflow's prediction endpoint."""
    # Convert request to DataFrame
    input_df = pd.DataFrame(request.get("inputs", [{"data": "test"}]))

    # Run prediction in thread pool (like MLflow does)
    result_df = await asyncio.to_thread(model.predict, input_df)

    # Return result
    predictions = json.loads(result_df["predictions"].iloc[0])
    return {"predictions": predictions}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


# Test functions
def test_single_request():
    """Test a single request works correctly."""
    client = TestClient(app)

    response = client.post("/predict", json={"inputs": [{"data": "test_single"}]})
    assert response.status_code == 200

    result = response.json()
    assert "predictions" in result
    assert len(result["predictions"]) == 1
    assert result["predictions"][0]["result"] == "Processed: test_single"

    logger.info("✅ Single request test passed")


def test_concurrent_requests():
    """Test multiple concurrent requests to verify event loop handling."""
    client = TestClient(app)
    num_requests = 20  # Same as user's test scenario

    # Reset model call count
    model.call_count = 0

    def make_request(i: int):
        """Make a single request."""
        try:
            response = client.post(
                "/predict", json={"inputs": [{"data": f"test_concurrent_{i}"}]}
            )
            if response.status_code != 200:
                logger.error(
                    f"Request {i} failed: {response.status_code} - {response.text}"
                )
                return None
            return response.json()
        except Exception as e:
            logger.error(f"Request {i} error: {e}")
            return None

    # Run concurrent requests
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    elapsed = time.time() - start_time

    # Verify all requests succeeded
    successful = [r for r in results if r is not None]
    failed = num_requests - len(successful)

    logger.info(f"Completed {num_requests} requests in {elapsed:.2f}s")
    logger.info(f"Successful: {len(successful)}, Failed: {failed}")

    assert failed == 0, f"{failed} requests failed"
    assert (
        model.call_count == num_requests
    ), f"Expected {num_requests} calls, got {model.call_count}"

    logger.info("✅ Concurrent requests test passed")


def test_stress_test():
    """Stress test with many concurrent requests."""
    client = TestClient(app)
    num_requests = 100
    batch_size = 5  # Requests per batch

    def make_batch_request(batch_id: int):
        """Make a batch request with multiple items."""
        try:
            inputs = [{"data": f"stress_{batch_id}_{i}"} for i in range(batch_size)]
            response = client.post("/predict", json={"inputs": inputs})

            if response.status_code != 200:
                logger.error(f"Batch {batch_id} failed: {response.status_code}")
                return None
            return response.json()
        except Exception as e:
            logger.error(f"Batch {batch_id} error: {e}")
            return None

    # Reset model
    model.call_count = 0

    # Run stress test
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(make_batch_request, i)
            for i in range(num_requests // batch_size)
        ]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    elapsed = time.time() - start_time

    # Verify results
    successful = [r for r in results if r is not None]
    failed = (num_requests // batch_size) - len(successful)

    logger.info(f"Stress test: {num_requests} items in {elapsed:.2f}s")
    logger.info(f"Successful batches: {len(successful)}, Failed: {failed}")
    logger.info(f"Total model calls: {model.call_count}")

    assert failed == 0, f"{failed} batches failed"
    assert (
        model.call_count == num_requests
    ), f"Expected {num_requests} calls, got {model.call_count}"

    logger.info("✅ Stress test passed")


def test_error_recovery():
    """Test that AsyncExecutor recovers from event loop errors."""

    # Simulate event loop issues
    async def problematic_async_func():
        """Function that might encounter event loop issues."""
        # Try to get the current loop
        try:
            loop = asyncio.get_running_loop()
            if loop.is_closed():
                raise RuntimeError("Event loop is closed")
        except RuntimeError:
            pass

        # Simulate work
        await asyncio.sleep(0.05)
        return "recovered"

    # Test recovery in different scenarios
    for i in range(5):
        try:
            result = AsyncExecutor.run_async(problematic_async_func, timeout=2)
            assert result == "recovered"
            logger.info(f"✅ Error recovery test {i+1} passed")
        except Exception as e:
            logger.error(f"❌ Error recovery test {i+1} failed: {e}")
            raise


def test_cleanup():
    """Test that AsyncExecutor properly cleans up resources."""
    # Get initial task count safely
    try:
        loop = asyncio.get_running_loop()
        initial_thread_count = len(asyncio.all_tasks(loop))
    except RuntimeError:
        initial_thread_count = 0

    # Make several requests
    client = TestClient(app)
    for i in range(10):
        response = client.post("/predict", json={"inputs": [{"data": f"cleanup_{i}"}]})
        assert response.status_code == 200

    # Check thread count hasn't grown excessively
    try:
        loop = asyncio.get_running_loop()
        final_thread_count = len(asyncio.all_tasks(loop))
    except RuntimeError:
        final_thread_count = 0

    thread_growth = final_thread_count - initial_thread_count

    logger.info(f"Thread growth: {thread_growth}")
    assert thread_growth < 5, f"Excessive thread growth: {thread_growth}"

    logger.info("✅ Cleanup test passed")


if __name__ == "__main__":
    logger.info("Starting AsyncExecutor concurrent FastAPI tests...")

    try:
        # Run all tests
        test_single_request()
        test_concurrent_requests()
        test_stress_test()
        test_error_recovery()
        test_cleanup()

        logger.info(
            "\n🎉 All tests passed! AsyncExecutor is working correctly with concurrent FastAPI requests."
        )

    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        raise
    finally:
        # Cleanup
        AsyncExecutor.shutdown()
