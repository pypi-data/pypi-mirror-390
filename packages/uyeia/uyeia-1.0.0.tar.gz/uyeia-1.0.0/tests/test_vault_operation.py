import uyeia


def test_put_vault(sample_config):
    uyeia.set_global_config(sample_config)
    vault = uyeia.Vault()
    vault.set("test_key", "test_value")
    value = vault.get("test_key")
    assert value == "test_value"


def test_modify_vault(sample_config):
    uyeia.set_global_config(sample_config)
    vault = uyeia.Vault()
    vault.set("test_key", "init_value")
    vault.set("test_key", "new_test_value")
    value = vault.get("test_key")
    assert value == "new_test_value"


def test_remove_vault(sample_config):
    uyeia.set_global_config(sample_config)
    vault = uyeia.Vault()
    vault.set("test_key", "test_value")
    vault.remove("test_key")
    value = vault.get("test_key")
    assert value is None
