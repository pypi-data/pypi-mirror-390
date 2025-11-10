"""Setup configuration for NeuroBUS."""

from setuptools import find_packages, setup

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version
with open("VERSION", "r", encoding="utf-8") as fh:
    version = fh.read().strip()

# Core dependencies
install_requires = [
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "aiofiles>=23.0.0",
]

# Optional dependencies
extras_require = {
    "semantic": [
        "sentence-transformers>=2.2.0",
        "torch>=2.0.0",
        "numpy>=1.24.0",
    ],
    "qdrant": [
        "qdrant-client>=1.7.0",
    ],
    "lancedb": [
        "lancedb>=0.3.0",
        "pyarrow>=12.0.0",
    ],
    "memory": [
        "qdrant-client>=1.7.0",
        "lancedb>=0.3.0",
        "pyarrow>=12.0.0",
    ],
    "openai": [
        "openai>=1.12.0",
    ],
    "anthropic": [
        "anthropic>=0.18.0",
    ],
    "ollama": [
        "httpx>=0.25.0",
    ],
    "llm": [
        "openai>=1.12.0",
        "anthropic>=0.18.0",
        "httpx>=0.25.0",
    ],
    "distributed": [
        "redis>=5.0.0",
    ],
    "monitoring": [
        "prometheus-client>=0.19.0",
    ],
    "dev": [
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.12.0",
        "black>=23.12.0",
        "ruff>=0.1.0",
        "mypy>=1.8.0",
        "types-PyYAML",
        "types-aiofiles",
    ],
}

# Combine all optional dependencies
extras_require["all"] = list(set(sum([
    extras_require[key]
    for key in extras_require
    if key != "dev"
], [])))

setup(
    name="neurobus",
    version=version,
    author="Eshan Roy",
    author_email="eshanized@proton.me",
    description="The World's First Neuro-Semantic Event Bus for Cognitive AI Systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eshanized/neurobus",
    project_urls={
        "Bug Tracker": "https://github.com/eshanized/neurobus/issues",
        "Documentation": "https://neurobus.readthedocs.io",
        "Source Code": "https://github.com/eshanized/neurobus",
        "Changelog": "https://github.com/eshanized/neurobus/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*", "docs", "docs.*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Typing :: Typed",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.11",
    install_requires=install_requires,
    extras_require=extras_require,
    keywords=[
        "event-bus",
        "semantic-routing",
        "cognitive-ai",
        "llm",
        "vector-database",
        "event-sourcing",
        "microservices",
        "distributed-systems",
        "async",
        "ai-agents",
    ],
    include_package_data=True,
    zip_safe=False,
)
