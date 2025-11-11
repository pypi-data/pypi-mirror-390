from setuptools import setup, find_packages

setup(
    name="toolkitify",
    version="0.0.1",
    packages=find_packages(),
    description="Everything you need for your project.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="TPEOficial LLC",
    author_email="support@tpeoficial.com",
    url="https://github.com/TPEOficial/dymo-api-python",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.6",
    license="Apache-2.0"
)