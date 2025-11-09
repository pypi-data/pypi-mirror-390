"""
Termivox - Voice Recognition Bridge for Linux

Setup configuration for PyPI distribution.

♠️ Nyro: Package structure recursion - from source to distribution
🌿 Aureon: Opening the flow to others seeking voice freedom
🎸 JamAI: Building the release harmony
"""

from setuptools import setup, find_packages

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="termivox",
    version="0.1.2",
    author="Gerico",
    author_email="gerico@jgwill.com",
    description="Voice Recognition Bridge for Linux - Speak naturally, control your system, type hands-free",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gerico1007/termivox",
    project_urls={
        "Bug Tracker": "https://github.com/Gerico1007/termivox/issues",
        "Documentation": "https://github.com/Gerico1007/termivox#readme",
        "Source Code": "https://github.com/Gerico1007/termivox",
    },
    package_dir={"termivox": "src"},
    packages=["termivox", "termivox.voice", "termivox.bridge", "termivox.ui", "termivox.utils"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Desktop Environment",
        "Topic :: Adaptive Technologies",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        "vosk>=0.3.45",
        "pyaudio>=0.2.13",
        "numpy>=1.24.0",
        "pynput>=1.7.6",
        "pystray>=0.19.5",
        "Pillow>=10.0.0",
        "speechrecognition>=3.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "termivox=termivox.main:main",
            "termivox-test=termivox.test_voice_script:main",
            "termivox-download-model=termivox.download_model:main",
        ],
    },
    include_package_data=True,
    package_data={
        "termivox": ["../config/*.json"],
    },
    keywords="voice-recognition speech-to-text linux vosk accessibility hands-free dictation",
)
