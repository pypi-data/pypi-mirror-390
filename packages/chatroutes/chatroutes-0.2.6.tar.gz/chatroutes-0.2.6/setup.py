from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chatroutes",
    version="0.2.6",
    author="ChatRoutes",
    author_email="support@chatroutes.com",
    description="Official Python SDK for ChatRoutes API - Conversation branching, AutoBranch, and multi-model AI chat",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chatroutes/chatroutes-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/chatroutes/chatroutes-python-sdk/issues",
        "Documentation": "https://docs.chatroutes.com",
        "Source Code": "https://github.com/chatroutes/chatroutes-python-sdk",
    },
    packages=find_packages(exclude=["tests*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ],
    },
    keywords="chatroutes ai chat conversation branching autobranch multi-model gpt claude api sdk",
)
