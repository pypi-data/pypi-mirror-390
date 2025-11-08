# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

### Development Commands
- `just test-unit` - Run unit tests (uses `uv run pytest`)
- `just test-examples` - Run example notebook tests
- `just test` - Run both unit tests and example tests
- `just lint` - Run style linting (ruff check + format check)
- `just fmt` - Format code with ruff
- `just build` - Build package (sdist and wheel)
- `just docs` - Build documentation
- `just docs-serve` - Serve docs with auto-rebuild

### Testing Specific Tests
- `uv run pytest tests/test_file.py::test_function` - Run specific test
- `uv run pytest tests/test_file.py -v` - Run all tests in file with verbose output
- `uv run pytest -k "test_pattern"` - Run tests matching pattern

### Package Management
- `uv` is used for dependency management and running commands
- Always prefix Python commands with `uv run` (e.g., `uv run python`, `uv run pytest`)

## Architecture Overview

### Core Structure
Ephemerista is a space mission analysis library focused on telecommunications and satellite constellation design. It builds on top of Orekit (Java) via JPype and lox-space for orbital mechanics.

### Key Components

**Initialization**: The library requires initialization via `ephemerista.init()` with Earth Orientation Parameters (EOP), planetary ephemerides (SPK), and Orekit data before use.

**Scenarios**: Central concept represented by the `Scenario` class in `scenarios.py`. Scenarios contain:
- Assets (spacecraft, ground stations) 
- Constellations
- Communication channels
- Areas/points of interest
- Time parameters

**Assets**: Defined in `assets.py`, include spacecraft and ground stations with associated communication systems and propagators.

**Propagation**: Multiple propagator types in `propagators/`:
- SGP4 for TLE-based propagation
- Numerical propagators (Orekit-based)
- Semi-analytical propagators
- OEM (Orbit Ephemeris Message) support

**Analysis Modules** in `analysis/`:
- **Visibility**: Computes visibility windows between ground stations and spacecraft
- **Coverage**: Analyzes coverage over areas of interest using visibility data
- **Link Budget**: RF link analysis between assets
- **Interference**: Interference analysis for communication links
- **Navigation**: GNSS dilution of precision analysis

**Communication Systems** in `comms/`:
- Antennas (simple, complex, patterns)
- Transmitters and receivers
- Channels and communication systems
- RF utilities and calculations

**Constellation Design** in `constellation/`:
- Walker Star and Walker Delta configurations
- Streets-of-Coverage patterns
- Flower constellations

### Critical Design Patterns

**Cached Properties**: The `Scenario.all_assets` property is cached using `@cached_property`. When modifying scenarios dynamically (e.g., in tests), clear the cache with `del scenario.__dict__['all_assets']` after changes.

**Asset Iteration**: Analysis modules should iterate over `scenario.all_assets` (not `scenario.assets`) to include both individual assets and constellation-generated assets.

**Ensemble Propagation**: Scenarios are propagated to create `Ensemble` objects containing trajectories for all assets. Analysis modules typically accept pre-computed ensembles for performance.

**Java Integration**: Heavy orbital mechanics computations use Orekit via JPype. The JVM is initialized during `ephemerista.init()`.

## Important Implementation Notes

### Performance Considerations
- Analysis modules can be computationally expensive for large scenarios
- Pre-filter assets by type before nested loops (see visibility.py optimization)
- Cache expensive function calls like `ephemeris()` and `get_eop_provider()`
- Consider using ensemble propagation results rather than re-propagating

### Testing Patterns
- Test data is in `tests/resources/`
- Fixtures in `conftest.py` provide common scenarios (phasma, navigation, etc.)
- When tests modify scenarios, ensure cached properties are cleared
- Use `@pytest.fixture(scope="session")` for expensive setup

### Data Dependencies
Tests require external data files (EOP, ephemeris) which should be placed in `tests/resources/` and initialized via `ephemerista.init()` in test setup.