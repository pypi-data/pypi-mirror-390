import os
import shutil

import uyeia


def test_read_cache_error():
    config = uyeia.Config(
        error_cache_location="./tests/samples/errors_cache.db",
        error_config_location="./tests/samples/uyeia.errors.json",
    )
    uyeia.set_global_config(config)
    errors = uyeia.get_errors()
    assert errors and len(errors) == 2


def test_open_corrupted_cache():
    # TODO:  Windows permission issue
    if os.name == "nt":
        return

    import tempfile

    # Use a temporary file to avoid Windows file locking issues
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        temp_db_path = temp_db.name

    # Copy corrupted cache to temporary location
    shutil.copy("./tests/samples/.corrupted_cache.db", temp_db_path)

    config = uyeia.Config(
        error_cache_location=temp_db_path,
        error_config_location="./tests/samples/uyeia.errors.json",
    )
    uyeia.set_global_config(config)
    watcher = uyeia.Watcher("test_watcher")
    watcher.register("T404")
    error = uyeia.get_errors("hot")
    assert error and error.get("status") == "WARNING"
