
from .loader import load_protected


# Load protected hashing module
hashing = load_protected("hashing")
utils = load_protected("utils")

def log_metrics_extended(
    label: str,                    # "Encryption" or "Decryption"
    input_path: str,
    output_path: str,
    hash_name: str,
    duration_sec: float,
    original_length: int,
    conf: dict,
    ks,                            # KeySchedule
    hash_input: str,
    hash_encrypted: str,
    hash_decrypted: str = None
):
    print("\n=== METRICS ===")

    # General
    print(f"File: {input_path}")
    print(f"Original length: {original_length:,} bytes")
    print(f"Hash function: {hash_name}")

    # Hash information
    info = hashing.get_hash_info(hash_name)
    print(f"Classical security: {info['klassisk']} bits")
    print(f"Quantum security:   {info['kvant']} bits")
    print(f"Performance: {'Fast' if info['snabb'] else 'Stable'}")

    # Matrix structure
    print("\n--- Matrix Structure ---")
    print(f"Cell size (data): {conf['cell_size_data']} bytes")
    print(f"Cell size (encrypted): {conf['cell_size_encrypted']} bytes")
    print(f"Blocks (rows): {conf['blocks']}")
    print(f"Dim1 (columns): {conf['dim1']}")
    print(f"Total cells: {conf['total_cells']}")

    # Padding
    total_bytes = conf['cell_size_data'] * conf['total_cells']
    padding_bytes = total_bytes - original_length
    padding_percent = 100 * padding_bytes / total_bytes if total_bytes else 0
    print(f"Padding: {padding_bytes} bytes ({padding_percent:.2f}%)")

    # Performance
    print("\n--- Performance ---")
    in_MB = original_length / 1_000_000
    MBps = in_MB / duration_sec if duration_sec > 0 else 0
    print(f"{label} took {duration_sec:.2f} seconds")
    print(f"Speed: {MBps:.2f} MB/s")

    # Hashes
    print("\n--- Hashes ---")
    print(f"Input hash:        {hash_input[:64]}")
    print(f"Encrypted hash:    {hash_encrypted[:64]}")
    if hash_decrypted:
        print(f"Decrypted hash:    {hash_decrypted[:64]}")
        print(f"Hash match: {'YES' if hash_decrypted == hash_input else 'NO'}")

    # Key parameters
    print("\n--- Key Parameters (Example) ---")
    i, j = 0, 0
    a, b, n, m = ks.get_params(i, j)
    rk = ks.get_rk(i, j, conf["cell_size_data"])
    wraps = ks.get_wraps(i, j)
    print(f"a={a}, b={b}, n={n}, m={m}")
    print(f"r_k={rk}")
    print(f"wraps={wraps}")

    print("=== END ===\n")
