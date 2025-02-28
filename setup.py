from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()


setup(
    name="vvvtslipsync",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vvvtslipsync=vvvtslipsync.__main__:main"
        ]
    },
    author="Your Name",
    description="Integration of VOICEVOX and VTubeStudio for lipsync",
    url="https://github.com/yourusername/vv-vts-lipsync",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
)
