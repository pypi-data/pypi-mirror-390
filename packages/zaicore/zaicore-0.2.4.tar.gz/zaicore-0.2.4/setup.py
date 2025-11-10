from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="zaicore",
    version="0.2.4",
    author="Muhammad Zaidan",
    author_email="muhammadzaidanfaiz8@gmail.com",
    description="ZAI Core — Adaptive Intelligence with auto-learn, insights, persistent & networked memory",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muhammadzaidanf/ZAI-Core",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["requests>=2.25"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Developers",
    ],
)
