from pathlib import Path
import yaml
import os

class HumalabConfig:
    """Manages HumaLab SDK configuration settings.

    Configuration is stored in ~/.humalab/config.yaml and includes workspace path,
    API credentials, and connection settings. Values are automatically loaded on
    initialization and saved when modified through property setters.

    Attributes:
        workspace_path (str): The local workspace directory path.
        base_url (str): The HumaLab API base URL.
        api_key (str): The API key for authentication.
        timeout (float): Request timeout in seconds.
    """
    def __init__(self):
        self._config = {
            "workspace_path": "",
            "base_url": "",
            "api_key": "",
            "timeout": 30.0,
        }
        self._workspace_path = ""
        self._base_url = ""
        self._api_key = ""
        self._timeout = 30.0
        self._load_config()

    def _load_config(self):
        """Load configuration from ~/.humalab/config.yaml."""
        home_path = Path.home()
        config_path = home_path / ".humalab" / "config.yaml"
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.touch()
        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f) or {}
        self._workspace_path = os.path.expanduser(self._config["workspace_path"]) if self._config and "workspace_path" in self._config else home_path
        self._base_url = self._config["base_url"] if self._config and "base_url" in self._config else ""
        self._api_key = self._config["api_key"] if self._config and "api_key" in self._config else ""
        self._timeout = self._config["timeout"] if self._config and "timeout" in self._config else 30.0

    def _save(self) -> None:
        """Save current configuration to ~/.humalab/config.yaml."""
        yaml.dump(self._config, open(Path.home() / ".humalab" / "config.yaml", "w"))

    @property
    def workspace_path(self) -> str:
        """The local workspace directory path.

        Returns:
            str: The workspace path.
        """
        return str(self._workspace_path)
    
    @workspace_path.setter
    def workspace_path(self, path: str) -> None:
        self._workspace_path = path
        self._config["workspace_path"] = path
        self._save()

    @property
    def base_url(self) -> str:
        """The HumaLab API base URL.

        Returns:
            str: The base URL.
        """
        return str(self._base_url)

    @base_url.setter
    def base_url(self, base_url: str) -> None:
        """Set the HumaLab API base URL and save to config.

        Args:
            base_url (str): The new base URL.
        """
        self._base_url = base_url
        self._config["base_url"] = base_url
        self._save()

    @property
    def api_key(self) -> str:
        """The API key for authentication.

        Returns:
            str: The API key.
        """
        return str(self._api_key)

    @api_key.setter
    def api_key(self, api_key: str) -> None:
        """Set the API key and save to config.

        Args:
            api_key (str): The new API key.
        """
        self._api_key = api_key
        self._config["api_key"] = api_key
        self._save()

    @property
    def timeout(self) -> float:
        """Request timeout in seconds.

        Returns:
            float: The timeout value.
        """
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: float) -> None:
        """Set the request timeout and save to config.

        Args:
            timeout (float): The new timeout in seconds.
        """
        self._timeout = timeout
        self._config["timeout"] = timeout
        self._save()