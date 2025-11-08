# invcrypt/loader.py
import importlib.util
import sys
import os


def load_protected(name):
    """
    Ladda en skyddad modul (.pyc) från __pycache__ om .py saknas.
    """
    base = os.path.dirname(__file__)
    # Försök hitta optimerad .pyc (skapas med python -O)
    pyc_path = os.path.join(base, "__pycache__", f"{name}.cpython-312.opt-1.pyc")
    if not os.path.exists(pyc_path):
        pyc_path = os.path.join(base, "__pycache__", f"{name}.cpython-312.pyc")
    if not os.path.exists(pyc_path):
        raise ImportError(f"Protected module not found: {name} ({pyc_path})")

    spec = importlib.util.spec_from_file_location(f"invcrypt.{name}", pyc_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[f"invcrypt.{name}"] = module
    return module
