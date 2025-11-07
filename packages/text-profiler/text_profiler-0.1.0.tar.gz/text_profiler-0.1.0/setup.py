from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="text-profiler",  # The name on PyPI
    version="0.1.0",       # Your first version
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple library for quick text statistics and profiling.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/text_profiler", # URL to your project
    packages=find_packages(),  # Automatically find the 'text_profiler' package
    
    # Classifiers help users find your project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.6",  # Minimum Python version
    install_requires=[],      # No dependencies! This is a plus.
)