from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lockedin-handeler",
    version="1.0.0",
    author="KAO",
    author_email="kao@overload.studio",
    description="A simple Python package for managing space availability in Convex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/convex-space-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "convex>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
    keywords="convex, space, management, database, real-time",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/convex-space-manager/issues",
        "Source": "https://github.com/yourusername/convex-space-manager",
    },
)
