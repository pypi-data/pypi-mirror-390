from setuptools import find_packages, setup
import os

# Ensure we're reading from the correct directory
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, "ReadMe.md"), "r", encoding="utf-8") as f:
        long_description = f.read()
except Exception as e:
    print(f"Warning: Could not read ReadMe.md: {e}")
    long_description = "An implementation of separation distances and s/c-metrics for causal graphs."

setup(
    name="sep_distances",
    version="1.0.0",
    description="An implementation of separation distances and s/c-metrics for causal graphs as introduced in the paper 'Separation-based distance metrics for causal graphs'.",
    package_dir={"sep_distances": "codebase",
                 "sep_distances.tests": "tests"},
    packages=["sep_distances", "sep_distances.tests"],
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JonasChoice/sep_distances",
    author="Jonas Wahl",
    author_email="jonas.wahl@dfki.de",
    license="GPL-3.0-only",
    install_requires=[
        "gadjid>=0.1.0",
        "networkx>=3.4.2",
        "numpy>=2.2.3",
        "scipy>=1.15.2",
        "setuptools>=75.8.0",
        "wheel>=0.45.1",
        ],
    extras_require={
        "dev": ["pytest>=7.0"],
        "twine": ["twine>=4.0.2"],
    },
    python_requires=">=3.10",
)