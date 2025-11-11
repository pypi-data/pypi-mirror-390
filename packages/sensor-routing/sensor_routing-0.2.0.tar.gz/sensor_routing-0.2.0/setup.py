"""
Setup script for sensor-routing package.
This file provides backward compatibility for older build tools.
The main configuration is in pyproject.toml.
"""
from setuptools import setup, find_packages
import os

# Read the README file
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Optimal routing for CRNS mobile sensor data collection"

setup(
    name='sensor-routing',
    version='0.2.0',
    description='Optimal routing for CRNS mobile sensor data collection',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Can Topaclioglu',
    author_email='can.topaclioglu@ufz.de',
    url='https://codebase.helmholtz.cloud/ufz/tb5-smm/met/wg7/sensor-routing',
    packages=find_packages(exclude=['tests', 'tests.*', 'build', 'dist', 'venv', 'work_dir', 'auxillary']),
    python_requires='>=3.12',
    install_requires=[
        'numpy>=2.2.0',
        'pandas>=2.2.3',
        'geopandas>=1.0.1',
        'osmnx>=2.0.0',
        'shapely>=2.0.6',
        'pyproj>=3.7.0',
        'pyogrio>=0.10.0',
        'networkx>=3.4.2',
        'scipy>=1.11.0',
        'scikit-learn>=1.3.0',
        'pydantic>=2.0.0',
        'annotated-types>=0.6.0',
        'tqdm>=4.66.0',
        'requests>=2.32.3',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.5.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'sensor-routing=sensor_routing.full_pipeline_cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    keywords='sensor-routing CRNS cosmic-ray-neutron-sensing geospatial routing-optimization',
    project_urls={
        'Source': 'https://codebase.helmholtz.cloud/ufz/tb5-smm/met/wg7/sensor-routing',
        'Issues': 'https://codebase.helmholtz.cloud/ufz/tb5-smm/met/wg7/sensor-routing/-/issues',
    },
)
