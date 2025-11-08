# invcrypt/main.py
import os
import time
import getpass

from .config import CONFIG
from .metrics import log_metrics_extended
from .info import print_flag_info, print_hash_list, print_usage_examples
from .cli_args import build_parser
from .constants import SUFFIX_ENCRYPTED, SUFFIX_DECRYPTED, SUFFIX_LEGACY
from .loader import load_protected
from . import __version__

matrix = load_protected("matrix")
crypto_core = load_protected("crypto_core")
hashing = load_protected("hashing")
utils = load_protected("utils")

# Gör alias till funktioner från skyddade moduler
set_hash_function = hashing.set_hash_function
hash_bytes = hashing.hash_bytes
file_hash = hashing.file_hash
get_hash_info = hashing.get_hash_info

avalanche_effect_file = utils.avalanche_effect_file
get_param_span_from_hash = utils.get_param_span_from_hash
DITGKeySchedule = utils.DITGKeySchedule

build_data_matrix = matrix.build_data_matrix
reconstruct_data_from_matrix = matrix.reconstruct_data_from_matrix
optimal_matrix_config = matrix.optimal_matrix_config

encrypt_matrix = crypto_core.encrypt_matrix
decrypt_matrix = crypto_core.decrypt_matrix

# === Konstanter ===
ALL_HASHES = ["shake256", "shake256x", "blake3x"]
MAGIC = b"INVCRYPT"
VERSION = 1

HASH_ID_MAP = {"shake256": 1, "shake256x": 2, "blake3x": 3}
HASH_ID_REVERSE = {v: k for k, v in HASH_ID_MAP.items()}


# === Hjälpfunktioner ===
def test_roundtrip(filepath, seed, hashname):
    """Testkörning: kryptera och dekryptera samma fil automatiskt."""
    import tempfile, uuid
    print(f"\n=== 🔁 TESTRUN (fil: {filepath}) ===")

    temp_dir = tempfile.gettempdir()
    temp_enc = os.path.join(temp_dir, f"invcrypt_{uuid.uuid4().hex}.invx")
    temp_dec = os.path.join(temp_dir, f"invcrypt_{uuid.uuid4().hex}.decrypted")

    for f in [temp_enc, temp_dec]:
        try:
            if os.path.exists(f):
                os.remove(f)
        except Exception:
            pass

    os.system(f'python -m invcrypt.main "{filepath}" "{temp_enc}" '
              f'--mode encrypt --seed "{seed}" --hash {hashname} --overwrite')
    os.system(f'python -m invcrypt.main "{temp_enc}" "{temp_dec}" '
              f'--mode decrypt --seed "{seed}" --hash {hashname} --overwrite')

    if os.path.exists(temp_dec):
        try:
            h1 = file_hash(filepath)
            h2 = file_hash(temp_dec)
            if h1 == h2:
                print("\n✅ Verifierad integritet – hash matchar originalfilen.")
            else:
                print("\n⚠️ Hash skiljer sig mellan original och dekrypterad fil.")
        except Exception as e:
            print(f"⚠️ Kunde inte verifiera hash: {e}")

    print(f"\n✅ Testkörning klar – krypterad: {temp_enc} | dekrypterad: {temp_dec}")


def _get_password(args):
    if getattr(args, "password_prompt", False):
        return getpass.getpass("Ange lösenord: ")
    if args.seed:
        return args.seed
    print("❌ Du måste ange lösenord via --seed eller --password-prompt")
    raise SystemExit(1)


def _derive_master_key(password_str: str) -> bytes:
    pw_bytes = bytearray(password_str.encode("utf-8"))
    mk = hash_bytes(bytes(pw_bytes), raw=True, length=64)
    for i in range(len(pw_bytes)):
        pw_bytes[i] = 0
    del pw_bytes
    return mk


def _write_header(fh, hash_name: str, original_length: int, stored_hash: bytes, master_key: bytes):
    hash_id = HASH_ID_MAP.get(hash_name, 0)
    if hash_id == 0:
        raise ValueError(f"Okänd hashfunktion i header: {hash_name}")
    compressed_length = original_length
    auth_tag = hash_bytes(master_key + stored_hash, raw=True, length=32)

    fh.write(MAGIC)
    fh.write(bytes([VERSION]))
    fh.write(bytes([hash_id]))
    fh.write(original_length.to_bytes(8, "big"))
    fh.write(compressed_length.to_bytes(8, "big"))
    fh.write(stored_hash)
    fh.write(auth_tag)


