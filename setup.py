from setuptools import setup

setup(
    name='premine',
    version='0.0.7',
    install_requires=[
        'pandas',
        'sudachipy',
        'sudachidict_core',
        'cloudscraper',
        'beautifulsoup4',
        'requests',
        'genanki',
        'jaconv'
    ],
    package_dir={'': 'src'},
    packages=['premine', 'premine.anki', 'premine.data_sources']
)
