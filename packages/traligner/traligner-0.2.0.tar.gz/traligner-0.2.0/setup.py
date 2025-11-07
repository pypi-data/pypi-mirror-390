from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="traligner",
    version="0.2.0",
    author="Hadar Miller",
    author_email="hadar.miller@example.com",
    description="Text Reuse Alignment for Hebrew and multi-language texts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/millerhadar/traligner",
    project_urls={
        "Bug Tracker": "https://github.com/millerhadar/traligner/issues",
        "Documentation": "https://github.com/millerhadar/traligner#readme",
        "Source Code": "https://github.com/millerhadar/traligner",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Information Analysis",
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
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "rapidfuzz>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.900",
        ],
        "elasticsearch": [
            "elasticsearch>=7.0.0,<9.0.0",
        ],
    },
    keywords="text-reuse alignment hebrew nlp linguistics text-analysis",
    include_package_data=True,
    zip_safe=False,
)
