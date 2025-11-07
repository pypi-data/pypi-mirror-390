from setuptools import setup, find_packages

setup(
    name="talklabs",
    version="2.1.3",
    author="Francisco Lima",
    author_email="franciscorllima@gmail.com",
    description="TalkLabs SDK - Ultra-low latency Text-to-Speech with intelligent streaming and persistent sessions (ElevenLabs compatible)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://talklabs.com.br",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "requests>=2.28.0",
        "websockets>=15.0",
        "python-dotenv>=1.0.0"
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
