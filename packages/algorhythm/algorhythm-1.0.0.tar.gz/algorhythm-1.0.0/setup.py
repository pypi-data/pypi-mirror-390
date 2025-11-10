# setup.py
from setuptools import setup, find_packages

setup(
    name="algorhythm",
    version="1.0.0",
    description="A Python library for real-time audio synthesis, pattern sequencing, and generative music.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Niamh Callinan Keenan",
    author_email="ncallinank@gmail.com",
    url="https://github.com/Niamhck/algorhythm",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "sounddevice>=0.4.0",
        "scipy>=1.7.0"
    ],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Sound Synthesis",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English"
    ],
    include_package_data=True,
    package_data={
        # Include any non-Python files here if needed, e.g.:
        # 'algorhythm': ['data/*.txt'],
    },
    entry_points={
        # Optionally add CLI entry points here
    },
)
