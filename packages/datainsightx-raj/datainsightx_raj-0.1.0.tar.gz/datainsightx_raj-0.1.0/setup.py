from setuptools import setup, find_packages

setup(
    name='datainsightx-raj',  # Must be unique across PyPI
    version='0.1.0',
    author='RAJALINGAMT',
    author_email='raju031001@gmail.com',
    description='A lightweight data quality and visualization toolkit for pandas DataFrames',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/TRajalingam/datainsightx-raj',
    packages=find_packages(),
    install_requires=['pandas', 'numpy', 'plotly', 'jinja2'],
    entry_points={
        'console_scripts': ['datainsightx=datainsightx.cli:main']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
