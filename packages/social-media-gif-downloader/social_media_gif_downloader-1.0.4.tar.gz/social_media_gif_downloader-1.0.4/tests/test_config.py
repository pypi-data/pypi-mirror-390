"""Tests for configuration management."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from config import Config


class TestConfig:
    """Test suite for Config class."""

    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """Create a temporary directory for config files."""
        return tmp_path

    @pytest.fixture
    def mock_home(self, temp_config_dir, monkeypatch):
        """Mock the home directory to use a temporary directory."""
        monkeypatch.setattr(Path, "home", lambda: temp_config_dir)
        return temp_config_dir

    def test_config_initialization_creates_default_file(self, mock_home):
        """Test that Config creates a default config file if it doesn't exist."""
        config = Config()
        
        config_file = mock_home / Config.CONFIG_FILENAME
        assert config_file.exists()
        
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        assert data == Config.DEFAULT_SETTINGS

    def test_config_loads_existing_file(self, mock_home):
        """Test that Config loads an existing config file."""
        config_file = mock_home / Config.CONFIG_FILENAME
        test_settings = {
            "default_save_location": "/test/path",
            "preferred_output_format": "mp4",
            "fps_settings": 30
        }
        
        with open(config_file, 'w') as f:
            json.dump(test_settings, f)
        
        config = Config()
        
        assert config.get_default_save_location() == "/test/path"
        assert config.get_preferred_output_format() == "mp4"
        assert config.get_fps_settings() == 30

    def test_config_merges_partial_settings(self, mock_home):
        """Test that Config merges partial settings with defaults."""
        config_file = mock_home / Config.CONFIG_FILENAME
        partial_settings = {
            "preferred_output_format": "mp4"
        }
        
        with open(config_file, 'w') as f:
            json.dump(partial_settings, f)
        
        config = Config()
        
        assert config.get_default_save_location() == ""
        assert config.get_preferred_output_format() == "mp4"
        assert config.get_fps_settings() == 15

    def test_set_default_save_location(self, mock_home):
        """Test setting default save location."""
        config = Config()
        config.set_default_save_location("/new/path")
        
        assert config.get_default_save_location() == "/new/path"
        
        # Verify it's saved to disk
        config_file = mock_home / Config.CONFIG_FILENAME
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        assert data["default_save_location"] == "/new/path"

    def test_set_preferred_output_format_valid(self, mock_home):
        """Test setting valid output format."""
        config = Config()
        
        config.set_preferred_output_format("mp4")
        assert config.get_preferred_output_format() == "mp4"
        
        config.set_preferred_output_format("gif")
        assert config.get_preferred_output_format() == "gif"

    def test_set_preferred_output_format_invalid(self, mock_home):
        """Test setting invalid output format defaults to 'gif'."""
        config = Config()
        config.set_preferred_output_format("invalid")
        
        assert config.get_preferred_output_format() == "gif"

    def test_set_fps_settings_valid(self, mock_home):
        """Test setting valid FPS."""
        config = Config()
        
        config.set_fps_settings(30)
        assert config.get_fps_settings() == 30
        
        config.set_fps_settings(1)
        assert config.get_fps_settings() == 1
        
        config.set_fps_settings(60)
        assert config.get_fps_settings() == 60

    def test_set_fps_settings_clamped(self, mock_home):
        """Test that FPS is clamped to valid range."""
        config = Config()
        
        config.set_fps_settings(0)
        assert config.get_fps_settings() == 1
        
        config.set_fps_settings(-10)
        assert config.get_fps_settings() == 1
        
        config.set_fps_settings(100)
        assert config.get_fps_settings() == 60

    def test_get_with_default(self, mock_home):
        """Test getting a value with a default."""
        config = Config()
        
        assert config.get("nonexistent_key", "default_value") == "default_value"
        assert config.get("fps_settings", 99) == 15

    def test_set_generic(self, mock_home):
        """Test setting a generic key-value pair."""
        config = Config()
        config.set("custom_key", "custom_value")
        
        assert config.get("custom_key") == "custom_value"

    def test_config_handles_corrupted_file(self, mock_home):
        """Test that Config handles corrupted JSON file gracefully."""
        config_file = mock_home / Config.CONFIG_FILENAME
        
        with open(config_file, 'w') as f:
            f.write("{ invalid json }")
        
        config = Config()
        
        assert config.settings == Config.DEFAULT_SETTINGS

    def test_config_persistence(self, mock_home):
        """Test that changes persist across Config instances."""
        config1 = Config()
        config1.set_default_save_location("/test/path")
        config1.set_preferred_output_format("mp4")
        config1.set_fps_settings(25)
        
        config2 = Config()
        
        assert config2.get_default_save_location() == "/test/path"
        assert config2.get_preferred_output_format() == "mp4"
        assert config2.get_fps_settings() == 25
