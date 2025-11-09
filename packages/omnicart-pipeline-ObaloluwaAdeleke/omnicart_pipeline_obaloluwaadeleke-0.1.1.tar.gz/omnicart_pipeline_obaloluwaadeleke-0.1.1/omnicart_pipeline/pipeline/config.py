# omnicart_pipeline/pipeline/config.py
import configparser
from importlib import resources
from typing import Optional

class ConfigManager:
    def __init__(self, config_path: Optional[str] = None, package: str = "omnicart_pipeline", config_name: str = "pipeline.cfg"):
        """
        If config_path is provided, read from that path (useful in dev/tests).
        Otherwise read pipeline.cfg from the package resources (works after installation).
        """
        self.config = configparser.ConfigParser()
        if config_path:
            # dev/test: read from provided path
            self.config.read(config_path)
        else:
            # production/install: read the file from the package resources (works across installs)
            text = resources.files(package).joinpath(config_name).read_text(encoding="utf-8")
            self.config.read_string(text)

    def get(self, section: str, key: str):
        # Only consider explicit sections (not DEFAULT)
        if section not in self.config.sections():
            raise KeyError(f"Section '{section}' not found in config (sections: {self.config.sections()}).")
        if not self.config.has_option(section, key):
            raise KeyError(f"Key '{key}' not found in section '{section}'.")
        return self.config.get(section, key)

    @property
    def base_url(self) -> str:
        return self.get("API", "base_url")

    @property
    def limit(self) -> int:
        return int(self.get("API", "limit"))
