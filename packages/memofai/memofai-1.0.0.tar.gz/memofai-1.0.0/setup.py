"""Setup script for memofai package."""

from setuptools import setup, find_packages
import os

# Read version from version.py
version_file = os.path.join(os.path.dirname(__file__), "memofai", "version.py")
with open(version_file, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("SDK_VERSION"):
            version = line.split("=")[1].strip().strip("'\"")
            break

# Read long description from README
readme_file = os.path.join(os.path.dirname(__file__), "README.md")
with open(readme_file, "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="memofai",
    version=version,
    author="Memory-of-Agents Team",
    author_email="dev@memof.ai",
    description="Official Python SDK for Memory-of-Agents (MOA) - AI memory infrastructure for intelligent applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://memof.ai",
    project_urls={
        "Documentation": "https://docs.memof.ai",
        "Source": "https://github.com/memof-ai/memofai-python-sdk",
        "Issues": "https://github.com/memof-ai/memofai-python-sdk/issues",
        "Changelog": "https://github.com/memof-ai/memofai-python-sdk/blob/main/CHANGELOG.md",
    },
    packages=find_packages(exclude=["tests", "tests.*", "demo", "demo.*"]),
    package_data={
        "memofai": ["py.typed"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0,<3.0.0",
        "urllib3>=1.26.0,<3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
            "types-requests>=2.28.0",
        ],
    },
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Typing :: Typed",
    ],
    keywords="memofai moa memory-of-agents ai-memory ai memory agents sdk python llm chatbot agent-memory",
    license="MIT",
    zip_safe=False,
)
