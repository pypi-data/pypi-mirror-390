from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="zaicore",
    version="0.2.1",
    author="Muhammad Zaidan",
    author_email="muhammadzaidanfaiz8@gmail.com",
    description="ZAI Core — A lightweight modular AI framework with persistent memory.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muhammadzaidanf/ZAI-Core",
    project_urls={
        "Bug Tracker": "https://github.com/muhammadzaidanf/ZAI-Core/issues",
        "Documentation": "https://github.com/muhammadzaidanf/ZAI-Core#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.8",
)
