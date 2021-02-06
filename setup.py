#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="fuzzy-vendor-matching-webhook-python",
    description="Example Rossum webhook for vendor matching based on vendor name, address or VAT ID.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://developers.rossum.ai/",
    author="Rossum developers",
    author_email="support@rossum.ai",
    license="MIT",
    project_urls={
        "Source": "https://github.com/rossumai/fuzzy-vendor-matching-webhook-python",
        "Tracker": "https://github.com/rossumai/fuzzy-vendor-matching-webhook-python/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=("tests*",)),
    install_requires=[
        "Click",
        "et-xmlfile",
        "Flask",
        "itsdangerous",
        "jdcal",
        "Jinja2",
        "MarkupSafe",
        "openpyxl",
        "psycopg2",
        "Werkzeug",
    ],
    python_requires=">=3.6",
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov", "pytest-flask", "pytest-postgresql"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "fuzzy_vendor_matching_webhook_python"
            "= fuzzy_vendor_matching_webhook_python.app:entry_point"
        ]
    },
)
