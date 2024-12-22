# setup.py
from setuptools import setup, find_packages

setup(
    name="contract_advisor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'camel',
        # 其他依赖包
    ],
)