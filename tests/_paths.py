from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = REPO_ROOT / "plugins" / "codex-notepad-librarian"

sys.path.insert(0, str(PLUGIN_ROOT))
