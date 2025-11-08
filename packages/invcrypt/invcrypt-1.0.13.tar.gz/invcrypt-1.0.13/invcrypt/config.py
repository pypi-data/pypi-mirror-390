CONFIG = {
    # 🔐 Nyckelgenerering
    "max_wraps": 2**128,
    "max_m": 16,

    # 📏 Matrisstorlek
    "min_cell_size": 10,     # Minsta tillåtna datacellsstorlek (bytes)
    "max_cell_size": 64,     # Största tillåtna datacellsstorlek (bytes)
    "min_blocks": 4,         # Minsta antal block/rader i matrisen
    "max_blocks": 5000,      # Max antal block/rader
    "min_dim1": 64,           # Minsta antal kolumner
    "max_dim1": 1000000,     # Max antal kolumner

    # 📦 Krypteringsstorlek
    "cell_size_encrypted": 16,  # Antal bytes per krypterad cell

    # 🎯 Kompression (just nu 0 för att behålla exakt storlek)
    "target_compression_percent": 0,
    
    # 🔁 Synka krypteringscell med datacell
    "match_cell_sizes": True,

    # 🔐 Minsta tillåtna filstorlek (bytes)
    "min_file_size": 4096
}
