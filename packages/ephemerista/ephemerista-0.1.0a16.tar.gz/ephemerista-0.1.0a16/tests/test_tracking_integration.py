"""Integration tests for antenna tracking functionality."""

import numpy as np
import pytest

from ephemerista.analysis.link_budget import LinkBudget
from ephemerista.assets import Asset, GroundStation, Spacecraft
from ephemerista.comms.antennas import SimpleAntenna
from ephemerista.comms.channels import Channel
from ephemerista.comms.frequencies import Frequency
from ephemerista.comms.receiver import SimpleReceiver
from ephemerista.comms.systems import CommunicationSystem
from ephemerista.comms.transmitter import Transmitter
from ephemerista.constellation.design import Constellation, WalkerDelta
from ephemerista.coords.twobody import Keplerian
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator
from ephemerista.scenarios import Scenario
from ephemerista.time import Time, TimeDelta


def test_asset_tracking_api():
    """Test the asset tracking API."""
    # Create time for orbit
    time = Time.from_utc("2024-01-01T00:00:00Z")

    # Create assets
    gs = Asset(name="Test GS", model=GroundStation.from_lla(longitude=0, latitude=0, altitude=0))

    # Create spacecraft with proper orbit
    orbit = Keplerian.from_elements(
        time=time,
        semi_major_axis=7000,  # km
        eccentricity=0,
        inclination=0,
        ascending_node=0,
        periapsis_argument=0,
        anomaly=0,
    )
    sc = Asset(name="Test SC", model=Spacecraft(propagator=SemiAnalyticalPropagator(state_init=orbit)))

    # Test single asset tracking
    gs.track(asset_ids=sc.asset_id)
    assert gs.tracked_object_ids == [sc.asset_id]
    assert gs.tracked_constellation_ids == []

    # Test multiple asset tracking
    orbit2 = Keplerian.from_elements(
        time=time,
        semi_major_axis=7200,  # km, slightly different
        eccentricity=0,
        inclination=0,
        ascending_node=0,
        periapsis_argument=0,
        anomaly=90,
    )
    sc2 = Asset(name="Test SC2", model=Spacecraft(propagator=SemiAnalyticalPropagator(state_init=orbit2)))
    gs.track(asset_ids=[sc.asset_id, sc2.asset_id])
    assert set(gs.tracked_object_ids) == {sc.asset_id, sc2.asset_id}

    # Test constellation tracking
    # Earth radius + altitude = semi_major_axis
    earth_radius = 6371  # km
    altitude = 550  # km
    constellation = Constellation(
        model=WalkerDelta(
            nsats=4,
            nplanes=2,
            inclination=45,
            semi_major_axis=earth_radius + altitude,
            eccentricity=0,
            periapsis_argument=0,
            time=time,
        ),
        name="Test Constellation",
    )
    gs.track(constellation_ids=constellation.constellation_id)
    assert gs.tracked_constellation_ids == [constellation.constellation_id]
    assert gs.tracked_object_ids == []  # Should clear asset tracking

    # Test combined tracking
    gs.track(asset_ids=[sc.asset_id], constellation_ids=[constellation.constellation_id])
    assert gs.tracked_object_ids == [sc.asset_id]
    assert gs.tracked_constellation_ids == [constellation.constellation_id]

    # Test clearing tracking
    gs.track()
    assert gs.tracked_object_ids == []
    assert gs.tracked_constellation_ids == []


def test_tracking_with_link_budget(phasma_scenario_manual, phasma_sc_with_comms, phasma_ground_stations):
    """Test that tracking affects link budget angles correctly."""
    # Get first ground station and spacecraft
    gs = phasma_ground_stations[0]
    sc = phasma_sc_with_comms

    # Configure mutual tracking
    gs.track(asset_ids=sc.asset_id)
    sc.track(asset_ids=gs.asset_id)

    # Set specific pointing errors
    gs.pointing_error = 0.5
    sc.pointing_error = 0.2

    # Run link budget analysis
    lb = LinkBudget(scenario=phasma_scenario_manual)
    results = lb.analyze()

    # Check that angles match pointing errors when tracking
    for link in results[gs, sc]:
        for stat in link.stats:
            if link.link_type == "uplink":
                # GS transmits, SC receives
                assert stat.tx_angle.degrees == pytest.approx(gs.pointing_error, rel=1e-3)
                assert stat.rx_angle.degrees == pytest.approx(sc.pointing_error, rel=1e-3)
            else:
                # SC transmits, GS receives
                assert stat.tx_angle.degrees == pytest.approx(sc.pointing_error, rel=1e-3)
                assert stat.rx_angle.degrees == pytest.approx(gs.pointing_error, rel=1e-3)


