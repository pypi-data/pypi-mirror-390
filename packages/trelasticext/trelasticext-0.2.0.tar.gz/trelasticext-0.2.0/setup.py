from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trelasticext",
    version="0.2.0",
    author="Hadar Miller",
    author_email="hadar.miller@example.com",
    description="Elasticsearch Extensions for Hebrew and Multi-language Text Processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/millerhadar/trelasticext",
    project_urls={
        "Bug Tracker": "https://github.com/millerhadar/trelasticext/issues",
        "Documentation": "https://github.com/millerhadar/trelasticext#readme",
        "Source Code": "https://github.com/millerhadar/trelasticext",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Database",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "elasticsearch>=7.0.0,<9.0.0",
        "pandas>=1.3.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
    keywords="elasticsearch hebrew tokenizer nlp text-processing linguistics",
    include_package_data=True,
    zip_safe=False,
)
