from setuptools import setup, find_packages

setup(
    name="OmnissiahPrayer",
    version="1.0.1",
    author="CountZero",
    author_email="zdavidx007@gmail.com",
    description="A ritual Python program that invokes the Machine God.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CountZero-Error/OmnissiahPrayer",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.7",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Religion",
        "Topic :: Artistic Software",
        "Intended Audience :: Developers",
    ],
)