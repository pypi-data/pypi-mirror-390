from setuptools import setup, find_packages

setup(
    name="vibedish-api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip() 
        for line in open('/Users/pranshav/Desktop/SE/CSC510-Section2-Group8/Project/requirements.txt').readlines()
    ],
    author="Pranshav Patel",
    description="VibeDish - Mood-based food delivery API",
    url="https://github.com/pranshavpatel/CSC510-Section2-Group8",
    python_requires='>=3.10',
)