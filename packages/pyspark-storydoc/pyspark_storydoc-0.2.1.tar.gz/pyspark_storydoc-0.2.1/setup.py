"""Setup configuration for PySpark StoryDoc."""

import os

from setuptools import find_packages, setup

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Business-friendly data lineage documentation for PySpark"

# Read requirements
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]
else:
    requirements = [
        "pyspark>=3.5.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
    ]

# Get version
version_file = os.path.join(os.path.dirname(__file__), "pyspark_storydoc", "version.py")
version_info = {}
with open(version_file, "r", encoding="utf-8") as fh:
    exec(fh.read(), version_info)

setup(
    name="pyspark-storydoc",
    version=version_info["__version__"],
    author=version_info["__author__"],
    author_email=version_info["__email__"],
    description=version_info["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyspark-storydoc/pyspark-storydoc",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Documentation",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
        ],
        "visualization": [
            "graphviz>=0.20.0",
        ],
        "history": [
            "delta-spark>=2.4.0",
        ],
        "all": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
            "graphviz>=0.20.0",
            "delta-spark>=2.4.0",
        ],
    },
    include_package_data=True,
    package_data={
        "pyspark_storydoc": [
            "config/*.yml",
            "config/*.yaml",
            "visualization/templates/*.j2",
            "visualization/templates/*.html",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyspark-storydoc=pyspark_storydoc.cli:main",
        ],
    },
    keywords="pyspark spark lineage visualization business data-science",
    project_urls={
        "Bug Reports": "https://github.com/pyspark-storydoc/pyspark-storydoc/issues",
        "Source": "https://github.com/pyspark-storydoc/pyspark-storydoc",
        "Documentation": "https://pyspark-storydoc.readthedocs.io/",
    },
)
