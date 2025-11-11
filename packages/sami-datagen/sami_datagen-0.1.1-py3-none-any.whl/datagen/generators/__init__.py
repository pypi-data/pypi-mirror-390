"""
Data Generators Module

This module contains all data agenerators for the datagen library.
Each generator creates synthetic datasets for different domains.
"""

from datagen.generators.profile import generate_profiles
from datagen.generators.salary import generate_salaries
from datagen.generators.region import generate_regions
from datagen.generators.car import generate_cars

__all__ = [
    'generate_profiles',
    'generate_salaries',
    'generate_regions',
    'generate_cars',
]