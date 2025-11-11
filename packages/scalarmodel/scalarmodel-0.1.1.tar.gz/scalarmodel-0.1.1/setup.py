from setuptools import setup, find_packages

setup(
    name='scalarmodel',  # your package name
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'scikit-learn',
        'tensorflow',
        'seaborn'
    ],
    author='sch',
    description='My ML functions for California Housing and Fashion MNIST',
    url='',  # optional
)