def test_constellation_tracking(phasma_scenario_manual, phasma_ground_stations):
    """Test tracking of constellation members."""
    # Create a small constellation
    earth_radius = 6371  # km
    altitude = 550  # km
    constellation = Constellation(
        model=WalkerDelta(
            nsats=3,
            nplanes=1,
            inclination=45,
            semi_major_axis=earth_radius + altitude,
            eccentricity=0,
            periapsis_argument=0,
            time=phasma_scenario_manual.start_time,
        ),
        name="Test Constellation",
    )

    # Add communication systems to constellation satellites
    channel = Channel(link_type="downlink", modulation="BPSK", data_rate=1e6, required_eb_n0=10.0, margin=3.0)
    comms = CommunicationSystem(
        channels=[channel.channel_id],
        transmitter=Transmitter(power=1.0, frequency=Frequency.gigahertz(2.2), line_loss=0.0),
        antenna=SimpleAntenna(gain_db=5.0, beamwidth_deg=40.0),
    )
    constellation.comms = [comms]

    # Add constellation to scenario
    phasma_scenario_manual.constellations.append(constellation)
    phasma_scenario_manual.channels.append(channel)

    # Configure ground station to track constellation
    gs = phasma_ground_stations[0]
    gs.track(constellation_ids=constellation.constellation_id)

    # Add receiver to ground station
    gs_comms = CommunicationSystem(
        channels=[channel.channel_id],
        receiver=SimpleReceiver(frequency=Frequency.gigahertz(2.2), system_noise_temperature=290),
        antenna=SimpleAntenna(gain_db=30.0, beamwidth_deg=5.0),
    )
    gs.comms.append(gs_comms)

    # Run link budget analysis
    lb = LinkBudget(scenario=phasma_scenario_manual)
    results = lb.analyze()

    # Check that ground station tracks constellation members
    constellation_assets = constellation.assets
    for sat in constellation_assets:
        links = results[gs, sat]
        if links:  # If there are visible passes
            for link in links:
                for stat in link.stats:
                    # When tracking constellation, should use pointing error
                    assert stat.rx_angle.degrees == pytest.approx(gs.pointing_error, rel=1e-3)


def test_multi_target_tracking():
    """Test that multi-target tracking selects the closest target."""
    # Create scenario
    start_time = Time.from_utc("2024-01-01T00:00:00Z")
    scenario = Scenario(
        name="Multi-target tracking test", start_time=start_time, end_time=start_time + TimeDelta.from_minutes(10)
    )

    # Create ground station at equator
    gs = Asset(name="Equator GS", model=GroundStation.from_lla(longitude=0, latitude=0, altitude=0))

    # Create two satellites at different positions
    # SC1 passes directly overhead (closer)
    sc1_orbit = Keplerian.from_elements(
        time=start_time,
        semi_major_axis=7000,  # km
        eccentricity=0,
        inclination=0,  # Equatorial orbit
        ascending_node=0,
        periapsis_argument=0,
        anomaly=0,
    )

    # SC2 in inclined orbit (farther)
    sc2_orbit = Keplerian.from_elements(
        time=start_time,
        semi_major_axis=7000,  # km
        eccentricity=0,
        inclination=45,  # Inclined orbit
        ascending_node=0,
        periapsis_argument=0,
        anomaly=0,
    )

    sc1 = Asset(name="SC1", model=Spacecraft(propagator=SemiAnalyticalPropagator(state_init=sc1_orbit)))
    sc2 = Asset(name="SC2", model=Spacecraft(propagator=SemiAnalyticalPropagator(state_init=sc2_orbit)))

    # Configure ground station to track both satellites
    gs.track(asset_ids=[sc1.asset_id, sc2.asset_id])

    # Add communication systems
    channel = Channel(link_type="uplink", modulation="BPSK", data_rate=1e6, required_eb_n0=10.0, margin=3.0)
    gs_comms = CommunicationSystem(
        channels=[channel.channel_id],
        transmitter=Transmitter(power=10.0, frequency=Frequency.gigahertz(2.2), line_loss=0.0),
        antenna=SimpleAntenna(gain_db=30.0, beamwidth_deg=5.0),
    )
    sc_comms = CommunicationSystem(
        channels=[channel.channel_id],
        receiver=SimpleReceiver(frequency=Frequency.gigahertz(2.2), system_noise_temperature=290),
        antenna=SimpleAntenna(gain_db=5.0, beamwidth_deg=40.0),
    )

    gs.comms = [gs_comms]
    sc1.comms = [sc_comms]
    sc2.comms = [sc_comms]

    # Add to scenario
    scenario.assets.append(gs)
    scenario.assets.append(sc1)
    scenario.assets.append(sc2)
    scenario.channels.append(channel)

    # Analyze
    lb = LinkBudget(scenario=scenario)
    results = lb.analyze()

    # When tracking multiple targets, the GS should point to the closest one
    # This would result in smaller angles for SC1 (overhead) than SC2 (inclined)
    links_sc1 = results[gs, sc1]
    links_sc2 = results[gs, sc2]

    if links_sc1 and links_sc2:
        # Compare average angles - SC1 should have smaller angles
        avg_angle_sc1 = np.mean([stat.tx_angle.degrees for link in links_sc1 for stat in link.stats])
        avg_angle_sc2 = np.mean([stat.tx_angle.degrees for link in links_sc2 for stat in link.stats])

        # The ground station tracks both, but SC1 passes closer so should have smaller average angle
        assert avg_angle_sc1 < avg_angle_sc2
