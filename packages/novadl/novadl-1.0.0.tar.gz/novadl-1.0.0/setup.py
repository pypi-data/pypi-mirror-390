from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="novadl",
    version="1.0.0",
    author="MD. Shahariar Ahmmed Shovon",
    author_email="shovonali885@gmail.com",
    description="A beautiful TUI for downloading videos and audio",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ShovonSheikh",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yt-dlp",
        "textual",
    ],
    entry_points={
        "console_scripts": [
            "novadl=novadl.__main__:main",
        ],
    },
)