from setuptools import setup, find_packages

setup(
    name="zaicore",
    version="0.1.0",
    author="Muhammad Zaidan",
    author_email="muhammadzaidanfaiz8@gmail.com",
    description="A lightweight modular AI framework for learning and experimentation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/muhammadzaidanf/ZAI-Core",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
)
