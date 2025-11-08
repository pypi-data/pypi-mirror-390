from setuptools import setup, find_packages
import re
import os

def read_version():
    """Extract __version__ from invcrypt/__init__.py"""
    version_file = os.path.join(os.path.dirname(__file__), "invcrypt", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r'__version__\s*=\s*["\'](.+)["\']', line)
            if match:
                return match.group(1)
    raise RuntimeError("Version not found in __init__.py")

setup(
    name="invcrypt",
    version=read_version(),
    author="INVICRA Technologies AB",
    author_email="contact@invicra.com",
    description="Quantum-safe local file encryption CLI based on Invicra’s DITG/FTG cryptography.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ivarolsson1415/invcrypt-community",
    license="Invicra Community License 2025",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Security :: Cryptography",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "tqdm>=4.66.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "invcrypt=invcrypt.main:main",
        ],
    },
    keywords=[
        "encryption",
        "quantum-safe",
        "post-quantum",
        "cli",
        "cryptography",
        "invicra",
    ],
)

