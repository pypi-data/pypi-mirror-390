from __future__ import annotations
from pathlib import Path
import importlib.util
import re

# This is the code which will prepend to files that import triton
DUMMY_TRITON = """try:
    import triton
    import triton.language as tl
    HAS_TRITON = True
except ImportError:
    HAS_TRITON = False
    class _DummyLang:
        def __getattr__(self, name):
            return type(name, (), {})
    class _DummyTriton:
        __version__ = "0.0.0"
        language = _DummyLang()
        @staticmethod
        def jit(fn): return fn
        @staticmethod
        def autotune(*a, **k):
            def dec(fn): return fn
            return dec
        @staticmethod
        def heuristics(*a, **k):
            def dec(fn): return fn
            return dec
        class Config:
            def __init__(self, *a, **k): pass
    triton = _DummyTriton()
    tl = triton.language
"""

# matches lines like: TRITON_VERSION = version.parse(triton.__version__)
TRITON_VERSION_RE = re.compile(
    r"(\w+)\s*=\s*version\.parse\(triton\.__version__\)"
)


def patch_triton_block(text: str) -> str:
    # If there's no triton import at all, don't touch it
    if "import triton" not in text and "from triton" not in text:
        return text
    # If already patched, don't double-patch
    if "HAS_TRITON" in text:
        return text

    lines = text.splitlines()
    # remove original triton imports
    lines = [
        ln for ln in lines
        if not ln.lstrip().startswith("import triton")
        and not ln.lstrip().startswith("from triton")
    ]

    return DUMMY_TRITON + "\n" + "\n".join(lines)


def patch_version_checks(text: str) -> str:
    # make version checks conditional on HAS_TRITON
    return TRITON_VERSION_RE.sub(
        r"\1 = HAS_TRITON and version.parse(triton.__version__)", text
    )


def patch_file(path: Path) -> bool:
    src = path.read_text()
    orig = src

    src = patch_triton_block(src)
    src = patch_version_checks(src)

    if src != orig:
        path.write_text(src)
        return True
    return False



def find_mamba2_ops_dir() -> Path:
    """
    Locate mamba2_torch on disk WITHOUT importing it (so we don't trigger triton).
    """
    spec = importlib.util.find_spec("mamba2_torch")
    if spec is None or spec.origin is None:
        raise ModuleNotFoundError(
            "mamba2_torch is not installed in this environment."
        )

    # spec.origin points to .../mamba2_torch/__init__.py
    root = Path(spec.origin).parent
    ops_dir = root / "ops"
    if not ops_dir.exists():
        raise FileNotFoundError(f"Could not find ops/ in {root}")
    return ops_dir

def patch_installed_mamba2(verbose: bool = True) -> int:
    ops_dir = find_mamba2_ops_dir()
    changed = 0
    for py in sorted(ops_dir.glob("*.py")):
        if py.name == "__init__.py":
            continue
        if patch_file(py):
            changed += 1
            if verbose:
                print(f"patched {py}")
    if verbose:
        print(f"done. {changed} file(s) patched.")
    return changed
