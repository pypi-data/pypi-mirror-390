from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cellrepair_langchain",
    version="1.0.1",
    author="CellRepair Systems",
    author_email="ai@cellrepair.ai",
    description="LangChain integration for CellRepair.AI - Access 4882 autonomous agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PowerForYou74/cellrepair-langchain",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
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
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "requests>=2.25.0",
        "pydantic>=2.0.0",
    ],
    keywords=[
        "langchain",
        "ai",
        "agents",
        "multi-agent",
        "llm",
        "gpt",
        "claude",
        "gemini",
        "artificial-intelligence",
        "machine-learning",
        "collaboration",
        "tools",
        "langchain-tools",
        "ai-collaboration",
        "autonomous-agents"
    ],
    project_urls={
        "Bug Reports": "https://github.com/PowerForYou74/cellrepair-langchain/issues",
        "Source": "https://github.com/PowerForYou74/cellrepair-langchain",
        "Documentation": "https://cellrepair.ai/api/",
        "Get API Key": "https://cellrepair.ai/api/?utm_source=langchain&utm_medium=pypi",
        "Live Demo": "https://huggingface.co/spaces/cellrepair-systems/cellrepair-ai",
    },
)
