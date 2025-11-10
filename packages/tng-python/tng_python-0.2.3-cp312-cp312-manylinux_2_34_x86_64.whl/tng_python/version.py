from functools import lru_cache
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # fallback for older Python versions


@lru_cache
def _get_version():
    """Get version from package metadata or fallback."""
    try:
        # Try to get version from installed package metadata
        import importlib.metadata
        return importlib.metadata.version("tng-python")
    except Exception:
        # Fallback for development
        try:
            pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
            return data["project"]["version"]
        except Exception:
            return "0.2.3"  # current version fallback


__version__ = _get_version()
