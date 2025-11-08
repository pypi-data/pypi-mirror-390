import os
from pathlib import Path

import geojson_pydantic
import jdk4py
import numpy as np
import pytest

import ephemerista
from ephemerista.analysis.link_budget import LinkBudget
from ephemerista.analysis.visibility import Visibility
from ephemerista.angles import Angle
from ephemerista.assets import Asset, GroundStation, Spacecraft
from ephemerista.bodies import Origin
from ephemerista.comms.antennas import Antenna, SimpleAntenna
from ephemerista.comms.channels import Channel
from ephemerista.comms.frequencies import Frequency
from ephemerista.comms.receiver import Receiver, SimpleReceiver
from ephemerista.comms.systems import CommunicationSystem
from ephemerista.comms.transmitter import Transmitter
from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import GEO, LEO, MEO, SSO, Cartesian
from ephemerista.propagators.sgp4 import SGP4
from ephemerista.scenarios import Scenario
from ephemerista.time import Time, TimeDelta

RESOURCES = Path(__file__).parent.joinpath("resources")
EOP_PATH = RESOURCES.joinpath("finals2000A.all.csv")
SPK_PATH = RESOURCES.joinpath("de440s.bsp")

# Always use the bundled JDK when testing
os.environ["JAVA_HOME"] = str(jdk4py.JAVA_HOME)


@pytest.fixture(scope="session", autouse=True)
def init():
    ephemerista.init(eop_path=EOP_PATH, spk_path=SPK_PATH)


@pytest.fixture(scope="session")
def iss_tle():
    return """ISS (ZARYA)
1 25544U 98067A   24187.33936543 -.00002171  00000+0 -30369-4 0  9995
2 25544  51.6384 225.3932 0010337  32.2603  75.0138 15.49573527461367"""


@pytest.fixture(scope="session")
def iss_trajectory(iss_tle):
    propagator = SGP4(tle=iss_tle)
    start_time = propagator.time
    end_time = start_time + TimeDelta.from_minutes(100)
    times = start_time.trange(end_time, step=float(TimeDelta.from_minutes(1)))
    return propagator.propagate(times)


@pytest.fixture(scope="session")
def resources():
    return RESOURCES


@pytest.fixture(scope="session")
def phasma_scenario(resources):
    json = resources.joinpath("phasma/scenario.json").read_text()
    return Scenario.model_validate_json(json)


@pytest.fixture(scope="session")
def phasma_link_budget(phasma_scenario):
    lb = LinkBudget(scenario=phasma_scenario)
    return lb.analyze()


@pytest.fixture(scope="session")
def lunar_scenario(resources):
    json = resources.joinpath("lunar/scenario.json").read_text()
    return Scenario.model_validate_json(json)


@pytest.fixture(scope="session")
def lunar_visibility(lunar_scenario):
    vis = Visibility(scenario=lunar_scenario, bodies=[Origin(name="Moon")])
    return vis.analyze()


@pytest.fixture(scope="session")
def lunar_transfer(resources):
    return Trajectory.from_csv(resources.joinpath("lunar/lunar_transfer.csv"))


@pytest.fixture(scope="session")
def root_folder(resources):
    return resources.parent.parent


@pytest.fixture(scope="session")
def phasma_tle():
    return """
1 99878U 14900A   24103.76319466  .00000000  00000-0 -11394-2 0    01
2 99878  97.5138 156.7457 0016734 205.2381 161.2435 15.13998005    06"""


@pytest.fixture(scope="session")
def phasma_sc(phasma_tle) -> Asset:
    propagator = SGP4(tle=phasma_tle)
    return Asset(model=Spacecraft(propagator=propagator), name="PHASMA")


@pytest.fixture(scope="session")
def c0() -> Cartesian:
    """
    Returns a Cartesian state for the propagators
    """
    time = Time.from_iso("TDB", "2016-05-30T12:00:00")
    r = np.array([6068.27927, -1692.84394, -2516.61918])
    v = np.array([-0.660415582, 5.495938726, -5.303093233])

    return Cartesian.from_rv(time, r, v)


@pytest.fixture(scope="session")
def test_time() -> Time:
    """Standard test time for orbital fixtures."""
    return Time.from_components("TAI", 2024, 6, 1, 12, 0, 0.0)


@pytest.fixture(scope="session")
def earth_origin() -> Origin:
    """Earth origin for orbital fixtures."""
    return Origin(name="Earth")


@pytest.fixture(scope="session")
def leo_iss(test_time, earth_origin) -> LEO:
    """ISS-like Low Earth Orbit fixture."""
    return LEO(time=test_time, altitude=408.0, inclination=51.6, origin=earth_origin)


@pytest.fixture(scope="session")
def meo_gps(test_time, earth_origin) -> MEO:
    """GPS-like Medium Earth Orbit fixture."""
    return MEO(time=test_time, altitude=20200.0, inclination=55.0, origin=earth_origin)


@pytest.fixture(scope="session")
def geo_satellite(test_time, earth_origin) -> GEO:
    """Geostationary orbit fixture."""
    return GEO(time=test_time, longitude=0.0, origin=earth_origin)


@pytest.fixture(scope="session")
def sso_landsat(test_time, earth_origin) -> SSO:
    """Landsat-like Sun-Synchronous Orbit fixture."""
    return SSO(time=test_time, altitude=705.0, ltan=10.0, origin=earth_origin)


