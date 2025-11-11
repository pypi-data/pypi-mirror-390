from setuptools import setup, find_packages

with open("./README.md", "r") as f:
    readme_text = f.read()

setup(
    name="aerapi",  
    version="0.2.1",  
    description="A comprehensive toolset for accessing REST APIs used by the data team",
    author="S.Nicholson",
    author_email="sean.nicholson@aerlytix.com",
    packages=find_packages(), 
    install_requires=[
        "requests",
        "PyYAML"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",  
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    long_description=readme_text,
    long_description_content_type="text/markdown",
    python_requires='>=3.6', 
)
