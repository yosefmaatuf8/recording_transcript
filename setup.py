from setuptools import setup, find_packages

setup(
    name="audio_transcription_interface",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "scipy",
        "numpy",
        "pyannote.audio",
        "pydub",
        "librosa",
        "requests",
        "tqdm",
        "gradio"
    ],
    author="yosef",
    author_email="yosefmaatuf848@gmail.com",
    description="Web interface for uploading and processing audio for transcription and speaker diarization.",
    long_description=open("README.md", encoding="utf-8").read(),

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7"
)
