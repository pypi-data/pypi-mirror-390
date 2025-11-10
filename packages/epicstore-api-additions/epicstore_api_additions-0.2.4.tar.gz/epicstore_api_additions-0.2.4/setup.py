from pathlib import Path

import setuptools

AUTHOR = 'fcorz'
VERSION = '0.2.4'

long_description = Path("README.md").read_text()

setuptools.setup(
    name='epicstore_api_additions',
    version=VERSION,
    author=AUTHOR,
    description='An API wrapper for Epic Games Store with additional features (fork of epicstore_api)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fcorz/epicstore_api_additions',
    license='MIT',
    include_package_data=True,
    install_requires=['cloudscraper>=1.2.71'],
    download_url=f'https://github.com/fcorz/epicstore_api_additions/archive/v_{VERSION}.tar.gz',
    packages=setuptools.find_packages(),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
)
