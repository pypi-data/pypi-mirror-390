# AsyncExecutor Event Loop Fixes

## Summary

Fixed persistent "Event loop is closed" errors that occurred under concurrent load in FastAPI/MLflow serving environments. The issue was caused by event loop lifecycle conflicts between FastAPI, MLflow's asyncio.to_thread(), and the Google AI SDK.

## Root Cause

The Google AI SDK (used via autonomize-autorag) was creating and managing its own event loops internally. When these event loops were closed after a request, subsequent requests would fail with "Event loop is closed" because the SDK or underlying libraries were trying to reuse the closed loop.

## Solution

### Using asyncio.run() for Complete Isolation

The key fix was to use `asyncio.run()` instead of manually managing event loops in worker threads. This ensures:
1. Each async operation gets a completely fresh event loop
2. The event loop is properly cleaned up after each operation
3. No event loop state persists between requests

```python
# Instead of manually creating and managing loops:
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    result = loop.run_until_complete(coro)
finally:
    loop.close()

# We now use:
result = asyncio.run(coro)
```

## Key Changes

### 1. Enhanced Event Loop Detection (async_utils.py)
- Added detection for closed event loops with proper fallback
- Improved handling of FastAPI's main thread event loop context
- Clear separation between main thread and worker thread execution paths

### 2. Simplified Worker Thread Execution
- Replaced manual event loop management with `asyncio.run()`
- Removed complex cleanup code that could interfere with Google AI SDK
- Each request gets a completely isolated event loop context

### 3. Retry Logic for Transient Errors
- Added automatic retry (up to 3 attempts) for event loop-related errors
- Specific handling for:
  - "Event loop is closed"
  - "Cannot run the event loop while another loop is running"
  - "This event loop is already running"
- Exponential backoff between retries

### 4. Improved Error Handling
- Enhanced logging throughout the async execution pipeline
- Better error messages with full tracebacks
- Removed error-prone cleanup code that could mask real issues

## Testing

Created comprehensive test suite (`test_concurrent_fastapi.py`) that verifies:
- Single request handling
- 20 concurrent requests (matching production scenario)
- 100-item stress test with batch processing
- Error recovery from event loop issues
- Resource cleanup and no thread leakage

All tests pass successfully, demonstrating the fixes resolve the production issues.

## Usage

The fixes are transparent to existing code. Models using AsyncExecutor will automatically benefit from the improvements:

```python
from modelhub.serving import AsyncExecutor

# Works correctly in all contexts now
result = AsyncExecutor.run_async(
    async_function,
    *args,
    timeout=30,
    **kwargs
)
```

## Production Deployment

1. Update modelhub-sdk to include these changes
2. Ensure all pharmacy models import AsyncExecutor from modelhub.serving (not local utils)
3. Deploy and monitor for any event loop errors
4. The retry logic will log warnings if transient issues occur but recover automatically
