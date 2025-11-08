from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="payagency-api",
    version="1.1.0",
    author="PaneruVipin",
    author_email="support@pay.agency",
    description="A comprehensive Python SDK for PayAgency payment processing platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vp-payomatix/payagency-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
        "cryptography>=3.4.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.812",
        ],
    },
    keywords="payagency payment api sdk cryptocurrency payout card",
)
