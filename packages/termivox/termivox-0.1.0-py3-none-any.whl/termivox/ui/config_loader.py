"""
Configuration loader for Termivox settings.

Loads and validates settings.json configuration file.

♠️ Nyro: Configuration structure - centralized control
🎸 JamAI: Load the settings, tune the interfaces
🌿 Aureon: Flexible configuration for every user's need
"""

import json
import os
from typing import Dict, Any


class ConfigLoader:
    """
    Load and validate Termivox configuration.

    Example:
        config = ConfigLoader.load()
        hotkey_enabled = config['interfaces']['hotkey']['enabled']
    """

    DEFAULT_CONFIG = {
        "interfaces": {
            "hotkey": {
                "enabled": True,
                "key": "ctrl+alt+v"
            },
            "tray": {
                "enabled": True
            },
            "widget": {
                "enabled": False,
                "position": {"x": 100, "y": 100},
                "size": {"width": 200, "height": 100},
                "always_on_top": True
            },
            "hardware": {
                "enabled": False,
                "device": None,
                "device_type": "usb"
            }
        },
        "voice": {
            "language": "en",
            "auto_space": True
        },
        "audio_feedback": False
    }

    @staticmethod
    def load(config_path="config/settings.json") -> Dict[str, Any]:
        """
        Load configuration from file or return defaults.

        Args:
            config_path: Path to settings.json

        Returns:
            Configuration dictionary
        """
        # Try to load from file
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                print(f"[Config] Loaded from {config_path}")
                return ConfigLoader._merge_with_defaults(config)
            except Exception as e:
                print(f"[Config] Error loading {config_path}: {e}")
                print("[Config] Using default configuration")
                return ConfigLoader.DEFAULT_CONFIG.copy()
        else:
            print(f"[Config] File not found: {config_path}")
            print("[Config] Using default configuration")
            return ConfigLoader.DEFAULT_CONFIG.copy()

    @staticmethod
    def _merge_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge loaded config with defaults (fill in missing keys).

        Args:
            config: Loaded configuration

        Returns:
            Merged configuration
        """
        def deep_merge(default, override):
            """Recursively merge dictionaries."""
            result = default.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(ConfigLoader.DEFAULT_CONFIG, config)

    @staticmethod
    def save(config: Dict[str, Any], config_path="config/settings.json"):
        """
        Save configuration to file.

        Args:
            config: Configuration dictionary
            config_path: Path to settings.json
        """
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"[Config] Saved to {config_path}")
        except Exception as e:
            print(f"[Config] Error saving: {e}")
