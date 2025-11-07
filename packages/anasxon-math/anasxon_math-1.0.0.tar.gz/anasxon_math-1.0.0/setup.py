from setuptools import setup, find_packages

setup(
    name='anasxon_math',
    version='1.0.0',
    description='A collection of mathematical tools and utilities',
    author='Anasxon Ummataliy',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=['numpy>=1.18.0',],
    python_requires='>=3.6',
    license='MIT',
)
