from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yemot-ai",
    version="0.1.0",
    author="Heskishar F.",
    author_email="heskisharf@gmail.com",
    description="חבילת Python לחיבור סוכני AI למערכות ימות המשיח",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/heskisharf/yemot-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Telephony",
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
        "yemot-flow>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
        ],
    },
    keywords="yemot ai ivr telephony voice codex openai",
    project_urls={
        "Bug Reports": "https://github.com/heskisharf/yemot-ai/issues",
        "Source": "https://github.com/heskisharf/yemot-ai",
        "Documentation": "https://github.com/heskisharf/yemot-ai#readme",
    },
)