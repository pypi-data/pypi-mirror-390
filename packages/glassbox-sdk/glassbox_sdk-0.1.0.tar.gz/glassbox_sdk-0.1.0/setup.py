from setuptools import setup, find_packages
from pathlib import Path

# Read README for long_description
this_directory = Path(__file__).parent
# README.md is in the root directory (2 levels up from sdk/python)
readme_path = this_directory.parent.parent / "README.md"
if not readme_path.exists():
    # Fallback: try current directory
    readme_path = this_directory / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else "See Your AI Costs in Real-Time"

setup(
    name="glassbox-sdk",
    version="0.1.0",
    author="Hudson Bales",
    author_email="hudson@glassbox.ai",
    description="See Your AI Costs in Real-Time",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HudsonBales/glassbox",
    project_urls={
        "Bug Reports": "https://github.com/HudsonBales/glassbox/issues",
        "Source": "https://github.com/HudsonBales/glassbox",
        "Documentation": "https://github.com/HudsonBales/glassbox#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0,<3.0.0",
        "websockets>=12.0,<13.0.0; python_version>='3.8'",
    ],
    extras_require={
        "test": [
            "pytest>=7.4.3,<8.0.0",
            "pytest-cov>=4.1.0,<5.0.0",
            "pytest-mock>=3.12.0,<4.0.0",
        ],
        "dev": [
            "pytest>=7.4.3,<8.0.0",
            "pytest-cov>=4.1.0,<5.0.0",
            "pytest-mock>=3.12.0,<4.0.0",
            "black>=23.12.1,<24.0.0",
            "flake8>=6.1.0,<7.0.0",
            "mypy>=1.7.1,<2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "glassbox=glassbox_sdk.cli:main",
        ],
    },
    keywords="ai, observability, monitoring, costs, terminal, cli, openai, anthropic, gpt-4, claude",
)

