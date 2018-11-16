from setuptools import setup, find_packages

requirements = [
    'drf_yasg',
    'setuptools',
    'djangorestframework-bulk'
]

setup(
    name='drf_yasg_bulk_extension',
    url='https://bitbucket.org/groovtech/drf_yasg_bulk_extension',
    author='Tuan Nguyen',
    author_email='tuan.nguyen@groovetechnology.com',
    packages=find_packages(),
    install_requires=requirements,
    version='0.1',
    license='MIT',
    description='A bulk api integration for drf_yasg',
    long_description=open('README.txt').read(),
)
