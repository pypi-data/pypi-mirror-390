from setuptools import setup, find_packages

setup(
    name='pynadlan',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'httpx',
    ],
    author='Your Name',
    author_email='bensterenson@gmail.com',
    description='A Python wrapper for the israel Nadlan prices.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/bensterenson/pynadlan',
) 