# setup.py
from setuptools import setup, find_packages

setup(
    name="plutofreeai",          # package name on pip
    version="0.1.0",
    packages=find_packages(),      # automatically find packages in your directory
    install_requires=[             # only external dependencies
        "requests",
        "beautifulsoup4",
        "lxml",
        "webscout",
    ],
    python_requires='>=3.8',
    author="Noah Olomu",
    author_email="noah_pvb@outlook.com",
    description="A free AI module that is easy to call",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HoryzenCodes/free_ai",  # optional
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
