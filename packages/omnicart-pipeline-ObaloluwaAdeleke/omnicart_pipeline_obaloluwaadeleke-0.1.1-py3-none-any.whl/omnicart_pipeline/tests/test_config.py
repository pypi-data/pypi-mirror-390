import pytest
from omnicart_pipeline.pipeline.config import ConfigManager

def test_config_manager_reads_values(tmp_path):
    config_text = """
    [API]
    base_url = https://example.com
    limit = 50
    """
    config_file = tmp_path / "test.cfg"
    config_file.write_text(config_text)
    cm = ConfigManager(config_path=str(config_file))
    assert cm.base_url == "https://example.com"
    assert cm.limit == 50

def test_config_manager_missing_section(tmp_path):
    config_text = """
    [OTHER]
    some_key = value
    """
    config_file = tmp_path / "missing.cfg"
    config_file.write_text(config_text)
    cm = ConfigManager(config_path=str(config_file))
    with pytest.raises(KeyError):
        cm.get("NON_EXISTENT", "key")

def test_config_reads_from_path(tmp_path):
    config_text = """
    [API]
    base_url = https://localtest.com
    limit = 10
    """
    config_file = tmp_path / "path.cfg"
    config_file.write_text(config_text)
    cm = ConfigManager(config_path=str(config_file))
    assert "https://" in cm.base_url
    assert isinstance(cm.limit, int)

def test_config_reads_from_package_resource():
    """
    Verifies ConfigManager can read the default config from the package
    and raises KeyError for missing sections.
    """
    cm = ConfigManager(config_path=None, package="omnicart_pipeline", config_name="pipeline.cfg")
    
    # Check that base config loads fine
    assert "https://" in cm.base_url
    assert isinstance(cm.limit, int)

    # Now deliberately test a missing section to raise KeyError
    with pytest.raises(KeyError):
        cm.get("NON_EXISTENT_SECTION", "fake_key")
