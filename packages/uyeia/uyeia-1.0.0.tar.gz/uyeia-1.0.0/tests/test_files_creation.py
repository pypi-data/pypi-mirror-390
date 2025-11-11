import atexit
import os

import uyeia


def test_errors_config_creation():
    config = uyeia.Config(
        error_cache_location="./tests/errors_cache.db",
        error_config_location="./tests/uyeia.errors.json",
    )
    uyeia.set_global_config(config)
    watcher = uyeia.Watcher("test")
    watcher.release()
    assert os.path.exists("./tests/uyeia.errors.json")


def test_errors_cache_creation():
    config = uyeia.Config(
        error_cache_location="./tests/errors_cache.db",
        error_config_location="./tests/samples/uyeia.errors.json",
    )
    uyeia.set_global_config(config)
    watcher = uyeia.Watcher("test")
    watcher.register("T404")
    atexit._run_exitfuncs()
    assert os.path.exists("./tests/errors_cache.db")
