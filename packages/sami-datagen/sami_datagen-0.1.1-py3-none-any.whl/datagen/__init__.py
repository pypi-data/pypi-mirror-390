"""
DataGen - Sythetic Data Generation Library

A python library for generating realistic sythetic datasets for testing,
analytics, and machine learning experiments.

Author: Sami
"""

__version__ = "0.1.0"

# Import all generators for easy access
from datagen.generators.profile import generate_profiles
from datagen.generators.salary import generate_salaries
from datagen.generators.region import generate_regions
from datagen.generators.car import generate_cars

# Import utility functions
from datagen.utils.io import save_data

__all__ = [
    # Version
    '__version__',

    # Generators
    'generate_profiles',
    'generate_salaries',
    'generate_regions',
    'generate_cars',

    # Utilities
    'save_data',
]