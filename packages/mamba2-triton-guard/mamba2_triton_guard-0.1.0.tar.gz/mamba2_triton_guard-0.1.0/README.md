# mamba2-triton-guard

A tiny helper tool that patches an installed `mamba2_torch` so it can be imported on Apple Silicon (M1/M2/M3) **even when Triton isn't available**.

This is useful when:
- you're experimenting with Mamba 2 models on macOS,
- you only want to run on CPU/MPS,
- the library you installed assumes Triton is present and crashes at import time.

> **Note**  
> This tool does **not** provide Triton kernels and does **not** make Triton work on macOS. It only makes the Python package *importable* by guarding or stubbing Triton-related imports.

---

## Installation

Install from your local checkout or from a package index:

```bash
pip install mamba2-triton-guard
```

Or, from a local source tree:

```bash
pip install -e .
```

(Use whatever virtual environment workflow you prefer.)

---

## Usage

1. Make sure `mamba2_torch` is installed in **the same environment**:

   ```bash
   pip install mamba2-torch  # example; use the actual source you have
   ```

2. Run the guard:

   ```bash
   mamba2-triton-guard
   ```

   This will:
   - locate the installed `mamba2_torch`
   - find its `ops/` modules
   - wrap Triton imports in a `try/except` with a lightweight dummy Triton

3. Test the import:

   ```bash
   python -c "from mamba2_torch import Mamba2Config; print('ok')"
   ```

If that works, you can run your own script that imports and uses `mamba2_torch`.

---

## How it works

- The tool discovers the installed `mamba2_torch` **without importing it**, so it doesn't trigger the failing `import triton`.
- It scans the `ops/` directory for files that directly import Triton.
- For each such file, it:
  - removes the raw `import triton` lines
  - prepends a guarded block like:

    ```python
    try:
        import triton
        import triton.language as tl
        HAS_TRITON = True
    except ImportError:
        HAS_TRITON = False
        # define a tiny dummy Triton that accepts decorators
        ...
    ```

- It also makes version checks conditional on `HAS_TRITON`.

This keeps the module importable on platforms where Triton is not present.

---

## Limitations

- This is a **workaround** for packages that aggressively import Triton at import time.
- It does **not** enable Triton kernels on macOS.
- If the upstream package changes its layout (different module names, no `ops/`, etc.), you may need to update this tool.
- Always run it inside the environment that actually holds `mamba2_torch`.

---

## CLI

```text
usage: mamba2-triton-guard [-h] [-q]

Patch mamba2_torch to run on Apple Silicon without Triton.

options:
  -h, --help   show help and exit
  -q, --quiet  suppress per-file output
```

---

## Development

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install in editable mode:

   ```bash
   pip install -e .
   ```

4. Run the CLI against an environment that has `mamba2_torch` installed.

---

## License

MIT
