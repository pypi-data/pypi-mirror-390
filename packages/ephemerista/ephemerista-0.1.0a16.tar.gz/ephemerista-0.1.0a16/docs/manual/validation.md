# Validation

Ephemerista's analysis modules have been validated against established tools and libraries to ensure accuracy and reliability.

## Validation Status

| Component | Validation Method | Test Cases |
|-----------|------------------|------------|
| Orbital dynamics | Based on Orekit, which is independently validated | [test_orekitprops.py](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/blob/main/tests/test_orekitprops.py), [test_orekitprops_java.py](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/blob/main/tests/test_orekitprops_java.py) |
| Visibility analysis | Validated against NASA GMAT, which is based on SPICE | [test_visibility.py](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/blob/main/tests/test_visibility.py) |
| Link budget analysis | Cross-validated with existing LSF tools and MATLAB Satellite Communications Toolbox | [test_link_budget.py](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/blob/main/tests/test_link_budget.py) |
| Interference analysis | Validated against MATLAB Satellite Communications Toolbox | [test_link_budget.py](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/blob/main/tests/test_link_budget.py) |
| Coverage analysis | Manual checks against existing constellations | [test_coverage.py](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/blob/main/tests/test_coverage.py) |
| Navigation analysis | Based on Orekit, which is independently validated | [test_requirements.py](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/blob/main/tests/test_requirements.py) |
