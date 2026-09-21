"""
Agent Loader — core/agent_loader.py
Loads agent definitions from agents/<name>.md using its bundled frontmatter reader.
Maintains active agent runtime state for CLI and Web Cockpit.
"""

from pathlib import Path
import json
from typing import Dict, Any, List

AGENTS_DIR = Path(__file__).parent.parent / "agents"
STATE_FILE = Path(__file__).parent.parent / "ui" / "state.json"

_ACTIVE_AGENT_NAME = "engineer"

def _parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    """Read the scalar-only frontmatter format used by bundled agents."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    _, header, body = text.split("---", 2)
    metadata = {}
    for line in header.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"\'')
    return metadata, body.lstrip("\r\n")


def load_agent(name: str) -> Dict[str, Any]:
    """
    Load an agent definition from agents/<name>.md
    Returns a dict with system_prompt + all frontmatter fields.
    """
    path = AGENTS_DIR / f"{name}.md"
    if not path.exists():
        available = [p.stem for p in AGENTS_DIR.glob("*.md")]
        raise FileNotFoundError(
            f"Agent '{name}' not found. Available agents: {available}"
        )

    metadata, content = _parse_frontmatter(path)

    agent = {
        "name": metadata.get("name", name),
        "description": metadata.get("description", ""),
        "system_prompt": content.strip(),
        "temperature": float(metadata.get("temperature", 0.7)),
        "top_logprobs": int(metadata.get("top_logprobs", 5)),
        "max_tokens": int(metadata.get("max_tokens", 1024)),
        "role": metadata.get("role", metadata.get("description", "Sovereign Agent")),
        "model": metadata.get("model", "nemotron-4b"),
        "path": str(path),
    }

    # Pass through any extra frontmatter keys
    for key, value in metadata.items():
        if key not in agent:
            agent[key] = value

    return agent


def list_agents() -> List[str]:
    """Returns sorted list of agent stem names."""
    if not AGENTS_DIR.exists():
        return []
    return sorted(p.stem for p in AGENTS_DIR.glob("*.md"))


def list_available_agents() -> List[Dict[str, Any]]:
    """Returns metadata for all available agents for API & UI."""
    result = []
    for name in list_agents():
        try:
            a = load_agent(name)
            result.append({
                "name": a["name"],
                "role": a.get("role", a.get("description", "")),
                "description": a.get("description", ""),
                "temperature": a.get("temperature", 0.7),
                "max_tokens": a.get("max_tokens", 1024),
                "top_logprobs": a.get("top_logprobs", 5)
            })
        except Exception:
            pass
    return result


def get_active_agent() -> Dict[str, Any]:
    """Returns currently active runtime agent."""
    global _ACTIVE_AGENT_NAME
    return load_agent(_ACTIVE_AGENT_NAME)


def set_active_agent(name: str) -> Dict[str, Any]:
    """
    Hot-switches the active runtime agent mid-session.
    Updates the in-memory pointer and preserves state in ui/state.json.
    """
    global _ACTIVE_AGENT_NAME
    agent_data = load_agent(name)
    _ACTIVE_AGENT_NAME = agent_data["name"]

    try:
        if STATE_FILE.exists():
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        else:
            state = {}
        state["active_agent"] = {
            "name": agent_data["name"],
            "role": agent_data.get("role", agent_data.get("description", "")),
            "description": agent_data.get("description", "")
        }
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass

    return agent_data


if __name__ == "__main__":
    print(f"Available agents: {list_agents()}")
    eng = load_agent("engineer")
    print(f"Loaded engineer: {eng['name']} (temp: {eng['temperature']})")
    frm = load_agent("framework")
    print(f"Loaded framework: {frm['name']} (tokens: {frm['max_tokens']})")
