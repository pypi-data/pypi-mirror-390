from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of your README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')  # Add encoding parameter

setup(
    name='dw-compare',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
    ],
    author='Mohd Azmat',
    author_email='azmat.siddique.98@gmail.com',
    description='A Python CLI tool that compares two tabular datasets and reports what truly changed',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    project_urls={
        'Source Repository': 'https://github.com/azmatsiddique/dw-compare'
    }
)