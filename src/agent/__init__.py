import importlib.util
from pathlib import Path

_AGENT_PATH = Path(__file__).resolve().parents[1] / "agent.py"

_spec = importlib.util.spec_from_file_location("agent_core_runtime", _AGENT_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load agent implementation from {_AGENT_PATH}")

_agent_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_agent_module)

globals().update(
    {
        name: getattr(_agent_module, name)
        for name in dir(_agent_module)
        if not name.startswith("_")
    }
)

__all__ = [name for name in globals() if not name.startswith("_")]
