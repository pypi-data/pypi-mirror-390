import uyeia


def test_errors_register(sample_config):
    uyeia.set_global_config(sample_config)
    watcher = uyeia.Watcher("test")
    watcher.register("T404")

    errors = uyeia.get_errors()
    assert errors and isinstance(errors, dict) and "test" in errors.get("WARNING")  # type: ignore


def test_errors_register_custom_message(sample_config):
    uyeia.set_global_config(sample_config)
    watcher = uyeia.Watcher("test")
    watcher.register("T404", "custom_message")

    errors = uyeia.get_errors()
    assert errors and isinstance(errors, dict) and "test" in errors.get("WARNING")  # type: ignore
    my_errors = errors["WARNING"]["test"]
    assert "custom_message" in my_errors["message"]


def test_errors_register_custom_message_replace_var(sample_config):
    uyeia.set_global_config(sample_config)
    watcher = uyeia.Watcher("test")
    watcher.register("T404", "custom_message {{VAR}}", {"VAR": "OK"})

    errors = uyeia.get_errors()
    assert errors and isinstance(errors, dict) and "test" in errors.get("WARNING")  # type: ignore
    my_errors = errors["WARNING"]["test"]
    assert "custom_message" in my_errors["message"] and "OK" in my_errors["message"]


def test_high_errors_register(sample_config):
    uyeia.set_global_config(sample_config)
    watcher1 = uyeia.Watcher("test")
    watcher2 = uyeia.Watcher("test2")
    watcher1.register("T404")
    watcher2.register("T405")

    error = uyeia.get_errors("hot")
    assert error and error["status"] == "WARNING"


def test_low_errors_register(sample_config):
    uyeia.set_global_config(sample_config)
    watcher1 = uyeia.Watcher("test")
    watcher2 = uyeia.Watcher("test2")
    watcher1.register("T404")
    watcher2.register("T405")

    error = uyeia.get_errors("cold")
    assert error and error["status"] == "LIMITED"


def test_errors_override(sample_config):
    uyeia.set_global_config(sample_config)
    watcher1 = uyeia.Watcher("test")
    watcher2 = uyeia.Watcher("test2")
    watcher1.register("T404")
    watcher2.register("T405")
    watcher2.register("T501")

    errors = uyeia.get_errors()
    assert errors and isinstance(errors, dict) and len(errors["LIMITED"]) == 1  # type: ignore


def test_errors_same_level(sample_config):
    uyeia.set_global_config(sample_config)
    watcher1 = uyeia.Watcher("test1")
    watcher2 = uyeia.Watcher("test2")
    watcher1.register("T405")
    watcher2.register("T501")

    errors = uyeia.get_errors()
    assert errors and isinstance(errors, dict) and len(errors["LIMITED"]) == 2  # type: ignore


def test_errors_override_status(sample_config):
    uyeia.set_global_config(sample_config)
    watcher1 = uyeia.Watcher("test")
    watcher1.register("T501")
    error = uyeia.get_errors("hot")
    assert error and error["status"] == "LIMITED"
    watcher1.register("T404")
    error = uyeia.get_errors("hot")
    assert error and error["status"] == "WARNING"
    assert len(uyeia.get_errors()) == 1
