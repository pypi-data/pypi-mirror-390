import uyeia


def test_error_escalation(sample_config):
    sample_config.max_escalation = 1
    uyeia.set_global_config(sample_config)
    watcher = uyeia.Watcher("test")
    watcher.register("T404")

    uyeia.escalate()
    errors = uyeia.get_errors()
    assert errors and isinstance(errors, dict) and "test" in errors.get("RESCUE")  # type: ignore


def test_multi_errors_escalation(sample_config):
    sample_config.max_escalation = 1
    uyeia.set_global_config(sample_config)
    watcher1 = uyeia.Watcher("test1")
    watcher2 = uyeia.Watcher("test2")
    watcher3 = uyeia.Watcher("test3")
    watcher1.register("T404")
    watcher2.register("T405")
    watcher3.register("T501")

    uyeia.escalate()
    errors = uyeia.get_errors()
    assert errors and isinstance(errors, dict) and len(errors["RESCUE"]) == 3  # type: ignore
