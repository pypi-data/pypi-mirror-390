import argparse
try:
    # Package execution (via entry point)
    from . import __version__
except Exception:
    # Direct script execution (fallback)
    from __init__ import __version__

def build_parser():
    parser = argparse.ArgumentParser(
        description="InvCrypt CLI (Community Edition) – Quantum-safe local file encryption based on DITG/FTG",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # === Info & help ===
    meta = parser.add_argument_group("Info & Help")
    meta.add_argument("--info", action="store_true", help="Show CLI overview, flags and examples")
    meta.add_argument("--flags", action="store_true", help="Show only CLI flags")
    meta.add_argument("--hashlist", action="store_true", help="Show available hash functions")

    # === Input / Output ===
    io = parser.add_argument_group("Input / Output")
    io.add_argument("input_file", type=str, nargs="?", help="Input file")
    io.add_argument("output_file", type=str, nargs="?", help="Output file (if not using --output)")
    io.add_argument("-o", "--output", type=str, help="Output file (alternative to positional argument)")

    # === Operation & encryption ===
    run = parser.add_argument_group("Operation & Encryption")
    run.add_argument("-m", "--mode", choices=["encrypt", "decrypt"], help="Select operation mode: encrypt or decrypt")
    run.add_argument("-s", "--seed", type=str, help="Seed / password (can be provided directly)")
    run.add_argument("-p", "--password-prompt", action="store_true", help="Prompt for password (hidden input)")
    run.add_argument("--hash", type=str, default="shake256", help="Hash function to use")
    run.add_argument("--avalanchtest", nargs=2, metavar=("FILE1", "FILE2"), help="Test avalanche effect between two files")
    run.add_argument("--metrics", action="store_true", help="Show extended metrics")
    run.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    run.add_argument("--testrun", type=str, metavar="FILE", help="Perform full test round (encrypt + decrypt + verify)")
    run.add_argument("--overwrite", action="store_true", help="Allow overwriting an existing output file")

    parser.add_argument("--version", action="version", version=f"InvCrypt CLI v{__version__} (Community Edition)")
    return parser
