"""
DataWeaver: Revolutionary Resonance Learning Algorithm
Setup configuration for PyPI distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="dataweaver-ai",
    version="1.0.0",
    author="Fardin Ibrahimi",
    author_email="fiafghan@example.com",  # Replace with your actual email
    description="Revolutionary Resonance Learning - Discover patterns between patterns through multi-dimensional harmonics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fiafghan/DataWeaver",  # Replace with your actual repo URL
    packages=find_packages(),
    py_modules=["dataweaver"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "machine-learning",
        "deep-learning",
        "resonance-learning",
        "pattern-recognition",
        "neural-networks",
        "pytorch",
        "multi-view-learning",
        "data-science",
        "artificial-intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "viz": [
            "matplotlib>=3.5.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/fiafghan/DataWeaver/issues",
        "Source": "https://github.com/fiafghan/DataWeaver",
        "Documentation": "https://github.com/fiafghan/DataWeaver/blob/main/DATAWEAVER_WHITEPAPER.md",
    },
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)
