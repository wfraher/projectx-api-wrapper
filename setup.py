from setuptools import setup, find_packages

setup(
    name="projectx-api-wrapper",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
    ],
    author="William Fraher",
    author_email="williamfraher95@gmail.com",
    description="Python wrapper for the ProjectX Gateway API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/wfraher/projectx-api-wrapper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 