def _read_and_verify_header(fh, master_key: bytes):
    magic = fh.read(8)
    if magic != MAGIC:
        raise ValueError("Ogiltig fil – verkar inte vara en InvCrypt-fil.")
    version = int.from_bytes(fh.read(1), "big")
    if version != VERSION:
        raise ValueError(f"Filversion {version} stöds ej (CLI-version {VERSION}).")
    hash_id = int.from_bytes(fh.read(1), "big")
    if hash_id not in HASH_ID_REVERSE:
        raise ValueError("Okänd hash-id i filheadern.")
    hash_name = HASH_ID_REVERSE[hash_id]
    original_length = int.from_bytes(fh.read(8), "big")
    compressed_length = int.from_bytes(fh.read(8), "big")
    stored_hash = fh.read(32)
    auth_tag = fh.read(32)

    expected_tag = hash_bytes(master_key + stored_hash, raw=True, length=32)
    if expected_tag != auth_tag:
        raise ValueError("Fel lösenord – autentisering misslyckades.")
    return hash_name, original_length, compressed_length, stored_hash


def _infer_mode(args):
    if args.mode:
        return args.mode
    if args.input_file:
        if args.input_file.endswith(SUFFIX_ENCRYPTED) or args.input_file.endswith(SUFFIX_LEGACY):
            return "decrypt"
    return "encrypt"


