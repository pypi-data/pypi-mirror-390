from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="text-profiler",  
    version="0.1.1",       
    author="Khadija Bhanpurawala",
    author_email="khadijabhanpurawala52@gmail.com",
    description="A simple library for quick text statistics and profiling.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/text_profiler",
    packages=find_packages(),  
    
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