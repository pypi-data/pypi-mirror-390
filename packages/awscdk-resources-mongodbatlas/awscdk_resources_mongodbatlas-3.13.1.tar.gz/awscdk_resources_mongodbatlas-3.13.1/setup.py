import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "awscdk_resources_mongodbatlas",
    "version": "3.13.1",
    "description": "MongoDB Atlas CDK Construct Library for AWS CloudFormation Resources",
    "license": "Apache-2.0",
    "url": "https://github.com/mongodb/awscdk-resources-mongodbatlas.git",
    "long_description_content_type": "text/markdown",
    "author": "MongoDB",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/mongodb/awscdk-resources-mongodbatlas.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "awscdk_resources_mongodbatlas",
        "awscdk_resources_mongodbatlas._jsii"
    ],
    "package_data": {
        "awscdk_resources_mongodbatlas._jsii": [
            "awscdk-resources-mongodbatlas@3.13.1.jsii.tgz"
        ],
        "awscdk_resources_mongodbatlas": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.200.1, <3.0.0",
        "constructs>=10.0.5, <11.0.0",
        "jsii>=1.118.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard>=2.13.3,<4.3.0"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
