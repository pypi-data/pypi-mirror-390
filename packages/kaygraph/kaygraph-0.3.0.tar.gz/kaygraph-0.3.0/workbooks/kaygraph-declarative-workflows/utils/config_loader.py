"""
Configuration loading utilities for declarative workflows.

Supports loading workflow configurations from TOML, YAML, and JSON files.
"""

import os
import json
from typing import Any, Dict, Optional, Union
from pathlib import Path

try:
    import toml
    HAS_TOML = True
except ImportError:
    HAS_TOML = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class ConfigLoader:
    """
    Utility class for loading configuration files in various formats.
    """

    SUPPORTED_FORMATS = ["toml", "yaml", "yml", "json"]

    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize config loader.

        Args:
            base_path: Base directory for relative config paths
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def load(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            Loaded configuration as dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config format is not supported
            ImportError: If required parser is not installed
        """
        config_path = Path(config_path)

        # Handle relative paths
        if not config_path.is_absolute():
            config_path = self.base_path / config_path

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        # Determine format from file extension
        suffix = config_path.suffix.lower().lstrip('.')
        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported config format: {suffix}")

        # Load based on format
        if suffix == "toml":
            if not HAS_TOML:
                raise ImportError("toml package is required for TOML files. Install with: pip install toml")
            return self._load_toml(config_path)
        elif suffix in ["yaml", "yml"]:
            if not HAS_YAML:
                raise ImportError("PyYAML package is required for YAML files. Install with: pip install pyyaml")
            return self._load_yaml(config_path)
        elif suffix == "json":
            return self._load_json(config_path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")

    def _load_toml(self, config_path: Path) -> Dict[str, Any]:
        """Load TOML configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except Exception as e:
            raise ValueError(f"Error loading TOML file {config_path}: {e}")

    def _load_yaml(self, config_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ValueError(f"Error loading YAML file {config_path}: {e}")

    def _load_json(self, config_path: Path) -> Dict[str, Any]:
        """Load JSON configuration file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Error loading JSON file {config_path}: {e}")

    def save(self, config: Dict[str, Any], config_path: Union[str, Path], format: Optional[str] = None) -> None:
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary to save
            config_path: Path where to save the file
            format: File format ('toml', 'yaml', 'json'), inferred from extension if not provided
        """
        config_path = Path(config_path)

        # Handle relative paths
        if not config_path.is_absolute():
            config_path = self.base_path / config_path

        # Create directory if it doesn't exist
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Determine format
        if format is None:
            suffix = config_path.suffix.lower().lstrip('.')
            if suffix not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Cannot determine format from extension: {suffix}")
            format = suffix

        # Save based on format
        if format == "toml":
            if not HAS_TOML:
                raise ImportError("toml package is required for TOML files")
            self._save_toml(config, config_path)
        elif format in ["yaml", "yml"]:
            if not HAS_YAML:
                raise ImportError("PyYAML package is required for YAML files")
            self._save_yaml(config, config_path)
        elif format == "json":
            self._save_json(config, config_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _save_toml(self, config: Dict[str, Any], config_path: Path) -> None:
        """Save configuration as TOML."""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                toml.dump(config, f)
        except Exception as e:
            raise ValueError(f"Error saving TOML file {config_path}: {e}")

    def _save_yaml(self, config: Dict[str, Any], config_path: Path) -> None:
        """Save configuration as YAML."""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise ValueError(f"Error saving YAML file {config_path}: {e}")

    def _save_json(self, config: Dict[str, Any], config_path: Path) -> None:
        """Save configuration as JSON."""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Error saving JSON file {config_path}: {e}")

    def merge(self, *config_paths: Union[str, Path]) -> Dict[str, Any]:
        """
        Merge multiple configuration files.

        Later files override earlier files for overlapping keys.

        Args:
            *config_paths: Paths to configuration files to merge

        Returns:
            Merged configuration dictionary
        """
        merged_config = {}

        for config_path in config_paths:
            config = self.load(config_path)
            merged_config = self._deep_merge(merged_config, config)

        return merged_config

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def validate_schema(self, config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """
        Validate configuration against a schema.

        This is a simple validation. For complex validation, consider using jsonschema.

        Args:
            config: Configuration to validate
            schema: Schema definition

        Returns:
            True if valid, False otherwise
        """
        # Simple validation - check required keys exist
        for key, definition in schema.items():
            if definition.get("required", False) and key not in config:
                return False

            # Type validation
            if key in config and "type" in definition:
                expected_type = definition["type"]
                if expected_type == "dict" and not isinstance(config[key], dict):
                    return False
                elif expected_type == "list" and not isinstance(config[key], list):
                    return False
                elif expected_type == "str" and not isinstance(config[key], str):
                    return False
                elif expected_type == "int" and not isinstance(config[key], int):
                    return False
                elif expected_type == "float" and not isinstance(config[key], (int, float)):
                    return False
                elif expected_type == "bool" and not isinstance(config[key], bool):
                    return False

        return True

    def interpolate_env_vars(self, config: Any) -> Any:
        """
        Interpolate environment variables in configuration values.

        Supports ${VAR_NAME} and ${VAR_NAME:default_value} syntax.

        Args:
            config: Configuration to process

        Returns:
            Configuration with environment variables interpolated
        """
        if isinstance(config, dict):
            return {key: self.interpolate_env_vars(value) for key, value in config.items()}
        elif isinstance(config, list):
            return [self.interpolate_env_vars(item) for item in config]
        elif isinstance(config, str):
            return self._interpolate_string(config)
        else:
            return config

    def _interpolate_string(self, value: str) -> str:
        """Interpolate environment variables in a string."""
        import re

        def replace_match(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) is not None else ""
            return os.getenv(var_name, default_value)

        # Pattern: ${VAR_NAME} or ${VAR_NAME:default}
        pattern = r'\$\{([^}:}]+)(?::([^}]*))?\}'
        return re.sub(pattern, replace_match, value)


# Global config loader instance
_default_loader = ConfigLoader()


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load configuration using default loader.

    Args:
        config_path: Path to configuration file

    Returns:
        Loaded configuration dictionary
    """
    return _default_loader.load(config_path)


def save_config(config: Dict[str, Any], config_path: Union[str, Path], format: Optional[str] = None) -> None:
    """
    Save configuration using default loader.

    Args:
        config: Configuration to save
        config_path: Path where to save
        format: File format
    """
    _default_loader.save(config, config_path, format)


def merge_configs(*config_paths: Union[str, Path]) -> Dict[str, Any]:
    """
    Merge multiple configuration files using default loader.

    Args:
        *config_paths: Paths to configuration files

    Returns:
        Merged configuration dictionary
    """
    return _default_loader.merge(*config_paths)


def set_base_path(base_path: Union[str, Path]) -> None:
    """
    Set the base path for the default loader.

    Args:
        base_path: New base path
    """
    global _default_loader
    _default_loader = ConfigLoader(base_path)


if __name__ == "__main__":
    # Test the config loader
    print("Testing configuration loader...")

    # Create a test config
    test_config = {
        "workflow": {
            "name": "test_workflow",
            "description": "Test workflow for validation"
        },
        "nodes": {
            "processor": {
                "type": "llm",
                "model": "meta-llama/Llama-3.3-70B-Instruct"
            }
        }
    }

    # Save as different formats
    print("Saving test configurations...")

    if HAS_TOML:
        save_config(test_config, "test_config.toml")
        print("✅ Saved TOML config")

    if HAS_YAML:
        save_config(test_config, "test_config.yaml")
        print("✅ Saved YAML config")

    save_config(test_config, "test_config.json")
    print("✅ Saved JSON config")

    # Test loading
    print("\nTesting configuration loading...")

    try:
        loaded = load_config("test_config.json")
        print(f"✅ Loaded JSON config: {loaded['workflow']['name']}")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")

    # Clean up
    for file in ["test_config.toml", "test_config.yaml", "test_config.json"]:
        if Path(file).exists():
            Path(file).unlink()