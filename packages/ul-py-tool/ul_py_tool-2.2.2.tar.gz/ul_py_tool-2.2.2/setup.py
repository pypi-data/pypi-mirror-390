from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='ul_py_tool',
    version='2.2.2',
    description='Python ul py tool',
    author='Unic-lab',
    author_email='',
    url='https://gitlab.neroelectronics.by/unic-lab/libraries/common-python-utils/ul-py-tool.git',
    packages=find_packages(include=['ul_py_tool*']),
    platforms='any',
    package_data={
        '': [
            'conf/*',
        ],
        'ul_py_tool': [
            'py.typed',
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
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
    entry_points={
        "console_scripts": [
            'ulpytool=ul_py_tool.main:main',
        ],
    },
    include_package_data=True,
    install_requires=[
        "numpy>=1.23.3, <2.0.0",
        "pandas==1.4.3",
        "pydantic[mypy]==2.10.5",
        "pydantic-i18n==0.2.3",
        "PyYAML==6.0",
        "colored==1.4.3",
        "rich==12.6.0",
        "tomli==2.0.1",
        "requests>=2.28.1, <3.0.0",

        "deepdiff>=5.8.1",

        "mypy>=1.9.0, <2.0.0",
        "types-pyyaml>=6.0.11",
        "types-pytz>=2022.1.2",
        "types-python-dateutil>=2.8.19",
        "types-setuptools>=63.4.0",
        "typing-extensions>=4.3.0",
        "data-science-types>=0.2.23",
        "types-requests>=2.28.8",

        "black>=24.4.0",
        "ruff>=0.4.1, <2.0.0",
        "isort[colors]==5.13.2",
        "yamllint==1.35.1",

        "pytest>=8.1.1",
        "pytest-cov==5.0.0",
        "python-gitlab==4.4.0",
        "kubernetes==23.6.0",

        "wheel==0.43.0",
        "twine==5.0.0",
        "setuptools==69.5.1",
    ],
)
