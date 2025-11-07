from setuptools import setup, find_packages

# Read the long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

# Core dependencies
install_requires = [
    'numpy>=1.20.0',
    'pandas>=1.3.0',
    'scikit-learn>=1.0.0',
    'scipy>=1.7.0',
]

# Optional dependencies
extras_require = {
    'torch': [
        'torch>=2.0.0',
        'tqdm>=4.60.0',
    ],
    'gnn': [
        'torch>=2.0.0',
        'torch-geometric>=2.3.0',
    ],
    'optimization': [
        'optuna>=3.0.0',
    ],
    'serving': [
        'faiss-cpu>=1.7.0',
        'fastapi>=0.100.0',
        'uvicorn>=0.23.0',
    ],
    'dev': [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'black>=23.0.0',
        'flake8>=6.0.0',
        'mypy>=1.0.0',
    ]
}

# Add 'all' option that includes everything
extras_require['all'] = list(set(sum(extras_require.values(), [])))

setup(
    name='sota-recommender',
    version='0.3.4',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
    author='Semen Lobachevskiy',
    author_email='hichnick@gmail.com',
    description='A modern, production-ready library for state-of-the-art recommender systems',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hichnicksemen/svd-recommender',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    keywords='recommender-systems, machine-learning, deep-learning, collaborative-filtering, matrix-factorization',
    project_urls={
        'Bug Reports': 'https://github.com/hichnicksemen/svd-recommender/issues',
        'Source': 'https://github.com/hichnicksemen/svd-recommender',
    },
)
