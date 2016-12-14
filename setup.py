from setuptools import setup, find_packages

setup(
    name='fsfclient',
    version='1',
    packages=find_packages(),
    url='https://github.com/emersonelectricco/fsf',
    license='Apache 2.0',
    author='Adam Kniffen',
    author_email='akniffen@cisco.com',
    description='The FSF v1.0 Client',
    package_data={'': ['fsfclient.json']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fsfclient=fsfclient.fsf_client_cli:main'
        ]
    }
)