def get_validated_coverage_geojson_dict(file_name: str, resources: Path | None = None) -> dict:
    """
    Returns a GeoJSON-like dict representing an AOI
    """
    resources_path = resources or RESOURCES
    with open(resources_path / "coverage" / file_name) as f:
        aoi = geojson_pydantic.FeatureCollection.model_validate_json(f.read())
        return aoi.__geo_interface__["features"][0]["geometry"]


@pytest.fixture(scope="session")
def aoi_geom_dict(resources) -> dict:
    """
    Returns a GeoJSON-like dict representing an AOI
    """
    return get_validated_coverage_geojson_dict(resources=resources, file_name="single_aoi.geojson")


@pytest.fixture(scope="session")
def nav_scenario(resources) -> Scenario:
    with open(resources.joinpath("navigation", "galileo_tle.txt")) as f:
        lines = f.readlines()

    start_time = Time.from_components("TAI", 2025, 1, 27)
    end_time = Time.from_components("TAI", 2025, 1, 28)

    assets = [Asset(name="ESOC", model=GroundStation.from_lla(8.622778, 49.871111))]
    for i in range(0, len(lines), 3):
        tle = lines[i : i + 3]
        name = tle[0].strip()
        assets.append(Asset(name=name, model=Spacecraft(propagator=SGP4(tle="".join(tle)))))

    return Scenario(start_time=start_time, end_time=end_time, assets=assets)


@pytest.fixture(scope="session")
def slant_range() -> float:
    return 2192.92  # km


@pytest.fixture(scope="session")
def frequency() -> Frequency:
    return Frequency.megahertz(2308.0)


@pytest.fixture(scope="session")
def gs_antenna(frequency) -> Antenna:
    return SimpleAntenna(gain_db=30, beamwidth_deg=5, design_frequency=frequency)


@pytest.fixture(scope="session")
def gs_transmitter(frequency) -> Transmitter:
    return Transmitter(power=4, frequency=frequency, line_loss=1.0)


@pytest.fixture(scope="session")
def gs_receiver(frequency) -> Receiver:
    return SimpleReceiver(system_noise_temperature=889, frequency=frequency)


@pytest.fixture(scope="session")
def uplink() -> Channel:
    return Channel(link_type="uplink", modulation="BPSK", data_rate=430502, required_eb_n0=2.3, margin=3)


@pytest.fixture(scope="session")
def downlink() -> Channel:
    return Channel(link_type="downlink", modulation="BPSK", data_rate=861004, required_eb_n0=4.2, margin=3)


@pytest.fixture(scope="session")
def gs_system(uplink, downlink, gs_transmitter, gs_receiver, gs_antenna) -> CommunicationSystem:
    return CommunicationSystem(
        channels=[uplink.channel_id, downlink.channel_id],
        transmitter=gs_transmitter,
        receiver=gs_receiver,
        antenna=gs_antenna,
    )


@pytest.fixture(scope="session")
def sc_antenna(frequency) -> Antenna:
    return SimpleAntenna(gain_db=6.5, beamwidth_deg=60, design_frequency=frequency)


@pytest.fixture(scope="session")
def sc_transmitter(frequency) -> Transmitter:
    return Transmitter(power=1.348, frequency=frequency, line_loss=1.0)


@pytest.fixture(scope="session")
def sc_receiver(frequency) -> Receiver:
    return SimpleReceiver(system_noise_temperature=429, frequency=frequency)


@pytest.fixture(scope="session")
def sc_system(uplink, downlink, sc_transmitter, sc_receiver, sc_antenna) -> CommunicationSystem:
    return CommunicationSystem(
        channels=[uplink.channel_id, downlink.channel_id],
        transmitter=sc_transmitter,
        receiver=sc_receiver,
        antenna=sc_antenna,
    )


@pytest.fixture  # Do not use session scope here, because we might modify this object in a unit test
def phasma_sc_with_comms(phasma_sc, sc_system) -> Asset:
    return phasma_sc.model_copy(update={"comms": [sc_system]})


@pytest.fixture  # Do not use session scope here, because we might modify this object in a unit test
def phasma_ground_stations(gs_system) -> list[Asset]:
    station_coordinates = [
        (38.017, 23.731),
        (36.971, 22.141),
        (35.501, 24.011),
        (39.326, -82.101),
        (50.750, 6.211),
    ]

    return [
        Asset(
            model=GroundStation.from_lla(longitude, latitude, minimum_elevation=Angle.from_degrees(10)),
            name=f"Station {i}",
            comms=[gs_system],
        )
        for i, (latitude, longitude) in enumerate(station_coordinates)
    ]


@pytest.fixture  # Do not use session scope here, because we might modify this object in a unit test
def phasma_scenario_manual(uplink, downlink, phasma_sc_with_comms, phasma_ground_stations) -> Scenario:
    start_date = phasma_sc_with_comms.model.propagator.time
    end_date = start_date + TimeDelta.from_days(1)

    return Scenario(
        assets=[*phasma_ground_stations, phasma_sc_with_comms],
        channels=[uplink, downlink],
        name="PHASMA Link Budget",
        start_time=start_date,
        end_time=end_date,
    )
