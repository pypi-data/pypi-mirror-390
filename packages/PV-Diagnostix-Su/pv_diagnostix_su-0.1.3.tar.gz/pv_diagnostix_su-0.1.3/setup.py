from setuptools import setup, find_packages

setup(
    name="PV-Diagnostix-Su",
    version='0.1.3',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'scipy>=1.7.0',
        'scikit-learn>=1.0.0',
        'plotly>=5.0.0',
        'pathlib',
        'logging',
        'PyYAML>=6.0',
        'pywavelets'
    ],
    python_requires='>=3.8',
)
