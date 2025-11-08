from .cli_args import build_parser
from .constants import SUFFIX_ENCRYPTED, SUFFIX_DECRYPTED, SUFFIX_LEGACY
from . import __version__

def print_banner():
    print(f"\n=== InvCrypt CLI v{__version__} (Community Edition) ===")
    print("Quantum-safe local file encryption based on DITG/FTG\n")

def print_flag_info():
    print_banner()
    print("=== CLI Commands and Parameters ===\n")

    parser = build_parser()
    for action in parser._actions:
        if action.option_strings:  # flags
            flags = ", ".join(action.option_strings)
            help_text = action.help or ""
            print(f"{flags:<25} {help_text}")
        else:  # positional arguments
            name = action.dest
            help_text = action.help or ""
            print(f"<{name}:>                {help_text}")

def print_hash_list(HASH_INFO, default="shake256"):
    print("\n=== Available Hash Functions ===")
    for i, (name, info) in enumerate(HASH_INFO.items(), 1):
        mark = " (default)" if name == default else ""
        print(f"{i}. {name}{mark}")
        print(f"   - {info['bits']}-bit output")
        print(f"   - Classical security: {info['klassisk']} bits")
        print(f"   - Quantum security:   {info['kvant']} bits")
        print(f"   - {'Fast' if info['snabb'] else 'Stable'}\n")

def print_usage_examples():
    print("\n=== Usage Examples ===\n")

    print("Encrypt a file (automatic mode):")
    print("  invcrypt file.txt --seed mypass\n")

    print(f"Decrypt a file (auto-detects {SUFFIX_ENCRYPTED} or {SUFFIX_LEGACY}):")
    print(f"  invcrypt file.txt{SUFFIX_ENCRYPTED} --seed mypass\n")

    print("Specify output file manually:")
    print(f"  invcrypt file.txt -o file.txt{SUFFIX_ENCRYPTED} --seed mypass\n")

    print("Encrypt with hidden password prompt:")
    print("  invcrypt file.txt -p\n")

    print("Decrypt to a specific file:")
    print(f"  invcrypt -m decrypt file.txt{SUFFIX_ENCRYPTED} -o output.txt --seed mypass\n")

    print("Encrypt and delete original file (secure cleanup):")
    print(f"  invcrypt file.txt --seed mypass --delete-original\n")

    print("Test avalanche effect between two files:")
    print("  invcrypt --avalanchtest file1.bin file2.bin\n")

    print("Run full encryption/decryption test:")
    print("  invcrypt --testrun file.txt --seed mypass\n")

    print("Show help, flags and version:")
    print("  invcrypt --info")
    print("  invcrypt --flags")
    print("  invcrypt --hashlist\n")