# === Huvudfunktion ===
def main():
    try:
        parser = build_parser()
        parser.add_argument("--delete-original", action="store_true",
                            help="Radera originalfilen efter lyckad operation")
        args = parser.parse_args()

        set_hash_function(args.hash)

        # Info / flaggar
        if args.flags:
            print_flag_info()
            return
        if args.hashlist:
            HASH_INFO = {name: get_hash_info(name) for name in ALL_HASHES}
            print_hash_list(HASH_INFO)
            return
        if args.info:
            HASH_INFO = {name: get_hash_info(name) for name in ALL_HASHES}
            print_flag_info()
            print_hash_list(HASH_INFO)
            print_usage_examples()
            return
        if args.avalanchtest:
            avalanche_effect_file(args.avalanchtest[0], args.avalanchtest[1])
            return
        if args.testrun:
            test_roundtrip(args.testrun, args.seed or "testseed", args.hash)
            return

        # Lösenord → master key
        password = _get_password(args)
        master_key = _derive_master_key(password)
        del password

        args.mode = _infer_mode(args)

        # Output-fil
        output_file = args.output or args.output_file
        if not output_file and args.input_file:
            if args.mode == "encrypt":
                output_file = args.input_file + SUFFIX_ENCRYPTED
            else:
                if args.input_file.endswith(SUFFIX_ENCRYPTED):
                    output_file = args.input_file[:-len(SUFFIX_ENCRYPTED)]
                elif args.input_file.endswith(SUFFIX_LEGACY):
                    output_file = args.input_file[:-len(SUFFIX_LEGACY)]
                else:
                    output_file = args.input_file + SUFFIX_DECRYPTED

        if not args.input_file or not os.path.isfile(args.input_file):
            print("❌ Input-fil saknas eller ogiltig sökväg.")
            return
        if not output_file:
            print("❌ Output-fil saknas och kunde inte härledas.")
            return
        if os.path.exists(output_file) and not args.overwrite:
            print(f"❌ Output-fil '{output_file}' finns redan. Använd --overwrite för att skriva över.")
            return

        print(f"--- InvCrypt CLI ---")
        print(f"Mode: {args.mode}")
        print(f"Input-fil: {args.input_file}")
        print(f"Output-fil: {output_file}")
        print(f"Hashfunktion: {args.hash}\n")

        # === Kryptering ===
        if args.mode == "encrypt":
            with open(args.input_file, "rb") as f:
                data = f.read()
            min_size = CONFIG.get("min_file_size", 32)
            if len(data) < min_size:
                print(f"❌ Filen är för liten ({len(data)} bytes). "
                      f"Minsta tillåtna storlek är {min_size} bytes för att säkerställa robust kryptering.")
                return

            original_length = len(data)
            data_hash = hash_bytes(data, raw=True, length=32)
            a_min, a_max = get_param_span_from_hash(data_hash, 2, 128, 32)

            conf_auto = optimal_matrix_config(original_length, CONFIG)
            conf = {**CONFIG, **conf_auto, "original_length": original_length, "a_min": a_min, "a_max": a_max}
            ks = DITGKeySchedule(master_key, conf)

            matrix_data, init_vec, _ = build_data_matrix(data, conf, ks, data_hash)
            print("Krypterar filen...")
            t0 = time.time()
            enc_bytes = encrypt_matrix(matrix_data, init_vec, ks, show_progress=True)
            t1 = time.time()

            tmp_path = output_file + ".tmp"
            with open(tmp_path, "wb") as f:
                _write_header(f, args.hash, original_length, data_hash, master_key)
                f.write(enc_bytes)
            os.replace(tmp_path, output_file)

            log_metrics_extended(
                label="Kryptering",
                input_path=args.input_file,
                output_path=output_file,
                hash_name=args.hash,
                duration_sec=t1 - t0,
                original_length=original_length,
                conf=conf,
                ks=ks,
                hash_input=file_hash(args.input_file),
                hash_encrypted=file_hash(output_file),
            )

        # === Dekryptering ===
        elif args.mode == "decrypt":
            with open(args.input_file, "rb") as f:
                try:
                    hash_name_hdr, original_length, compressed_length, stored_hash = _read_and_verify_header(f, master_key)
                    if hash_name_hdr != args.hash:
                        set_hash_function(hash_name_hdr)
                    enc_bytes = f.read()
                except ValueError as e:
                    print(f"❌ {e}")
                    return

            a_min, a_max = get_param_span_from_hash(stored_hash, 2, 128, 32)
            conf_auto = optimal_matrix_config(compressed_length, CONFIG)
            conf = {**CONFIG, **conf_auto, "original_length": original_length, "a_min": a_min, "a_max": a_max}
            ks = DITGKeySchedule(master_key, conf)
            init_vec = ks.get_init_vec(stored_hash, conf["dim1"], conf["cell_size_encrypted"])

            print("Dekrypterar filen...")
            t0 = time.time()
            dec_matrix = decrypt_matrix(enc_bytes, init_vec, ks, show_progress=True)
            out_bytes = reconstruct_data_from_matrix(dec_matrix, conf["cell_size_data"], original_length, compressed_length)
            t1 = time.time()

            computed_hash = hash_bytes(out_bytes, raw=True, length=32)
            if computed_hash != stored_hash:
                print("❌ Dekryptering misslyckades: Filen är korrupt eller lösenordet fel.")
                return

            tmp_path = output_file + ".tmp"
            with open(tmp_path, "wb") as f:
                f.write(out_bytes)
            os.replace(tmp_path, output_file)

            log_metrics_extended(
                label="Dekryptering",
                input_path=args.input_file,
                output_path=output_file,
                hash_name=args.hash,
                duration_sec=t1 - t0,
                original_length=original_length,
                conf=conf,
                ks=ks,
                hash_input=stored_hash.hex(),
                hash_encrypted=file_hash(args.input_file),
                hash_decrypted=file_hash(output_file),
            )
            print("✅ Verifiering OK – Hash matchar.")

        # === Radera original vid begäran ===
        if args.delete_original:
            try:
                os.remove(args.input_file)
                print(f"🗑️ Originalfilen '{args.input_file}' har raderats.")
            except Exception as e:
                print(f"⚠️ Kunde inte radera originalfilen: {e}")

        # Nollställ nyckel ur minnet
        if isinstance(master_key, (bytes, bytearray)):
            try:
                mk_mut = bytearray(master_key)
                for i in range(len(mk_mut)):
                    mk_mut[i] = 0
                del mk_mut
            except Exception:
                pass
        del master_key

        print(f"\n✅ Klar! {'Krypterade' if args.mode == 'encrypt' else 'Dekrypterade'}")
        print(f"📄 Input:  {args.input_file}")
        print(f"📁 Output: {output_file}\n")

    except FileNotFoundError:
        print("❌ Filen hittades inte. Kontrollera sökvägen.")
    except PermissionError:
        print("❌ Åtkomst nekad – kör som admin eller välj annan plats.")
    except KeyboardInterrupt:
        print("\n⏹️ Avbrutet av användaren.")
    except Exception as e:
        print(f"⚠️ Oväntat fel: {str(e)}")


if __name__ == "__main__":
    main()
