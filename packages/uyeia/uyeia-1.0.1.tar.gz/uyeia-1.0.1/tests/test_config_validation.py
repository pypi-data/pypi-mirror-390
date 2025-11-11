import pytest

import uyeia


def test_global_config_unknow_logging_level_int():
    config = uyeia.Config(
        status={
            "HEALTHY": -1,
        }
    )

    with pytest.raises(uyeia.UYEIAConfigError):
        uyeia.set_global_config(config)


def test_global_config_unknow_logging_level_str():
    config = uyeia.Config(
        status={
            "HEALTHY": "test",
        }
    )

    with pytest.raises(uyeia.UYEIAConfigError):
        uyeia.set_global_config(config)
