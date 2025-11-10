from setuptools import setup, find_packages

setup(
    name="cryptionx",
    version="1.0.0",
    author="Matttz",
    author_email="proactivestudiocomercial@gmail.com",
    description="Simple and transparent encryption library for everyone.",
    long_description="CryptionX is a lightweight cryptography library designed for developers who want full control and modularity without depending on third-party libraries. It supports multiple stream ciphers, key exchange mechanisms, message integrity verification and more.",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
