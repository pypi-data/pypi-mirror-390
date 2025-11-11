# setup.py
from setuptools import setup, find_packages

setup(
    name="rgbterminal",                   # Package name on PyPI
    version="0.3.0",                      # Initial version
    packages=find_packages(),             # Automatically find packages
    python_requires=">=3.10",             # Python version requirement
    install_requires=[
        "numpy>=1.25.0"
    ],

    # Metadata
    author="Ulus Vatansever",
    author_email="cvcvka5@gmail.com",
    description="A Python library for terminal-colored text with 256-color and truecolor support",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cvcvka5/rgbterminal",
    license="MIT",
    
    # Classifiers (PyPI metadata)
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries",
    ],
)
