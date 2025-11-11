# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-11-10

### Added
- Comprehensive debug control system with `DEBUG` flags in all modules
- Debug file output control (all debug files now respect DEBUG flag)
- Progress bar control (tqdm now respects DEBUG flag)
- Economic routing variants (econ_mapping, econ_benefit, econ_paths, econ_route)
- Pydantic V2 support with ConfigDict
- Complete PyPI packaging support
- Proper `__init__.py` with version and metadata
- Comprehensive README.md with usage examples
- LICENSE file (EUPL-1.2)
- MANIFEST.in for proper package distribution
- Development dependencies in pyproject.toml

### Changed
- Migrated from Poetry to modern setuptools with pyproject.toml
- Updated requirements.txt with all missing dependencies (scipy, scikit-learn, pydantic, tqdm)
- Organized requirements by category with comments
- Changed version constraints from `==` to `>=` for better compatibility
- Updated pyproject.toml with complete metadata and classifiers
- Improved setup.py with proper package metadata

### Fixed
- All debug terminal prints now respect DEBUG flag (10 modules)
- All debug file outputs now respect DEBUG flag (16+ files)
- tqdm progress bars now conditional on DEBUG flag
- Pydantic V2 deprecation warning (migrated to ConfigDict)
- Missing dependencies in requirements.txt

### Removed
- Removed unused debug_config.py file
- Cleaned up orphaned debug infrastructure

## [0.1.15] - 2024-09-18

### Added
- Initial release with basic routing functionality
- Point mapping to road networks
- Benefit calculation for route segments
- Path finding with Dijkstra algorithm
- Route optimization with ACO (Ant Colony Optimization)
- Hull points extraction for optimal sensor placement
- OpenStreetMap integration via OSMnx
- Geospatial data processing with GeoPandas

### Features
- Support for EPSG:25832 and EPSG:31468 coordinate systems
- Network-based routing with real road data
- Information value maximization
- Convex hull analysis
- Command-line interface

## [Unreleased]

### Planned
- Unit tests with pytest
- Continuous integration setup
- Performance optimizations
- Additional routing algorithms
- Web-based visualization tools
- API documentation with Sphinx
- Example notebooks
- Docker containerization

---

## Version History

- **0.2.0** - PyPI-ready release with complete packaging
- **0.1.15** - Initial functional release
