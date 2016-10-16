#!/usr/bin/env python

from setuptools import setup

setup(
    name='pbtool',
    version='0.1.0',
    description='A tool for compiling, populating, and sending protobufs on the command line',
    author='Disha Garg, Eric Roy',
    license='MIT',
    keywords='protobuf protocol buffers',
    package_dir={'': 'src'},
    packages=['pbtool', 'pbtool.pbtool_bin', 'pbtool.pbtool_gui'],
    package_data={'pbtool.pbtool_bin': ['compiler/protoc.exe'], 'pbtool.pbtool_gui': ['wheels/*.whl'], 'pbtool': ['pbtool_gui/tutorial.proto']},
    install_requires=['protobuf==2.6.1', 'requests==2.9.1'],
    entry_points={
        'console_scripts': [
            'pbtool_bin=pbtool.pbtool_bin.script:main',
            'pbtool_gui=pbtool.pbtool_gui.protobuf:main',
        ],
    }
)
