from setuptools import setup, find_packages

setup(
    name="smart-budgeting-pkg",                 # <-- pick a unique name
    version="0.1.0",
    description="Reusable budget projections & anomaly checks for Spendwise",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Manojkumar",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial",
    ],
    project_urls={
        "Homepage": "https://example.com/smart-budgeting-pkg",
        "Changelog": "https://example.com/smart-budgeting-pkg/changelog",
    },
)
