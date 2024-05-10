from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='auto_di_tag',
    version='0.1.0',
    description='finds music files in directory, renames them and tags them with ID3 tags use for https://github.com/Klassenserver7b/Danceinterpreter',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/klassenserver7b/AutoDITag',
    author='klassenserver7b',
    author_email='klassenserver7bwin10@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='m3u m3u8 playlist dance tag id3',
    python_requires='>=3.10',
    install_requires=['mutagen', 'argparse'],
    extras_require={},
    project_urls={
        'Bug Reports': 'https://github.com/klassenserver7b/AutoDITag/issues',
        'Source': 'https://github.com/klassenserver7b/AutoDITag',
    },
    entry_points={
        'console_scripts': [
            f'{alias}=auto_di_tag:main'
        for alias in ('auto_di_tag', 'auto-di-tag', 'autoditag', 'ditag')],
    },
)