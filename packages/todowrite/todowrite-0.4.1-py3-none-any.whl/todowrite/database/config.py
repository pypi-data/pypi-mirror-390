"""
This module contains the configuration for the database connection.

ToDoWrite uses a DATABASE-FIRST approach with cascading fallbacks:
1. PostgreSQL (preferred, especially via Docker)
2. SQLite3 (reliable fallback)
3. YAML files (last resort when databases are unavailable)

The system automatically tries each option in order until one works.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from enum import Enum
from typing import Any, cast

# Configuration cache
_storage_cache: dict[str, Any] = {}
_cache_timestamp: float = 0.0
_cache_ttl: float = 600.0  # 10 minutes cache


class StorageType(Enum):
    """Available storage types for ToDoWrite."""

    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    YAML = "yaml"


class StoragePreference(Enum):
    """Storage preference options."""

    AUTO = "auto"  # Use automatic fallback chain
    POSTGRESQL_ONLY = "postgresql_only"  # Only try PostgreSQL
    SQLITE_ONLY = "sqlite_only"  # Only try SQLite
    YAML_ONLY = "yaml_only"  # Only use YAML files


# Global storage preference - can be overridden
storage_preference: StoragePreference = StoragePreference.AUTO

# Explicit database URL override
DATABASE_URL: str = os.getenv(
    "TODOWRITE_DATABASE_URL",
    os.getenv("DATABASE_URL", ""),  # Check standard DATABASE_URL too
)
"""The URL for the database connection.

Environment Variables:
    TODOWRITE_DATABASE_URL: Full database URL (overrides automatic detection)
    DATABASE_URL: Standard database URL environment variable
    TODOWRITE_STORAGE_PREFERENCE: Storage preference (auto, pg, sqlite, yaml)

Examples:
    PostgreSQL: postgresql://user:password@localhost:5432/todowrite_db
    SQLite: sqlite:///todowrite.db
    YAML: yaml (uses YAML files instead of database)
