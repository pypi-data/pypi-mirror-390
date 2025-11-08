from setuptools import setup

setup(
    name='paneric-di-container',
    version='1.0.0',
    py_modules=["DIContainer", "DIContainerInterface"],
    author='Tomasz Januszewicz',
    author_email='your.email@example.com',
    description='A simple dependency injection container.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://gitlab.com/python5471645/libs/paneric-di-container',
)
