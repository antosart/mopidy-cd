from __future__ import unicode_literals

import re

from setuptools import find_packages, setup


def get_version(filename):
    content = open(filename).read()
    metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", content))
    return metadata['version']


setup(
    name='Mopidy-Cd',
    version=get_version('mopidy_cd/__init__.py'),
    url='https://github.com/forscher21/mopidy-cd',
    license='Apache License, Version 2.0',
    author='Antonio Sartori',
    author_email='antonio217@web.de',
    description='Mopidy extension to play audio CDs',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'setuptools',
        'Mopidy >= 0.14',
        'Pykka >= 1.1',
        'discid >= 1.1',
        'musicbrainzngs >= 0.6',
    ],
    entry_points={
        'mopidy.ext': [
            'cd = mopidy_cd:Extension',
        ],
    },
    classifiers=[
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Multimedia :: Sound/Audio :: Players',
    ],
)
