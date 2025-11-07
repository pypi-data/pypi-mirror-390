import io
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with io.open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
   long_description = f.read()

setup(
    name='signalr-unified-client',
    version='0.0.10',
    description='Fork of SignalR client for Python based on threads instead of gevent',
    long_description=long_description,
    url='https://github.com/your-org/signalr-unified-client',
    author='Andy Datewood',
    author_email='andy@datewood.net',
    license='Apache-2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    keywords='signalr',
    packages=find_packages(),
)
