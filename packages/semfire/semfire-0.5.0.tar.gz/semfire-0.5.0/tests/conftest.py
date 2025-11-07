import os
import sys
from pathlib import Path


def pytest_sessionstart(session):  # noqa: D401
    """Set a workspace-local SemFire config path for tests.

    This avoids sandbox write issues to user home (e.g., ~/.semfire) and keeps
    tests hermetic. Provider tests and helpers will resolve to this path.
    """
    # Ensure repo root and src are importable for tests
    repo_root = Path(__file__).resolve().parent.parent
    src_dir = repo_root / "src"
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    if src_dir.is_dir() and str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    # Use workspace-local SemFire config path for hermetic tests
    test_cfg = os.path.join(os.getcwd(), ".semfire_test", "config.json")
    os.environ.setdefault("SEMFIRE_CONFIG", test_cfg)
    # Ensure parent exists for any direct file ops
    os.makedirs(os.path.dirname(test_cfg), exist_ok=True)
