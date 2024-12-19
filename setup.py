import os
from setuptools import setup, find_packages

# Read long description from README.rst
if os.path.exists('README.md'):
    long_description = open('README.md').read()
else:
    long_description = (
        'PyMVPA is a Python module for multivariate pattern analysis (MVPA) '
        'of fMRI datasets with a high-level interface that is easy to learn '
        'and use, building on numpy, scipy, matplotlib, nibabel, h5py, '
        'scikit-learn, joblib, and, optionally, other packages for '
        'neuroimaging, machine learning, and psychophysics.'
    )

setup(
    name='PyMVPA',
    version='3.0.3',
    description='Multivariate Pattern Analysis in Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='PyMVPA Developers',
    author_email='developers@pymvpa.org',
    url='https://github.com/MVPA-Solutions/PyMVPA',
    packages=find_packages(),
    install_requires=[
        'scipy',
        'nibabel',
        'h5py',
        'joblib',
        'scikit-learn',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.7',
    project_urls={
        'Source': 'https://github.com/MVPA-Solutions/PyMVPA',
        'Bug Reports': 'https://github.com/MVPA-Solutions/PyMVPA/issues',
        'Original Project': 'https://github.com/PyMVPA/PyMVPA',
    },
)