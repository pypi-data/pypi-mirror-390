from setuptools import setup, find_packages

setup(
    name='ray_helper',
    version='0.1.0',
    description='A simple package to convert text to uppercase',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
    ],
)