"""


def set_storage_preference(preference: StoragePreference) -> None:
    """Set the global storage preference."""
    global storage_preference
    storage_preference = preference


def get_storage_preference() -> StoragePreference:
    """Get the current storage preference."""
    # Check environment variable first
    env_pref = os.getenv("TODOWRITE_STORAGE_PREFERENCE", "").lower()
    if env_pref:
        try:
            return StoragePreference(env_pref)
        except ValueError:
            pass

    return storage_preference


def test_postgresql_connection(url: str) -> bool:
    """Test if PostgreSQL connection is available."""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def test_sqlite_connection(url: str) -> bool:
    """Test if SQLite connection is available."""
    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_postgresql_candidates() -> list[str]:
    """Get list of potential PostgreSQL connection URLs to try."""
    candidates: list[str] = []

    # Explicit URL from environment
    if DATABASE_URL and DATABASE_URL.startswith("postgresql:"):
        candidates.append(DATABASE_URL)

    # Docker container detection
    docker_path = shutil.which("docker")
    if (
        docker_path
        and os.path.isabs(docker_path)
        and os.path.exists(docker_path)
    ):
        try:
            # Validate docker path is safe (absolute path and executable)
            docker_args = [
                docker_path,
                "ps",
                "--filter",
                "name=todowrite-postgres",
                "--format",
                "{{.Names}}",
            ]
            result = subprocess.run(
                docker_args,
                capture_output=True,
                text=True,
                timeout=5,
                shell=False,
            )
            if "todowrite-postgres" in result.stdout:
                candidates.append(
                    "postgresql://todowrite:todowrite_dev_password@localhost:5432/todowrite"
                )
        except (
            subprocess.TimeoutExpired,
            FileNotFoundError,
            subprocess.SubprocessError,
        ):
            pass

    # Standard localhost
    if not any("localhost" in url for url in candidates):
        candidates.append(
            "postgresql://todowrite:todowrite_dev_password@localhost:5432/todowrite"
        )

    return candidates


def get_sqlite_candidates() -> list[str]:
    """Get list of potential SQLite connection URLs to try."""
    candidates: list[str] = []

    # Explicit URL from environment
    if DATABASE_URL and DATABASE_URL.startswith("sqlite:"):
        candidates.append(DATABASE_URL)

    # Default SQLite locations
    default_paths = [
        "sqlite:///todowrite.db",
        "sqlite:///./data/todowrite.db",
        "sqlite:///~/.todowrite/todowrite.db",
    ]

    for path in default_paths:
        if path not in candidates:
            candidates.append(path)

    return candidates


def _clear_storage_cache() -> None:
    """Clear expired storage cache."""
    global _storage_cache, _cache_timestamp
    current_time = time.time()
    if current_time - _cache_timestamp > _cache_ttl:
        _storage_cache.clear()
        _cache_timestamp = float(current_time)


def determine_storage_backend() -> tuple[StorageType, str | None]:
    """
    Determine storage backend based on preference and availability.

    Returns:
        Tuple of (StorageType, connection_url_or_none)
    """
    # Check cache first
    _clear_storage_cache()
    cache_key = "determine_storage_backend"
    cached_result = _storage_cache.get(cache_key)
    if cached_result is not None:
        return cast("tuple[StorageType, str | None]", cached_result)

    preference = get_storage_preference()

    # Use a single result variable with proper typing from the start
    result: tuple[StorageType, str | None]

    if preference == StoragePreference.YAML_ONLY:
        result = StorageType.YAML, None
        _storage_cache[cache_key] = result
        return result

    elif preference == StoragePreference.POSTGRESQL_ONLY:
        for url in get_postgresql_candidates():
            if test_postgresql_connection(url):
                result = StorageType.POSTGRESQL, url
                _storage_cache[cache_key] = result
                return result
        raise RuntimeError("PostgreSQL requested but not available")

    elif preference == StoragePreference.SQLITE_ONLY:
        for url in get_sqlite_candidates():
            if test_sqlite_connection(url):
                result = StorageType.SQLITE, url
                _storage_cache[cache_key] = result
                return result
        raise RuntimeError("SQLite requested but not available")

    else:  # StoragePreference.AUTO
        # Try PostgreSQL first
        for url in get_postgresql_candidates():
            if test_postgresql_connection(url):
                result = StorageType.POSTGRESQL, url
                _storage_cache[cache_key] = result
                return result

        # Try SQLite second
        for url in get_sqlite_candidates():
            if test_sqlite_connection(url):
                result = StorageType.SQLITE, url
                _storage_cache[cache_key] = result
                return result

        # Fall back to YAML
        result = StorageType.YAML, None

        # Cache the result
        _storage_cache[cache_key] = result
        return result


def get_storage_info() -> dict[str, str]:
    """Get information about the current storage configuration."""
    try:
        storage_type, url = determine_storage_backend()
        preference = get_storage_preference()

        if storage_type == StorageType.POSTGRESQL:
            return {
                "type": "PostgreSQL",
                "url": url or "",
                "priority": "1 (Preferred)",
                "fallback": "No",
                "preference": preference.value,
            }
        elif storage_type == StorageType.SQLITE:
            return {
                "type": "SQLite",
                "url": url or "",
                "priority": "2 (Database Fallback)",
                "fallback": "Yes",
                "preference": preference.value,
            }
        else:  # YAML
            return {
                "type": "YAML Files",
                "url": "configs/ directory",
                "priority": "3 (Last Resort)",
                "fallback": "Yes",
                "preference": preference.value,
            }
    except Exception as e:
        return {
            "type": "Error",
            "url": f"Error: {e}",
            "priority": "Unknown",
            "fallback": "Unknown",
            "preference": get_storage_preference().value,
        }


def get_setup_guidance() -> str:
    """Provide setup guidance for storage configuration."""
    info = get_storage_info()

    if info["type"] == "PostgreSQL":
        return """
✅ PostgreSQL detected (preferred storage)
   No additional setup needed.
        """.strip()

    elif info["type"] == "SQLite":
        return """
📋 SQLite detected (database fallback)

   To use PostgreSQL (recommended):
   1. Run: cd tests && docker-compose up -d postgres
   2. Optional: export TODOWRITE_DATABASE_URL=postgresql://todowrite:todowrite_dev_password@localhost:5432/todowrite
   3. Restart application (will auto-detect PostgreSQL)
        """.strip()

    elif info["type"] == "YAML Files":
        return """
📄 YAML files mode (last resort fallback)
   Database connections failed, using YAML files for storage.

   To use database storage:
   1. For PostgreSQL: cd tests && docker-compose up -d postgres
   2. For SQLite: Ensure write permissions in current directory
   3. Check: python -m todowrite db-status
        """.strip()

    else:
        return """
❌ Storage configuration error

   To resolve:
   1. Try: cd tests && docker-compose up -d postgres (PostgreSQL)
   2. Or: ensure current directory is writable (SQLite)
   3. Or: set TODOWRITE_STORAGE_PREFERENCE=yaml_only (YAML fallback)
        """.strip()


# Legacy compatibility functions
def get_postgresql_url(
    user: str,
    password: str,
    host: str = "localhost",
    port: int = 5432,
    database: str = "todowrite",
) -> str:
    """Generate PostgreSQL connection URL."""
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def is_sqlite() -> bool:
    """Check if current configuration uses SQLite."""
    storage_type, _ = determine_storage_backend()
    return storage_type == StorageType.SQLITE


def is_postgresql() -> bool:
    """Check if current configuration uses PostgreSQL."""
    storage_type, _ = determine_storage_backend()
    return storage_type == StorageType.POSTGRESQL


def is_yaml() -> bool:
    """Check if current configuration uses YAML files."""
    storage_type, _ = determine_storage_backend()
    return storage_type == StorageType.YAML
