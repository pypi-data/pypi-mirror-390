import argparse
from .patcher import patch_installed_mamba2

def main():
    parser = argparse.ArgumentParser(
        description="Patch mamba2_torch to run on Apple Silicon without Triton."
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="suppress per-file output"
    )
    args = parser.parse_args()

    patched = patch_installed_mamba2(verbose=not args.quiet)
    if not args.quiet and patched == 0:
        print("nothing to patch.")
