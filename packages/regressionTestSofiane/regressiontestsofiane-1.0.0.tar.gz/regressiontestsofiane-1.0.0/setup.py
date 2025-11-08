from setuptools import setup, find_packages

setup(
    name='regressionTestSofiane',
    version='1.0.0',
    author='Bensetallah sofiane',
    author_email='rtsof91@gmail.com',
    packages=find_packages(),
    description='A simple linear regression implementation from scratch (by Sofiane)',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=['numpy'],
    url='https://pypi.org/project/regressionTestSofiane/',
    license='LICENSE.txt',
)
