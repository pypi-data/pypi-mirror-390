"""
Async utilities for MLflow model serving.

This module provides utilities for safely executing async functions in MLflow serving
environments, which use thread pools for request handling.
"""

import asyncio
import concurrent.futures
import logging
import threading
from typing import Any, Callable, Coroutine, Optional, TypeVar

T = TypeVar("T")
logger = logging.getLogger(__name__)


class AsyncExecutor:
    """
    Thread-safe executor for running async functions in MLflow serving environments.

    This executor intelligently detects the execution context and uses the most
    appropriate method to run async functions, avoiding nested thread pools and
    event loop conflicts that can occur in production serving.

    Key Features:
    - Detects if running in main thread vs worker thread
    - Avoids nested thread pools when called from MLflow's asyncio.to_thread
    - Provides clean event loop lifecycle management
    - Supports timeouts and proper error handling

    Example:
        # In your MLflow model's predict method:
        from modelhub.serving import AsyncExecutor

        async def process_with_llm(data):
            # Your async LLM call here
            result = await llm_client.generate(data)
            return result

        class MyModel(mlflow.pyfunc.PythonModel):
            def predict(self, context, model_input):
                # This works safely in MLflow serving
                result = AsyncExecutor.run_async(
                    process_with_llm,
                    model_input,
                    timeout=30
                )
                return result
    """

    # Global thread pool for async operations (used only from main thread)
    _executor = None
    _lock = threading.Lock()

    @classmethod
    def _get_executor(cls):
        """Get or create the thread pool executor."""
        if cls._executor is None:
            with cls._lock:
                if cls._executor is None:
                    cls._executor = concurrent.futures.ThreadPoolExecutor(
                        max_workers=10, thread_name_prefix="AsyncExecutor"
                    )
        return cls._executor

    @staticmethod
    def _run_in_thread(
        async_func: Callable, args: tuple, kwargs: dict, timeout: Optional[float]
    ) -> Any:
        """Run async function in a dedicated thread with its own event loop."""
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the async function
            if timeout:
                coro = asyncio.wait_for(async_func(*args, **kwargs), timeout=timeout)
            else:
                coro = async_func(*args, **kwargs)

            result = loop.run_until_complete(coro)
            return result

        except asyncio.TimeoutError:
            logger.error(f"Operation timed out after {timeout} seconds")
            raise TimeoutError(f"Operation timed out after {timeout} seconds")
        except asyncio.CancelledError:
            logger.warning("Operation was cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in async function: {e}", exc_info=True)
            raise
        finally:
            # Clean shutdown of the event loop
            try:
                # Cancel all pending tasks
                pending = asyncio.all_tasks(loop)
                if pending:
                    logger.debug(f"Cancelling {len(pending)} pending tasks")
                    for task in pending:
                        task.cancel()

                    # Wait for cancellation to complete with a short timeout
                    try:
                        loop.run_until_complete(
                            asyncio.wait_for(
                                asyncio.gather(*pending, return_exceptions=True),
                                timeout=1.0,
                            )
                        )
                    except asyncio.TimeoutError:
                        logger.warning("Some tasks didn't cancel in time")

                # Close the loop
                loop.close()
                logger.debug("Event loop closed successfully")

            except Exception as e:
                logger.error(f"Error during event loop cleanup: {e}")

    @classmethod
    def run_async(
        cls,
        async_func: Callable[..., Coroutine[Any, Any, T]],
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> T:
        """
        Execute an async function in a thread-safe manner.

        This method intelligently detects the execution context and uses the
        most appropriate method to run the async function, avoiding nested
        thread pools and event loop conflicts.

        When called from the main thread:
        - Uses a thread pool to run the async function
        - Creates a new event loop in the worker thread

        When called from a worker thread (e.g., MLflow serving):
        - Uses asyncio.run() directly to avoid nested thread pools
        - Each call gets its own event loop for isolation

        Args:
            async_func: The async function to execute
            *args: Positional arguments for the function
            timeout: Optional timeout in seconds
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the async function

        Raises:
            TimeoutError: If the operation times out

        Example:
            async def fetch_data(url):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        return await response.json()

            # This works in any context
            data = AsyncExecutor.run_async(fetch_data, "https://api.example.com/data")
        """
        # Check if we're in FastAPI/Uvicorn context with an event loop
        try:
            loop = asyncio.get_running_loop()

            # Check if the loop is closed
            if loop.is_closed():
                logger.debug("Detected closed event loop, creating new one")
                raise RuntimeError("Event loop is closed")

            # Check if we're in the main thread with a running loop (FastAPI request context)
            if threading.current_thread() is threading.main_thread():
                logger.debug("In main thread with running event loop (FastAPI context)")

                # Create a new event loop in a worker thread to avoid blocking FastAPI
                executor = cls._get_executor()
                future = executor.submit(
                    cls._run_in_thread, async_func, args, kwargs, timeout
                )

                try:
                    thread_timeout = (timeout + 5) if timeout else None
                    return future.result(timeout=thread_timeout)
                except concurrent.futures.TimeoutError:
                    future.cancel()
                    raise TimeoutError(f"Operation timed out after {timeout} seconds")
            else:
                # We're in a worker thread with a running loop
                logger.debug("In worker thread with running event loop")

                # Create task in the existing loop
                if timeout:
                    coro = asyncio.wait_for(
                        async_func(*args, **kwargs), timeout=timeout
                    )
                else:
                    coro = async_func(*args, **kwargs)

                # Use create_task for better performance
                task = asyncio.create_task(coro)
                return asyncio.run_coroutine_threadsafe(task, loop).result()

        except RuntimeError as e:
            # No running event loop or loop is closed
            logger.debug(f"No running event loop or error: {e}")

        # Check if we're already in a worker thread (not main thread)
        if threading.current_thread() is not threading.main_thread():
            logger.debug(f"Running in worker thread: {threading.current_thread().name}")

            # We're in a worker thread without a running loop
            # This is the typical MLflow serving scenario
            max_retries = 3
            last_error = None

            for attempt in range(max_retries):
                try:
                    # Check if there's an existing event loop that might be closed
                    try:
                        existing_loop = asyncio.get_event_loop()
                        if existing_loop.is_closed():
                            logger.debug(
                                f"Found closed event loop on attempt {attempt + 1}, clearing it"
                            )
                            asyncio.set_event_loop(None)
                    except RuntimeError:
                        # No event loop, which is fine
                        pass

                    # Use asyncio.run() for complete isolation
                    # This creates a fresh event loop and properly cleans it up
                    logger.debug(f"Using asyncio.run() for attempt {attempt + 1}")

                    async def wrapped_coro():
                        if timeout:
                            return await asyncio.wait_for(
                                async_func(*args, **kwargs), timeout=timeout
                            )
                        else:
                            return await async_func(*args, **kwargs)

                    # asyncio.run() handles all event loop lifecycle management
                    result = asyncio.run(wrapped_coro())
                    logger.debug(
                        f"Successfully completed async function on attempt {attempt + 1}"
                    )
                    return result

                except Exception as e:
                    last_error = e
                    error_msg = str(e)

                    # Handle specific error patterns
                    if (
                        "Event loop is closed" in error_msg
                        and attempt < max_retries - 1
                    ):
                        logger.warning(
                            f"Event loop closed error on attempt {attempt + 1}, retrying..."
                        )
                        # Small delay before retry
                        import time

                        time.sleep(0.1 * (attempt + 1))
                        continue
                    elif (
                        "Cannot run the event loop while another loop is running"
                        in error_msg
                        and attempt < max_retries - 1
                    ):
                        logger.warning(
                            f"Nested event loop error on attempt {attempt + 1}, retrying..."
                        )
                        # Clear any existing event loop
                        asyncio.set_event_loop(None)
                        continue
                    elif (
                        "This event loop is already running" in error_msg
                        and attempt < max_retries - 1
                    ):
                        logger.warning(
                            f"Event loop already running on attempt {attempt + 1}, retrying..."
                        )
                        asyncio.set_event_loop(None)
                        continue
                    else:
                        # Log the error with full traceback
                        logger.error(
                            f"Failed to execute async function: {e}", exc_info=True
                        )
                        raise

            # If we get here, all retries failed
            if last_error:
                raise last_error

        else:
            # We're in the main thread - use thread pool
            logger.debug("Running in main thread, using thread pool")
            executor = cls._get_executor()
            future = executor.submit(
                cls._run_in_thread, async_func, args, kwargs, timeout
            )

            # Wait for completion with optional timeout
            try:
                # Add a small buffer to the timeout for thread overhead
                thread_timeout = (timeout + 5) if timeout else None
                return future.result(timeout=thread_timeout)
            except concurrent.futures.TimeoutError:
                # Cancel the future if possible
                future.cancel()
                raise TimeoutError(f"Operation timed out after {timeout} seconds")

    @classmethod
    def shutdown(cls):
        """
        Shutdown the thread pool executor.

        Call this when your application is shutting down to clean up resources.
        This is especially important in test environments.
        """
        if cls._executor is not None:
            with cls._lock:
                if cls._executor is not None:
                    cls._executor.shutdown(wait=True)
                    cls._executor = None


# Compatibility function for easier migration
def run_async(async_func: Callable[..., Coroutine[Any, Any, T]], *args, **kwargs) -> T:
    """
    Convenience function for running async functions.

    This is a shorthand for AsyncExecutor.run_async() for simpler usage.

    Example:
        from modelhub.serving.async_utils import run_async

        result = run_async(my_async_function, arg1, arg2, timeout=30)
    """
    return AsyncExecutor.run_async(async_func, *args, **kwargs)


class EventLoopContext:
    """
    Context manager for isolating event loops in Google AI SDK operations.

    This ensures that each Google AI SDK call gets a clean event loop context,
    preventing conflicts with FastAPI/MLflow event loops.
    """

    def __init__(self):
        self.original_loop = None
        self.new_loop = None

    def __enter__(self):
        """Set up a new event loop context."""
        try:
            self.original_loop = asyncio.get_event_loop()
        except RuntimeError:
            self.original_loop = None

        # Create and set a new event loop
        self.new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.new_loop)
        return self.new_loop

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up the event loop context."""
        if self.new_loop:
            try:
                # Cancel any pending tasks
                pending = asyncio.all_tasks(self.new_loop)
                for task in pending:
                    task.cancel()

                # Give tasks a chance to cleanup
                if pending:
                    self.new_loop.run_until_complete(
                        asyncio.wait_for(
                            asyncio.gather(*pending, return_exceptions=True),
                            timeout=0.5,
                        )
                    )
            except Exception:
                pass
            finally:
                # Close the loop
                try:
                    self.new_loop.close()
                except Exception:
                    pass

        # Restore the original loop
        if self.original_loop and not self.original_loop.is_closed():
            asyncio.set_event_loop(self.original_loop)
        else:
            asyncio.set_event_loop(None)
