# Module Structure

Ephemerista is structured into several larger subpackages and submodules.
The most important ones and their contents are listed below.
A full API reference listing all modules is provided in [the following section](#api-target).

## Time `ephemerista.time`

This module contains the `Time` class which models a timestamp in all relevant time scale and provides transformations between time scales and different input and output formats.

## Orbital Coordinates `ephemerista.coords`

This package contains several submodules which provide classes for representing spacecraft states as Cartesian states, Keplerian states, and trajectories.

## Orbital Propagators `ephemeris.propagators`

This packages provides access to orbit propagators from [Orekit] and other open source libraries.

## Communication System Models `ephemerista.comms`

This package contains several submodules which provide models of antennas, antenna gain patterns, transmitters, receivers, channels, and complete comms systems.

## Assets `ephemerista.assets` and Scenarios `ephemerista.scenarios`

These modules provide the capabilities to model space and ground assets with their respective communications payloads and simulate them together as part of scenarios.

## Constellation Design `ephemerista.constellation`

Scenarios with satellite constellations can also be automatically generated through the constellation design features of the `constellation`.

## Analyses `ephemerista.analysis`

This package provides several downstream analyses such as visibility, link budgets, or coverage that can be computed for each scenario.

[Orekit]: https://orekit.org