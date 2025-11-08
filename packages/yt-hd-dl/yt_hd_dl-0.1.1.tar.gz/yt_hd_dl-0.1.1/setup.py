from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yt-hd-dl",
    version="0.1.1",
    author="DNhacker",
    author_email="darknighthacker0@gmail.com",
    description="A Python library to download YouTube videos in HD MP4 and MP3 formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
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
    ],
    python_requires=">=3.7",
    install_requires=[
        "pytube>=15.0.0",
        "moviepy>=1.0.3",
        "tqdm>=4.64.0",
    ],
    entry_points={
        "console_scripts": [
            "yt-hd-dl=yt_hd_dl.downloader:main",
        ],
    },
    keywords="youtube download video mp4 mp3 hd",
    url="https://github.com/DNhacker/yt-dl",
)