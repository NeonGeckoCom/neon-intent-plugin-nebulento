#!/usr/bin/env python3
from setuptools import setup

PLUGIN_ENTRY_POINT = 'neon-intent-plugin-nebulento=neon_intent_plugin_nebulento:NebulentoExtractor'
setup(
    name='neon-intent-plugin-nebulento',
    version='0.0.1',
    description='A intent plugin for mycroft',
    url='https://github.com/NeonGeckoCom/neon-intent-plugin-nebulento',
    author='JarbasAi',
    author_email='jarbasai@mailfence.com',
    license='Apache-2.0',
    packages=['neon_intent_plugin_nebulento'],
    install_requires=["ovos-plugin-manager", "nebulento"],
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={'intentbox.intent': PLUGIN_ENTRY_POINT}
)
