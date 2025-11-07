from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="dns-threat-detector",
    version="1.0.6",
    author="UMUDGA Project",
    author_email="contact@umudga.edu",
    description="Production-ready DNS threat detection using machine learning - Model-driven architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SubratDash67/DNS-Security",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "lightgbm>=4.0.0",
        "scikit-learn>=1.3.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "tldextract>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dns-detect=dns_threat_detector.cli:main",
        ],
    },
    include_package_data=True,
    keywords=[
        "dns",
        "threat-detection",
        "machine-learning",
        "dga",
        "typosquatting",
        "security",
        "cybersecurity",
        "malware",
        "phishing",
    ],
    project_urls={
        "Documentation": "https://github.com/umudga/dns-threat-detector/wiki",
        "Source": "https://github.com/umudga/dns-threat-detector",
        "Bug Reports": "https://github.com/umudga/dns-threat-detector/issues",
    },
)
