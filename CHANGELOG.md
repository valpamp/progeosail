# Changelog

## 2.1.0 - Unreleased

- Add GeoSail support through `run_progeosail`, `geocone`, and `geocyli`.
- Rename the import package from `prosail` to `progeosail`.
- Implement Huemmrich's instantaneous absorbed-radiation fraction (`GSFR`) for cone and cylinder crowns.
- Export the legacy `geocily` spelling as an alias for `geocyli`.
- Fix the upstream FourSAIL directional reflectance bug that double-counted `rsod`.
- Add regression tests against Huemmrich's Aspen and Spruce GeoSail examples.
- Modernize package metadata for PyPI builds through `pyproject.toml`.
- Update CI to test Python 3.10, 3.11, and 3.12.
