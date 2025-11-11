import os
import time
from importlib import reload

import pytest

import uyeia


@pytest.fixture(autouse=True)
def cleanup_tests_folder():
    def delete_file_config(path):
        if os.path.exists(path):
            # Retry logic for Windows file locking issues
            max_attempts = 20
            for attempt in range(max_attempts):
                try:
                    os.remove(path)
                    break
                except (PermissionError, OSError):
                    if attempt < max_attempts - 1:
                        time.sleep(0.1)  # Wait 100ms before retry
                        continue

    delete_file_config("./tests/uyeia.errors.json")
    delete_file_config("./tests/errors_cache.db")
    delete_file_config("./tests/samples/corrupted_cache.db")
    yield
    delete_file_config("./tests/uyeia.errors.json")
    delete_file_config("./tests/errors_cache.db")
    delete_file_config("./tests/samples/corrupted_cache.db")


@pytest.fixture(autouse=True)
def reload_package():
    global uyeia
    reload(uyeia)
    yield


@pytest.fixture
def sample_config():
    return uyeia.Config(
        error_config_location="./tests/samples/uyeia.errors.json",
        error_cache_location="./tests/errors_cache.db",
    )


@pytest.fixture(autouse=True)
def ensure_db_cleanup():
    """Ensure database connections are properly closed after each test."""
    yield

    # Force close any remaining database connections
    if hasattr(uyeia, "__root__"):
        try:
            if hasattr(uyeia.__root__, "close_cache"):
                uyeia.__root__.close_cache()
        except Exception:
            pass

    # Additional Windows-specific cleanup with retry logic
    import gc

    gc.collect()  # Force garbage collection

    db_paths = ["./tests/errors_cache.db", "./tests/samples/corrupted_cache.db"]
    for db_path in db_paths:
        # Clean up both the main file and associated SQLite files
        for suffix in ["", "-wal", "-shm"]:
            file_path = db_path + suffix
            if os.path.exists(file_path):
                max_attempts = 10
                for attempt in range(max_attempts):
                    try:
                        os.remove(file_path)
                        break
                    except (PermissionError, OSError):
                        if attempt < max_attempts - 1:
                            time.sleep(0.05)  # Wait 50ms before retry
                            continue
