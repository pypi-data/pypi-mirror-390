import json
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

from uyeia import Vault, Watcher, get_errors, set_global_config
from uyeia.type import Config


@pytest.fixture
def thread_safe_config():
    """Create a test configuration for thread safety testing."""
    temp_dir = tempfile.mkdtemp()

    config = Config()
    config.error_cache_location = os.path.join(temp_dir, "thread_test_cache.db")
    config.error_config_location = os.path.join(temp_dir, "thread_test_errors.json")
    config.status = {
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL",
    }
    config.disable_logging = True

    # Create error definitions
    error_definitions = {
        "THREAD_TEST_001": {
            "status": "INFO",
            "message": "Thread test message {{thread_id}}",
        },
        "THREAD_TEST_002": {
            "status": "ERROR",
            "message": "Thread error test {{thread_id}}",
        },
    }

    with open(config.error_config_location, "w") as f:
        json.dump(error_definitions, f)

    set_global_config(config)

    yield config

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)


def test_concurrent_watcher_operations(thread_safe_config):
    """Test that multiple threads can use watchers concurrently without SQLite errors."""

    def worker_thread(thread_id, num_ops=10):
        """Worker function for each thread."""
        try:
            watcher = Watcher(f"test_thread_{thread_id}")

            for i in range(num_ops):
                # Alternate between different error codes
                error_code = "THREAD_TEST_001" if i % 2 == 0 else "THREAD_TEST_002"
                watcher.register(error_code, vars={"thread_id": str(thread_id)})

                # Get status to ensure cache operations work
                status = watcher.get_actual_status()
                assert status is not None

                # Release occasionally to test cache cleanup
                if i % 3 == 2:
                    watcher.release()

            return True
        except Exception as e:
            return f"Thread {thread_id} failed: {str(e)}"

    # Run multiple threads concurrently
    num_threads = 8
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_thread, i) for i in range(num_threads)]

        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    # Check all threads completed successfully
    errors = [r for r in results if r is not True]
    assert len(errors) == 0, f"Threads failed with errors: {errors}"

    # Verify we can still read from cache
    cached_errors = get_errors("all")
    assert cached_errors is not None


def test_concurrent_vault_operations(thread_safe_config):
    """Test that vault operations work correctly across threads."""

    def vault_worker(thread_id, num_ops=5):
        """Worker function for vault operations."""
        try:
            vault = Vault()

            for i in range(num_ops):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"

                # Set value
                vault.set(key, value)

                # Retrieve and verify
                retrieved = vault.get(key)
                assert retrieved == value, f"Expected {value}, got {retrieved}"

                # Remove
                vault.remove(key)

                # Verify removal
                assert vault.get(key) is None

            return True
        except Exception as e:
            return f"Vault thread {thread_id} failed: {str(e)}"

    # Run multiple threads concurrently
    num_threads = 6
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(vault_worker, i) for i in range(num_threads)]

        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    # Check all threads completed successfully
    errors = [r for r in results if r is not True]
    assert len(errors) == 0, f"Vault threads failed with errors: {errors}"


def test_mixed_operations_thread_safety(thread_safe_config):
    """Test mixed watcher and vault operations across threads."""

    def mixed_worker(thread_id):
        """Worker that performs both watcher and vault operations."""
        try:
            # Watcher operations
            watcher = Watcher(f"mixed_thread_{thread_id}")
            watcher.register("THREAD_TEST_001", vars={"thread_id": str(thread_id)})

            # Vault operations
            vault = Vault()
            vault.set(f"mixed_key_{thread_id}", f"mixed_value_{thread_id}")
            retrieved = vault.get(f"mixed_key_{thread_id}")

            # Verify watcher status
            status = watcher.get_actual_status()
            assert status is not None
            assert retrieved == f"mixed_value_{thread_id}"

            watcher.release()
            vault.remove(f"mixed_key_{thread_id}")

            return True
        except Exception as e:
            return f"Mixed thread {thread_id} failed: {str(e)}"

    # Run multiple threads concurrently
    num_threads = 5
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(mixed_worker, i) for i in range(num_threads)]

        results = []
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    # Check all threads completed successfully
    errors = [r for r in results if r is not True]
    assert len(errors) == 0, f"Mixed operation threads failed with errors: {errors}"
