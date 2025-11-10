from setuptools import setup, find_packages

setup(
    name="bhashini-client",
    version="0.1.3",
    author="Sai",
    author_email="digitalindiabhashinidivision@gmail.com",
    description="A Python client for interacting with Bhashini inference services (ASR, NMT, TTS).",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/bhashini-client",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
