"""
Setup configuration for evolvishub-text-classification-llm library.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

# Version
version = "1.1.0"

# Core dependencies
core_deps = [
    "pydantic>=2.0.0",
    "asyncio-throttle>=1.0.0",
    "aiofiles>=23.0.0",
    "httpx>=0.25.0",
    "pyyaml>=6.0",
    "python-dateutil>=2.8.0",
]

# Provider-specific dependencies
openai_deps = ["openai>=1.3.0"]
anthropic_deps = ["anthropic>=0.7.0"]
google_deps = ["google-generativeai>=0.3.0"]
cohere_deps = ["cohere>=4.0.0"]
azure_deps = ["openai>=1.3.0", "azure-identity>=1.15.0"]
bedrock_deps = ["boto3>=1.34.0", "botocore>=1.34.0"]
huggingface_deps = [
    "transformers>=4.36.0",
    "torch>=2.1.0",
    "accelerate>=0.25.0",
    "bitsandbytes>=0.41.0",
    "sentencepiece>=0.1.99"
]
ollama_deps = ["ollama>=0.1.0"]

# Workflow dependencies
langgraph_deps = ["langgraph>=0.0.26", "langchain-core>=0.1.0"]

# Monitoring dependencies
monitoring_deps = [
    "prometheus-client>=0.19.0",
    "structlog>=23.2.0",
    "psutil>=5.9.0"
]

# Caching dependencies
caching_deps = ["redis>=5.0.0", "diskcache>=5.6.0"]

# Security dependencies
security_deps = ["cryptography>=41.0.0", "bleach>=6.1.0"]

# Development dependencies
dev_deps = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.12.0",
    "pytest-cov>=4.1.0",
    "black>=23.11.0",
    "isort>=5.12.0",
    "flake8>=6.1.0",
    "mypy>=1.7.0",
    "pre-commit>=3.6.0",
    "sphinx>=7.2.0",
    "sphinx-rtd-theme>=1.3.0",
    "jupyter>=1.0.0",
    "pandas>=2.1.0",  # For examples and data processing
]

# All dependencies
all_deps = (
    core_deps + openai_deps + anthropic_deps + google_deps + cohere_deps +
    azure_deps + bedrock_deps + huggingface_deps + ollama_deps +
    langgraph_deps + monitoring_deps + caching_deps + security_deps
)

setup(
    name="evolvishub-text-classification-llm",
    version=version,
    author="Alban Maxhuni, PhD",
    author_email="a.maxhuni@evolvis.ai",
    description="Enterprise-grade text classification library with enhanced multi-LLM provider support and structured classification output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/evolvishub/text-classification-llm",
    project_urls={
        "Documentation": "https://docs.evolvishub.com/text-classification-llm",
        "Source": "https://github.com/evolvishub/text-classification-llm",
        "Tracker": "https://github.com/evolvishub/text-classification-llm/issues",
    },
    packages=find_packages(exclude=['tests*', 'examples*']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.9",
    install_requires=core_deps,
    extras_require={
        # Individual providers
        "openai": openai_deps,
        "anthropic": anthropic_deps,
        "google": google_deps,
        "cohere": cohere_deps,
        "azure": azure_deps,
        "bedrock": bedrock_deps,
        "huggingface": huggingface_deps,
        "ollama": ollama_deps,
        
        # Provider groups
        "cloud": openai_deps + anthropic_deps + google_deps + cohere_deps,
        "local": huggingface_deps + ollama_deps,
        "enterprise": azure_deps + bedrock_deps,
        
        # Feature groups
        "workflows": langgraph_deps,
        "monitoring": monitoring_deps,
        "caching": caching_deps,
        "security": security_deps,
        
        # Complete installations
        "all": all_deps,
        "dev": all_deps + dev_deps,
    },
    entry_points={
        "console_scripts": [
            "tcllm=evolvishub_text_classification_llm.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "evolvishub_text_classification_llm": [
            "config/*.yaml",
            "config/*.json",
            "templates/*.txt",
            "examples/*.py",
        ],
    },
    keywords=[
        "text-classification", "llm", "nlp", "machine-learning", "ai",
        "openai", "anthropic", "huggingface", "transformers", "gpt",
        "claude", "gemini", "cohere", "enterprise", "async", "batch-processing"
    ],
    zip_safe=False,
)
