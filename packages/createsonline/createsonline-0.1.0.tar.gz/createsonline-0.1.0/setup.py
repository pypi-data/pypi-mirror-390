from setuptools import setup, find_packages
from pathlib import Path

# Read the version from VERSION file
def get_version():
    version_file = Path(__file__).parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.1.0"  # fallback version

# Read the contents of your README file
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name="createsonline",
    version=get_version(),
    author="meahmedh",
    author_email="ahmed@createsonline.com",
    description="A framework for creating and deploying AI-powered applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meahmedh/createsonline",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    
    # 🚀 CLI ENTRY POINTS
    entry_points={
        "console_scripts": [
            # Main CLI command
            "createsonline=createsonline.cli.main:run_cli",
            # Django-style management command
            "createsonline-admin=createsonline.cli.manage:main",
        ]
    },
    
    # Package data to include templates, static files, etc.
    package_data={
        "createsonline": [
            # Ship HTML templates and all static assets actually used by the admin
            "templates/**/*.html",
            "static/**/*",
        ]
    },
    
    # Include additional files
    include_package_data=True,
    
    # Keywords for better discoverability
    keywords=[
        "web framework", 
        "ai framework",
        "artificial intelligence",
        "machine learning", 
        "async",
        "api",
        "web development",
        "llm",
        "vector database",
        "smart fields",
        "ai-native"
    ],
    
    # Project URLs
    project_urls={
        "Homepage": "https://github.com/meahmedh/createsonline",
        "Documentation": "https://docs.createsonline.com", 
        "Repository": "https://github.com/meahmedh/createsonline",
        "Bug Tracker": "https://github.com/meahmedh/createsonline/issues",
    },
    
    # Optional dependencies
    extras_require={
        # AI EXTERNAL SERVICES - COMING IN FUTURE VERSIONS
        # Currently using 100% internal implementations
        # Uncomment when external AI service support is ready
        # "ai": [
        #     "openai>=1.0.0",              # OpenAI API integration
        #     "anthropic>=0.18.0",          # Anthropic/Claude API integration
        #     "pandas>=2.0.0",              # Advanced data processing & Excel support
        #     "scikit-learn>=1.3.0",        # Advanced ML algorithms (sklearn fallback)
        #     "httpx>=0.25.0",              # Async HTTP client for AI APIs
        # ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        # ALL EXTRAS - COMING IN FUTURE VERSIONS
        # "all": [
        #     # AI dependencies (future)
        #     "openai>=1.0.0",
        #     "anthropic>=0.18.0",
        #     "pandas>=2.0.0",
        #     "scikit-learn>=1.3.0",
        #     "httpx>=0.25.0",
        #     # Dev dependencies (current)
        #     "pytest>=7.0.0",
        #     "pytest-asyncio>=0.21.0",
        #     "black>=23.0.0",
        #     "isort>=5.12.0",
        #     "mypy>=1.0.0",
        #     "pre-commit>=3.0.0",
        # ]
    },
    
    # Ensure package is not zipped
    zip_safe=False,
)
