# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Made IPython and folium optional dependencies for visualization
- Visualization module now imports gracefully if dependencies not installed
- Fixed test failures in CI/CD by adding API key environment variable
- Updated all GitHub URLs to point to correct repository (reneignacio/iniamet-library)
- Added conftest.py to automatically set test API key for CI

### Changed
- Moved visualization dependencies to optional `[viz]` extra
- Install with `pip install iniamet[viz]` to use visualization features
- Updated installation instructions in README

### Security
- **BREAKING CHANGE**: Removed hardcoded API key for security
- Users must now configure their own API key (see README)
- Added three methods for API key configuration:
  1. Config file (easiest): `python -m iniamet.config set-key YOUR-KEY`
  2. Environment variable: `INIA_API_KEY`
  3. Direct in code: `INIAClient(api_key='YOUR-KEY')`
- Added helpful error messages when API key is not configured
- Config file stored with restrictive permissions

## [0.1.0] - 2025-11-07

### Added
- Initial release of INIAMET library
- `INIAClient` high-level API for station data access
- `RegionalDownloader` for bulk regional data downloads
- `QualityControl` module with comprehensive data validation
  - Extreme value checks (WMO standards)
  - Stuck sensor detection (persistence test)
  - Temporal consistency validation
  - Suspicious zero detection
- `Visualization` module with Folium-based mapping
  - Station location maps
  - Temperature heatmaps
  - Interactive popup information
- Smart station code handling (10 different network types)
- Regional filtering by Chilean regions (R01-R16)
- Built-in caching system for faster repeated queries
- Type hints throughout the codebase
- pandas DataFrame integration
- Automated temperature download examples
  - Regional multi-station downloader
  - Configurable date ranges
  - Hourly vs 15-minute data options
  - Automatic quality control integration
  - CSV export with 2-decimal precision

### Supported Features
- **Station Management**: Query 400+ stations across Chile
- **Variables**: Temperature, precipitation, humidity, wind, radiation, pressure
- **Regions**: All 16 Chilean regions supported
- **Data Formats**: pandas DataFrames, CSV export
- **Quality Control**: 4-level validation system
- **Caching**: Local file-based cache for offline access
- **Visualization**: Interactive HTML maps with Folium

### Dependencies
- requests >= 2.28.0
- pandas >= 1.5.0
- numpy >= 1.23.0
- folium >= 0.14.0

### Known Issues
- Folium HeatMap temporarily disabled due to compatibility issue
- API key hardcoded (will be moved to environment variable in 0.2.0)

### Documentation
- Complete README with examples
- Quick Reference guide
- Recipe collection for common tasks
- Function reference documentation

[Unreleased]: https://github.com/yourusername/iniamet/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/iniamet/releases/tag/v0.1.0
