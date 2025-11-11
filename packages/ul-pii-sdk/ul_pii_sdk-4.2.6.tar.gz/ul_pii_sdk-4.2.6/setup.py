from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ul_pii_sdk',
    version='4.2.6',
    description='Pii sdk',
    author='Unic-lab',
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_data={
        "pii_sdk": [
            'py.typed',
        ],
    },
    packages=find_packages(include=['pii_sdk*']),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    platforms='any',
    install_requires=[
        'ul-api-utils>=7.2.8',
        'ul-data-aggregator-sdk>=10.1.7',
        # "ul-api-utils>=9.2.7",
        # "bcrypt==3.2.0",
        # "passlib==1.7.4",
        # "ul-notification-sdk-iot-account==3.0.6",
        # "ul-py-tool==2.1.4,
        # "ul-api-utils==9.1.1"
        # "ul-db-utils==5.1.0",
        # 'ul-data-aggregator-sdk>=10.5.1',
    ],
)
