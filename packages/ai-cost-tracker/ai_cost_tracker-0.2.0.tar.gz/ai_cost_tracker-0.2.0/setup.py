#!/usr/bin/env python3
"""
Setup script for OpenAI Cost Tracker
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read version
version_file = Path(__file__).parent / "openai_cost_tracker" / "__init__.py"
version = "0.2.0"
if version_file.exists():
    for line in version_file.read_text().split("\n"):
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="ai-cost-tracker",
    version=version,
    author="OpenAI Cost Tracker Contributors",
    author_email="",
    description="Zero-config OpenAI API cost tracking - just one import and you're done!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dhruvildarji/ai-cost-tracker",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
    ],
    extras_require={
        "email": [
            "python-dotenv>=1.0.0",
            "requests>=2.28.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openai-cost-tracker=openai_cost_tracker.cli:main",
            "openai-cost-view=openai_cost_tracker.cli.view_costs:main",
            "openai-cost-scan=openai_cost_tracker.cli.scan:main",
            "openai-cost-monitor=openai_cost_tracker.cli.monitor:main",
            "openai-cost-config-email=openai_cost_tracker.cli.config_email:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

