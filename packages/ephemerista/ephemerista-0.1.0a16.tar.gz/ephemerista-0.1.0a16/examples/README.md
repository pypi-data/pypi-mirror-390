# Ephemerista Examples

This directory contains example data files and Jupyter notebooks demonstrating the capabilities of Ephemerista.

## For Users Who Installed via pip

If you installed Ephemerista using `pip install ephemerista`, you don't have these example files locally. You can download them from the GitLab repository:

### Download Options

#### Option 1: Download Entire Examples Directory

```bash
# Download and extract examples directory
wget https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/archive/main/ephemerista-simulator-main.zip?path=examples -O examples.zip
unzip examples.zip
mv ephemerista-simulator-main-examples/examples .
rm -rf ephemerista-simulator-main-examples examples.zip
```

#### Option 2: Clone the Repository

```bash
git clone https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator.git
cd ephemerista-simulator/examples
```

#### Option 3: Download Individual Files

Individual files can be downloaded directly from GitLab. See the file list below for direct links.

## Example Files

### Jupyter Notebooks

Interactive tutorials demonstrating Ephemerista features:

- `01-basics.ipynb` - Basic satellite orbit propagation and visualization
- `02-orekit_features.ipynb` - Advanced propagation with Orekit
- `03-visibility.ipynb` - Visibility analysis between spacecraft and ground stations
- `04-antennas.ipynb` - Antenna modeling and pattern visualization
- `05-link_budget.ipynb` - RF link budget calculations
- `06-constellations.ipynb` - Constellation design (Walker, Streets-of-Coverage)
- `07-coverage.ipynb` - Coverage analysis over areas of interest
- `08-navigation.ipynb` - GNSS dilution of precision analysis

### Scenario Files (`scenarios/`)

Pre-configured mission scenarios in JSON format:

| File | Size | Description | Download Link |
|------|------|-------------|---------------|
| `coverage.json` | 2.4 KB | Coverage analysis scenario | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/scenarios/coverage.json) |
| `lunar.json` | 405 KB | Lunar transfer mission with ground stations | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/scenarios/lunar.json) |
| `navigation.json` | 15 KB | GNSS navigation scenario | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/scenarios/navigation.json) |
| `phasma.json` | 8.3 KB | PHASMA mission scenario | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/scenarios/phasma.json) |
| `phasma_interference.json` | 10.6 KB | PHASMA with interference analysis | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/scenarios/phasma_interference.json) |

### GeoJSON Area of Interest Files

Geographic areas for coverage analysis:

| File | Description | Download Link |
|------|-------------|---------------|
| `half_earth.geojson` | Hemisphere coverage area | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/half_earth.geojson) |
| `simple_polygons.geojson` | Multiple polygon areas | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/simple_polygons.geojson) |
| `single_aoi.geojson` | Single area of interest | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/single_aoi.geojson) |

### Navigation Data (`navigation/`)

| File | Size | Description | Download Link |
|------|------|-------------|---------------|
| `galileo_tle.txt` | 5.0 KB | TLE data for Galileo constellation satellites | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/navigation/galileo_tle.txt) |

### Antenna Pattern Files (`antennas/`)

| File | Size | Description | Download Link |
|------|------|-------------|---------------|
| `cylindricalDipole.pln` | 9.1 KB | MSI antenna pattern file from MATLAB | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/antennas/cylindricalDipole.pln) |

### CCSDS Orbit Files

| File | Description | Download Link |
|------|-------------|---------------|
| `OEMExample5.txt` | Example CCSDS Orbit Ephemeris Message | [Download](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/raw/main/examples/OEMExample5.txt) |

### Performance Test Data (`performance/`)

GeoJSON files for performance testing of coverage algorithms.

## Usage in Documentation Examples

When following examples in the documentation, ensure your working directory has access to these files. The documentation assumes paths relative to a working directory that contains an `examples/` subdirectory.

For example, if the documentation shows:
```python
scenario = Scenario.load_from_file("examples/scenarios/lunar.json")
```

You should either:
1. Run your code from the parent directory of `examples/`
2. Adjust the path based on your working directory location

## Required Runtime Data

In addition to these example files, Ephemerista requires the following data files to run (these must be downloaded separately):

1. **Earth Orientation Parameters**: [finals2000A.all.csv](https://datacenter.iers.org/data/csv/finals2000A.all.csv) (~3.8 MB)
2. **Planetary Ephemerides**: [de440s.bsp](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp) (~32.7 MB)
3. **Orekit Data**: [orekit-data-main.zip](https://gitlab.orekit.org/orekit/orekit-data/-/archive/main/orekit-data-main.zip)
   - Alternative: `pip install orekitdata`

See the main [README.md](../README.md) for more information on initializing Ephemerista with these data files.

## Contributing Examples

If you've created interesting examples or scenarios, consider contributing them back to the project! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

Example files are distributed under the same [AGPLv3](https://choosealicense.com/licenses/agpl-3.0/) license as the Ephemerista library.
