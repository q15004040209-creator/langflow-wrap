from setuptools import setup, find_packages

setup(
    name="langflow-wrap",
    version="0.1.0",
    description="Python wrapper for Langflow AI workflow platform",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="q15004040209-creator",
    author_email="q15004040209@example.com",
    url="https://github.com/q15004040209-creator/langflow-wrap",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[],
    extras_require={
        "dev": ["pytest", "requests", "black", "mypy"]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Artificial Intelligence",
    ],
    license="MIT",
)