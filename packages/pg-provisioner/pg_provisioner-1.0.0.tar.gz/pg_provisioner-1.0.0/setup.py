from setuptools import setup, find_packages

setup(
    name="pg-provisioner",
    version="1.0.0",
    author="Causum™ Analytics",
    author_email="info@causum.ai",
    description="Python library for provisioning and managing PostgreSQL on AWS RDS.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/causum/pg-provisioner",
    
    # Code lives under src/
    package_dir={"": "src"},
    packages=find_packages(where="src"),

    # Python compatibility
    python_requires=">=3.10",

    # Runtime dependencies
    install_requires=[
        "boto3>=1.35.0",
        "botocore>=1.35.0",
        "psycopg2-binary>=2.9.9",
        "python-dotenv>=1.2.1",
        "typing-extensions>=4.10.0",
    ],

    # Optional development & testing dependencies
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "moto[rds,s3]>=5.0",
            "boto3-stubs[rds,s3,sts]>=1.35.0",
            "types-psycopg2>=2.9.21",
            "mypy>=1.10.0",
        ],
    },

    # Include type hints and any package data files
    include_package_data=True,
    package_data={
        "": ["py.typed"],
    },

    # Metadata
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)