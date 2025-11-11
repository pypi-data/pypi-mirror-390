"""
Sensor Routing - Optimal routing for CRNS sensor data collection

This package provides tools for calculating optimal routes for mobile sensor data collection,
specifically designed for Cosmic Ray Neutron Sensing (CRNS) applications.
"""

__version__ = "0.2.0"
__author__ = "Can Topaclioglu"
__email__ = "can.topaclioglu@ufz.de"
__license__ = "EUPL-1.2"

# Import main modules for easier access
from . import point_mapping
from . import benefit_calculation
from . import path_finding
from . import route_finding
from . import hull_points_extraction
from . import econ_mapping
from . import econ_benefit
from . import econ_paths
from . import econ_route

__all__ = [
    "point_mapping",
    "benefit_calculation",
    "path_finding",
    "route_finding",
    "hull_points_extraction",
    "econ_mapping",
    "econ_benefit",
    "econ_paths",
    "econ_route",
]
