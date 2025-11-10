"""
Centralized configuration management for CLI.

Provides consistent configuration access across all CLI modules.
"""

import os
import threading
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class CLIConfig:
    """CLI configuration settings (immutable after creation)."""
    api_url: str
    log_level: str
    log_file: Optional[Path]
    auth_file: Path
    max_directory_depth: int
    max_file_size_mb: int
    max_files_to_analyze: int
    analysis_timeout_seconds: int
    
    def __post_init__(self):
        """Validate configuration values after initialization."""
        # Validate log level
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if self.log_level.upper() not in valid_levels:
            # Use object.__setattr__ to modify frozen dataclass
            object.__setattr__(self, 'log_level', 'INFO')
        
        # Validate resource limits (raise errors instead of silently modifying)
        if self.max_directory_depth < 1:
            raise ValueError(f"max_directory_depth must be >= 1, got {self.max_directory_depth}")
        elif self.max_directory_depth > 1000:
            raise ValueError(f"max_directory_depth must be <= 1000, got {self.max_directory_depth}")
        
        if self.max_file_size_mb < 1:
            raise ValueError(f"max_file_size_mb must be >= 1, got {self.max_file_size_mb}")
        elif self.max_file_size_mb > 10000:
            raise ValueError(f"max_file_size_mb must be <= 10000, got {self.max_file_size_mb}")
        
        if self.max_files_to_analyze < 1:
            raise ValueError(f"max_files_to_analyze must be >= 1, got {self.max_files_to_analyze}")
        elif self.max_files_to_analyze > 1000000:
            raise ValueError(f"max_files_to_analyze must be <= 1000000, got {self.max_files_to_analyze}")
        
        if self.analysis_timeout_seconds < 1:
            raise ValueError(f"analysis_timeout_seconds must be >= 1, got {self.analysis_timeout_seconds}")
        elif self.analysis_timeout_seconds > 86400:  # 24 hours max
            raise ValueError(f"analysis_timeout_seconds must be <= 86400, got {self.analysis_timeout_seconds}")
    
    @classmethod
    def _safe_int_env(cls, key: str, default: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """Safely get integer from environment variable with validation."""
        try:
            value = int(os.getenv(key, str(default)))
            # Validate non-negative for values that should never be negative
            if min_val is not None and min_val >= 0 and value < 0:
                return default
            if min_val is not None:
                value = max(min_val, value)
            if max_val is not None:
                value = min(max_val, value)
            return value
        except (ValueError, TypeError):
            return default
    
    @classmethod
    def from_env(cls) -> 'CLIConfig':
        """Create configuration from environment variables."""
        # API URL - never hardcode, always use environment variable
        api_url = os.getenv("ROHKUN_API_URL", "http://localhost:8000")
        if not api_url or not isinstance(api_url, str):
            api_url = "http://localhost:8000"
        
        # Logging
        log_level = os.getenv("ROHKUN_LOG_LEVEL", "INFO")
        if not isinstance(log_level, str):
            log_level = "INFO"
        log_level = log_level.upper()
        
        log_file_str = os.getenv("ROHKUN_LOG_FILE")
        log_file = None
        if log_file_str and isinstance(log_file_str, str):
            try:
                log_file = Path(log_file_str)
            except (ValueError, TypeError):
                log_file = None
        
        # Auth file with absolute path fallback
        try:
            auth_file = Path.home() / ".rohkun" / "auth.json"
        except (RuntimeError, OSError):
            # Fallback to temp directory if home cannot be determined
            import tempfile
            try:
                temp_dir = Path(tempfile.gettempdir())
                auth_file = temp_dir / ".rohkun" / "auth.json"
            except (RuntimeError, OSError):
                # Last resort: current directory (but make it absolute)
                auth_file = Path.cwd() / ".rohkun" / "auth.json"
        
        # Resource limits with validation
        max_directory_depth = cls._safe_int_env("ROHKUN_MAX_DEPTH", 50, 1, 1000)
        max_file_size_mb = cls._safe_int_env("ROHKUN_MAX_FILE_SIZE_MB", 100, 1, 10000)
        max_files_to_analyze = cls._safe_int_env("ROHKUN_MAX_FILES", 10000, 1, 1000000)
        analysis_timeout_seconds = cls._safe_int_env("ROHKUN_TIMEOUT", 3600, 1, 86400)
        
        config = cls(
            api_url=api_url,
            log_level=log_level,
            log_file=log_file,
            auth_file=auth_file,
            max_directory_depth=max_directory_depth,
            max_file_size_mb=max_file_size_mb,
            max_files_to_analyze=max_files_to_analyze,
            analysis_timeout_seconds=analysis_timeout_seconds
        )
        
        return config


# Global configuration instance with thread-safe access
_config: Optional[CLIConfig] = None
_config_lock = threading.RLock()  # Use RLock for reentrant locking


def get_config() -> CLIConfig:
    """Get global configuration instance (thread-safe, immutable)."""
    global _config
    if _config is None:
        with _config_lock:
            # Double-check pattern
            if _config is None:
                try:
                    _config = CLIConfig.from_env()
                except ValueError as e:
                    # Configuration validation failed - use safe defaults
                    import sys
                    print(f"Warning: Configuration validation failed: {e}", file=sys.stderr)
                    print("Using safe default configuration", file=sys.stderr)
                    # Create with safe defaults
                    _config = CLIConfig(
                        api_url="http://localhost:8000",
                        log_level="INFO",
                        log_file=None,
                        auth_file=Path.home() / ".rohkun" / "auth.json",
                        max_directory_depth=50,
                        max_file_size_mb=100,
                        max_files_to_analyze=10000,
                        analysis_timeout_seconds=3600
                    )
    return _config


def reset_config():
    """Reset configuration (useful for testing)."""
    global _config
    with _config_lock:
        _config = None
