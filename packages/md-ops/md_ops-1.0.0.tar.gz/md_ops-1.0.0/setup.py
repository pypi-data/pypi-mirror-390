from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="md-ops",
    version="1.0.0",
    author="Consult Anubhav",
    description="Convert Markdown <-> DOCX easily with full formatting support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/consultanubhav/gpt2docx-be",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: Other/Proprietary License",
    ],
    python_requires=">=3.7",
    install_requires=[
        "python-docx>=0.8.11",
        "markdown2>=2.4.0",
    ],
    keywords="markdown docx converter word document md",
    project_urls={
        "Bug Reports": "https://github.com/consultanubhav/gpt2docx-be/issues",
        "Source": "https://github.com/consultanubhav/gpt2docx-be",
    },
)
