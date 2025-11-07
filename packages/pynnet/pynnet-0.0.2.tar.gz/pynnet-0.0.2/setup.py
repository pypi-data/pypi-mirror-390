import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynnet",
    version="0.0.2",  # Incrementing version number for the README update
    author="Zain Qamar",
    author_email="zainqamarch@gmail.com",
    description="A simple neural network library built from scratch in Python ensuring easy application and understanding of artificial neural networks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/prime-programmer-ar/pynnet_project.git",
    license="CC-BY-NC-SA-4.0",
    
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy>=1.20.0',
    ],
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.7',
)