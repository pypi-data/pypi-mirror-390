from setuptools import setup, find_packages

setup(
    name="expreess",
    version="0.2.3",
    packages=find_packages(),
    install_requires=[],
    author="Aayush Singh",
    author_email="youremail@example.com",
    description="A simple greeting module called expreess",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/expreess",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
