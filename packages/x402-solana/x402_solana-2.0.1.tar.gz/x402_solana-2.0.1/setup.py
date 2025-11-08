from setuptools import setup, find_packages

setup(
    name="x402_solana",
    version="2.0.1",
    description="Complete x402 Protocol Implementation for Solana",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="mega123-art",
    # 💡 FIX: Replaced placeholder URL
    url="https://github.com/mega123-art/x402-solana",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: AsyncIO",
    ],
    install_requires=[
        "solana>=0.30.0",        # Core Solana functionality
        "solders>=0.18.0",        # Solana type wrappers
        "httpx>=0.24.0",          # Modern asynchronous HTTP client
        "spl-token>=0.2.0",       # SPL Token program instructions
        "base58>=2.1.1",          # Used in wallet utilities
    ],
    extras_require={
        # Optional CDP client integration for multi-chain and facilitated payments
        "cdp": ["x402>=1.0.0"],
        # Optional infrastructure components (PaymentCache)
        "infrastructure": ["aioredis>=2.0.0"],
        # Development tools
        "dev": ["pytest", "pytest-asyncio", "black", "mypy"],
    },
    python_requires=">=3.8",
)