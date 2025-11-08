from setuptools import setup, find_packages

setup(
    name='VKPyKit',
    version='0.1.2',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    description='Packaged functions for ML and Data Science tasks.',
    author='Vishal Khapre',
    author_email='assignarc@gmail.com',
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'seaborn',
        'scikit-learn',
        'IPython.display',
        'plotly.express',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    # packages=find_packages(
    #     where='src',
    #     include=['VKPyKit'],
    # ),
)
