from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="paegents",
    version="2.4.0",
    author="Paegents Inc",
    author_email="support@paegents.com",
    description="Official Python SDK for Paegents - Payment infrastructure for AI agents with Service Catalog and Usage Escrow",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paegents/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/paegents/python-sdk/issues",
        "Documentation": "https://docs.paegents.com",
        "Homepage": "https://paegents.com",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ]
    },
    keywords="payments ai agents fintech automation stripe braintree stablecoin",
)