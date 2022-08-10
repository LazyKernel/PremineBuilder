from setuptools import setup

setup(
    name='premine',
    version='0.0.1',
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
    packages=['premine']
)
