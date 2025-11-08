"""
TalkLabs STT SDK - Setup Configuration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="talklabs-stt",
    version="1.0.3",
    author="Francisco Lima",
    author_email="franciscorllima@gmail.com",
    description="TalkLabs STT SDK - Speech-to-Text API compatible with Deepgram",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://talklabs.com.br",
    project_urls={
        "Source": "https://github.com/talklabs/talklabs-stt",
    },
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "websockets>=15.0",
        "python-dotenv>=1.0.0",
        "soundfile>=0.12.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0",
            "pytest-mock>=3.10.0",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    keywords="speech-to-text stt transcription audio deepgram talklabs",
)
