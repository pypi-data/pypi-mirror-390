"""
Setup script for Cadence package
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="cadence-punctuation",
    version="1.0.5",
    author="AI4Bhārat",  
    author_email="opensource@ai4bharat.org", 
    description="Multilingual punctuation restoration model for Indic languages",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/AI4Bharat/Cadence", 
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.9",
    install_requires=[
        "torch>=2.1.0",
        "transformers>=4.51.3",
        "safetensors>=0.4.1",
        "numpy>=1.21.0",
        "huggingface-hub>=0.30.2",
    ],
    include_package_data=True,
    package_data={
        "cadence": ["py.typed"],
    },
)