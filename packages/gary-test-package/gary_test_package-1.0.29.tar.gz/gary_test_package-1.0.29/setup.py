from setuptools import setup, find_packages
from packaging.version import Version
from os.path import exists

if exists("VERSION.txt"):
    with open("VERSION.txt", "r") as fh:
        version_string = fh.read()
else:
    version_string = "0.0.0"
version = Version(version_string)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='gary-test-package',
    description='This is a test package and is only a hello world app.',
    version=str(version),
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    author="Gary Schaetz",
    author_email='gary@schaetzkc.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='',
    keywords='',
    install_requires=[],
    include_package_data=True,
    entry_points={
        'console_scripts':
        ['gary-test-package=gary_test_package.gary_test:main'],
    }
)
