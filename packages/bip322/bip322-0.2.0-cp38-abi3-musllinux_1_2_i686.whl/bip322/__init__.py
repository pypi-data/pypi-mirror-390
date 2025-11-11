# Re-export the Rust extension function from the compiled submodule (.abi3.so)
from .bip322 import verify_simple_encoded as verify_simple_encoded  # type: ignore[attr-defined]
from .bip322 import VerificationError as VerificationError          # type: ignore[attr-defined]

__all__ = ["verify_simple_encoded", "VerificationError"]

# Optional: expose package version for convenience
try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("bip322")
except Exception:
    __version__ = "0"
