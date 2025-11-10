import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "simple-agentcore-runtime-patterns",
    "version": "0.0.0",
    "description": "AWS CDK construct library for deploying Bedrock AgentCore Runtime",
    "license": "MIT-0",
    "url": "https://github.com/ivorycirrus/simple-agentcore-construct.git",
    "long_description_content_type": "text/markdown",
    "author": "@ivorycirrus<ivorycirrus@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/ivorycirrus/simple-agentcore-construct.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "simple_agentcore_runtime_patterns",
        "simple_agentcore_runtime_patterns._jsii"
    ],
    "package_data": {
        "simple_agentcore_runtime_patterns._jsii": [
            "simple-agentcore-runtime-patterns@0.0.0.jsii.tgz"
        ],
        "simple_agentcore_runtime_patterns": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "aws-cdk-lib>=2.221.0, <3.0.0",
        "cdk-ecr-deployment>=4.0.3, <5.0.0",
        "cdk-nag>=2.37.55, <3.0.0",
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
