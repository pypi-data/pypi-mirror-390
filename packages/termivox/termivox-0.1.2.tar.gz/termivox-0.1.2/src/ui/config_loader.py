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
from pathlib import Path


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
    def load(config_path=None) -> Dict[str, Any]:
        """
        Load configuration from file or return defaults.

        Args:
            config_path: Path to settings.json (optional)

        Returns:
            Configuration dictionary
        """
        # Search locations in priority order
        search_paths = []

        # 1. User-specified path (if provided)
        if config_path:
            search_paths.append(Path(config_path))

        # 2. User config directory (~/.termivox/settings.json)
        user_config = Path.home() / ".termivox" / "settings.json"
        search_paths.append(user_config)

        # 3. Current working directory
        search_paths.append(Path("config/settings.json"))

        # 4. Package bundled config
        try:
            package_dir = Path(__file__).parent.parent.parent
            bundled_config = package_dir / "config" / "settings.json"
            search_paths.append(bundled_config)
        except:
            pass

        # Try to load from each location
        for path in search_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        config = json.load(f)
                    print(f"[Config] Loaded from {path}")
                    return ConfigLoader._merge_with_defaults(config)
                except Exception as e:
                    print(f"[Config] Error loading {path}: {e}")
                    continue

        print("[Config] No config file found, using defaults")
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
