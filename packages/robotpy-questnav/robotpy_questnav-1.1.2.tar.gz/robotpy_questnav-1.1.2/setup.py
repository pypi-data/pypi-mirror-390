from setuptools import setup, find_packages

setup(
    name="robotpy-questnav",
    version="1.1.2",
    packages=find_packages(include=["questnav", "questnav.*"]),
    description="QuestNav Library for Robotpy, works with pyhton now",
    author="Hayder Chammakhi",
    url="https://github.com/Ultime5528/FRC2025",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
