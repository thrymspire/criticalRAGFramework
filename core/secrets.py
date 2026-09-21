"""
Secrets Vault Enclave Loader for Critical Path Harness
Secures API keys, tokens, and credentials in the /etc/harness/secrets/ enclave directory.
Ensures secrets are never exposed in terminal outputs or git commits.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

# Default enclave path in criticalpath-harness-v1.0 (chmod 700)
ENCLAVE_SECRETS_DIR = Path("/etc/harness/secrets")
FALLBACK_LOCAL_SECRETS_DIR = Path.home() / ".harness" / "secrets"


class SecretVault:
    """Secure memory vault for managing secrets loaded from enclave storage."""

    def __init__(self, secrets_dir: Optional[Path] = None):
        self.secrets_dir = secrets_dir or (
            ENCLAVE_SECRETS_DIR if ENCLAVE_SECRETS_DIR.exists() else FALLBACK_LOCAL_SECRETS_DIR
        )
        self._cache: Dict[str, str] = {}
        self.load_secrets()

    def load_secrets(self) -> None:
        """Loads all secret files from the vault directory into memory."""
        if not self.secrets_dir.exists():
            return

        try:
            for item in self.secrets_dir.iterdir():
                if item.is_file() and not item.name.startswith("."):
                    key_name = item.name.upper().replace("-", "_").replace(".", "_")
                    self._cache[key_name] = item.read_text(encoding="utf-8").strip()
        except PermissionError:
            print(f"[VAULT] Warning: Insufficient permissions reading {self.secrets_dir}", file=sys.stderr)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieves a secret by key, checking vault memory then environment variables."""
        norm_key = key.upper().replace("-", "_").replace(".", "_")
        if norm_key in self._cache:
            return self._cache[norm_key]
        return os.environ.get(norm_key, os.environ.get(key, default))

    def mask(self, key: str) -> str:
        """Returns a safe masked representation of a secret for logs and UI status."""
        val = self.get(key)
        if not val:
            return "[MISSING]"
        if len(val) <= 8:
            return "********"
        return f"{val[:4]}...{val[-4:]}"

    def list_available_keys(self) -> list[str]:
        """Returns list of loaded secret keys without revealing values."""
        return sorted(list(self._cache.keys()))


# Global singleton helper
_VAULT_INSTANCE: Optional[SecretVault] = None

def get_vault() -> SecretVault:
    global _VAULT_INSTANCE
    if _VAULT_INSTANCE is None:
        _VAULT_INSTANCE = SecretVault()
    return _VAULT_INSTANCE
