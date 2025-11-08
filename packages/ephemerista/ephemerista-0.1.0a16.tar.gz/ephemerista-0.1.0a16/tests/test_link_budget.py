import numpy as np
import pandas as pd
import pytest
from scipy.io import loadmat

from ephemerista.analysis.link_budget import LinkBudget, LinkBudgetResults
from ephemerista.angles import Angle
from ephemerista.assets import Asset, GroundStation, Spacecraft
from ephemerista.comms.antennas import ComplexAntenna, GaussianPattern
from ephemerista.comms.channels import Channel
from ephemerista.comms.frequencies import Frequency
from ephemerista.comms.receiver import SimpleReceiver
from ephemerista.comms.systems import CommunicationSystem
from ephemerista.comms.transmitter import Transmitter
from ephemerista.comms.utils import free_space_path_loss, from_db
from ephemerista.coords.twobody import Keplerian
from ephemerista.propagators.orekit.semianalytical import SemiAnalyticalPropagator
from ephemerista.propagators.sgp4 import SGP4
from ephemerista.scenarios import Scenario
from ephemerista.time import Time, TimeDelta


def test_fspl(slant_range, frequency):
    assert free_space_path_loss(slant_range, frequency) == pytest.approx(166, rel=1e-1)


def test_gs_transmitter(gs_transmitter, gs_antenna):
    assert gs_transmitter.equivalent_isotropic_radiated_power(gs_antenna, 0.0) == pytest.approx(35.0, rel=1e-1)


def test_gs_receiver(gs_receiver, gs_antenna):
    expected = -4.99 + 3 + 1.5 + 1
    assert gs_receiver.gain_to_noise_temperature(gs_antenna, 0.0) == pytest.approx(expected, rel=1e-1)


def test_sc_transmitter(sc_transmitter, sc_antenna):
    assert sc_transmitter.equivalent_isotropic_radiated_power(sc_antenna, 0.0) == pytest.approx(7.5, rel=1e-1)


def test_sc_receiver(sc_receiver, sc_antenna):
    assert sc_receiver.gain_to_noise_temperature(sc_antenna, 0.0) == pytest.approx(-19.82, rel=1e-1)


def test_uplink(uplink, gs_system, sc_system, slant_range):
    ebn0 = uplink.bit_energy_to_noise_density(gs_system, sc_system, 8.5, slant_range, 0.0, 0.0)
    assert ebn0 == pytest.approx(10, rel=1.0)


def test_downlink(downlink, sc_system, gs_system, slant_range):
    ebn0 = downlink.bit_energy_to_noise_density(sc_system, gs_system, 8.5, slant_range, 0.0, 0.0)
    assert ebn0 == pytest.approx(1.5, rel=1e-1)


def test_link_budget(phasma_scenario_manual):
    lb = LinkBudget(scenario=phasma_scenario_manual)
    results = lb.analyze()
    assert isinstance(results, LinkBudgetResults)


def test_c_n0i0_without_interference(gs_system, sc_system, slant_range):
    bandwidth = 1e6
    c_n0 = gs_system.carrier_to_noise_density(sc_system, losses=0.0, rng=slant_range, tx_angle=0.0, rx_angle=0.0)
    c_n0i0 = gs_system.carrier_to_noise_interference_density(
        sc_system,
        losses=0.0,
        rng=slant_range,
        tx_angle=0.0,
        rx_angle=0.0,
        bandwidth=bandwidth,
        interference_power_w=0.0,
    )
    assert c_n0 == pytest.approx(c_n0i0, rel=1e-9)


def test_eb_n0i0_without_interference(downlink, sc_system, gs_system, slant_range):
    bandwidth = 1e6
    eb_n0 = downlink.bit_energy_to_noise_density(
        sc_system, gs_system, losses=0.0, rng=slant_range, tx_angle=0.0, rx_angle=0.0
    )
    eb_n0i0 = downlink.bit_energy_to_noise_interference_density(
        sc_system,
        gs_system,
        losses=0.0,
        rng=slant_range,
        tx_angle=0.0,
        rx_angle=0.0,
        bandwidth=bandwidth,
        interference_power_w=0.0,
    )
    assert eb_n0 == pytest.approx(eb_n0i0, rel=1e-9)


def test_antenna_tracking(phasma_scenario_manual, phasma_sc_with_comms, phasma_ground_stations):
    for asset in phasma_scenario_manual.assets:
        if isinstance(asset.model, Spacecraft):
            # Tell spacecraft to track first ground station
            asset.track(phasma_ground_stations[0].asset_id)
        else:
            # Tell ground station to track spacecraft
            asset.track(phasma_sc_with_comms.asset_id)

    for asset in phasma_scenario_manual.assets:
        # Check that every asset tracks another asset
        assert asset.tracked_object_ids

    lb = LinkBudget(scenario=phasma_scenario_manual)
    results = lb.analyze()
    for i_gs, gs_asset in enumerate(phasma_ground_stations):
        for link in results[gs_asset, phasma_sc_with_comms]:
            for link_stat in link.stats:
                if link.link_type == "uplink":
                    # All ground stations should track the spacecraft with pointing error
                    assert link_stat.tx_angle.degrees == pytest.approx(0.1, rel=1e-3)
                    if i_gs == 0:
                        # The spacecraft tracks only the first ground station with pointing error
                        assert link_stat.rx_angle.degrees == pytest.approx(0.1, rel=1e-3)
                    else:
                        # The angle must be strictly positive because no tracking
                        assert link_stat.rx_angle.degrees > 0 and link_stat.rx_angle.degrees <= 180
                else:
                    # All ground stations should track the spacecraft with pointing error
                    assert link_stat.rx_angle.degrees == pytest.approx(0.1, rel=1e-3)
                    if i_gs == 0:
                        # The spacecraft tracks only the first ground station with pointing error
                        assert link_stat.tx_angle.degrees == pytest.approx(0.1, rel=1e-3)
                    else:
                        # The angle must be strictly positive because no tracking
                        assert link_stat.tx_angle.degrees > 0 and link_stat.tx_angle.degrees <= 180


def test_antenna_no_tracking(phasma_scenario_manual, phasma_sc_with_comms, phasma_ground_stations):
    # Check that tracking is disabled by default on all assets
    for asset in phasma_scenario_manual.assets:
        assert asset.tracked_object_ids == []

    lb = LinkBudget(scenario=phasma_scenario_manual)
    results = lb.analyze()
    for gs_asset in phasma_ground_stations:
        for link in results[gs_asset, phasma_sc_with_comms]:
            for link_stat in link.stats:
                # The angles must be strictly positive because no tracking
                assert link_stat.rx_angle.degrees > 0 and link_stat.rx_angle.degrees <= 180
                assert link_stat.tx_angle.degrees > 0 and link_stat.tx_angle.degrees <= 180


def fix_tle_checksum(line: str) -> str:
    """
    Calculate the checksum of a TLE line (Line 2).
    The checksum is the sum of the digits in the line modulo 10.
    """
    # Exclude the checksum digit (last digit) to calculate the checksum
    line_without_checksum = line[:-1]
    total = 0
    for char in line_without_checksum:
        if char.isdigit():
            total += int(char)
        elif char == "-":
            total += 1
    checksum = total % 10
    return line_without_checksum + str(checksum)


@pytest.mark.filterwarnings("ignore::scipy.io.matlab.MatReadWarning")
def test_matlab_interference_scenario(resources):
    mat_dict = loadmat(resources / "interference" / "InterferenceFromSatConstellationOnCommunicationsLinkExample.mat")
    constellation_tle_file = resources / "interference" / "leoSatelliteConstellation.tle"

    start_time = Time.from_utc(mat_dict["startTimeStr"][0])
    stop_time = start_time + TimeDelta.from_minutes(mat_dict["durationMinutes"][0, 0])

    downlink = Channel(
        link_type="downlink",
        modulation="BPSK",
        data_rate=1e6 * mat_dict["bitRateMbit"][0, 0],
        required_eb_n0=mat_dict["rxGsRequiredEbN0"][0, 0],
        margin=0,
    )

    tx_meo_freq = mat_dict["txMEOFreq"][0, 0]
    interference_freq = mat_dict["interferenceFreq"][0, 0]

    tx_meo_antenna = ComplexAntenna(
        pattern=GaussianPattern(
            diameter=mat_dict["txMEOAntDiameter"][0, 0],
            efficiency=mat_dict["txMEOAntEfficiency"][0, 0],
        ),
        boresight_vector=(0, -1, 0),
    )
    tx_meo_transmitter = Transmitter(
        power=from_db(mat_dict["txMEOPower_dBW"][0, 0]),
        frequency=Frequency(tx_meo_freq),
        line_loss=0.0,
    )
    tx_meo_system = CommunicationSystem(
        channels=[downlink.channel_id],
        transmitter=tx_meo_transmitter,
        antenna=tx_meo_antenna,
    )

    tx_interferer_antenna = ComplexAntenna(
        pattern=GaussianPattern(
            diameter=mat_dict["txInterferingAntDiameter"][0, 0],
            efficiency=mat_dict["txInterferingAntEfficiency"][0, 0],
        ),
        boresight_vector=(0, -1, 0),
    )
    tx_interferer_systems = [
        CommunicationSystem(
            channels=[downlink.channel_id],
            transmitter=Transmitter(
                power=from_db(tx_interferer_power_dbw),
                frequency=Frequency(value=interference_freq / 1e9, unit="GHz"),
                line_loss=0.0,
            ),
            antenna=tx_interferer_antenna,
        )
        for tx_interferer_power_dbw in mat_dict["txInterferingPowers_dBW"][0]
    ]

    gs_antenna = ComplexAntenna(
        pattern=GaussianPattern(
            diameter=mat_dict["gsAntDiameter"][0, 0],
            efficiency=mat_dict["gsAntEfficiency"][0, 0],
        ),
    )
    gs_receiver = SimpleReceiver(
        frequency=Frequency(tx_meo_freq),
        system_noise_temperature=mat_dict["rxGsNoiseTemperature"][0, 0],
    )
    gs_system = CommunicationSystem(
        channels=[downlink.channel_id],
        receiver=gs_receiver,
        antenna=gs_antenna,
    )

    gs_asset = Asset(
        model=GroundStation.from_lla(
            longitude=mat_dict["gsLon_deg"][0, 0],
            latitude=mat_dict["gsLat_deg"][0, 0],
            minimum_elevation=Angle.from_degrees(0),
        ),
        name="Ground station",
        comms=[gs_system],
    )

    true_anomaly = mat_dict["trueAnomaly"][0, 0]
    orbit = Keplerian.from_elements(
        start_time,
        1e-3 * mat_dict["semiMajorAxis"][0, 0],  # converting to km
        mat_dict["eccentricity"][0, 0],
        mat_dict["inclination"][0, 0],
        mat_dict["raan"][0, 0],
        mat_dict["argOfPeriapsis"][0, 0],
        true_anomaly if true_anomaly <= 180 else true_anomaly - 360,
        angle_unit="degrees",
        anomaly_type="true",
    )
    kepler_prop = SemiAnalyticalPropagator(
        state_init=orbit, grav_degree_order=None, prop_max_step=mat_dict["sampleTime"][0, 0]
    )
    main_sc = Asset(model=Spacecraft(propagator=kepler_prop), name="MAIN_SAT", comms=[tx_meo_system])

    interfering_sc_assets: list[Asset] = []

    with open(constellation_tle_file) as f:
        tle_lines = f.readlines()
        i = 0
        i_sat = 0
        while i < len(tle_lines):
            sat_name = tle_lines[i].split("\n")[0]
            tle_line1 = fix_tle_checksum(tle_lines[i + 1].split("\n")[0])
            tle_line2 = fix_tle_checksum(tle_lines[i + 2].split("\n")[0])
            propagator = SGP4(tle="\n".join([tle_line1, tle_line2]))
            interfering_sc_assets.append(
                Asset(model=Spacecraft(propagator=propagator), name=sat_name, comms=[tx_interferer_systems[i_sat]])
            )
            i += 3
            i_sat += 1

    # Define antenna tracking to match MATLAB behavior
    # In MATLAB: all satellites use pointAt(gs) to track ground station directly
    # Ground station uses pointAt(meoSat) to track main satellite
    gs_asset.track(main_sc.asset_id)
    main_sc.track(gs_asset.asset_id)
    for interfering_sc_asset in interfering_sc_assets:
        interfering_sc_asset.track(gs_asset.asset_id)

    # Set perfect pointing to match MATLAB's antenna behavior
    # MATLAB uses perfect pointing (0° off-boresight) while Ephemerista default is 0.1°
    gs_asset.pointing_error = 0.0
    main_sc.pointing_error = 0.0
    for interfering_sc_asset in interfering_sc_assets:
        interfering_sc_asset.pointing_error = 0.0

    scenario = Scenario(
        assets=[gs_asset, main_sc, *interfering_sc_assets],
        channels=[downlink],
        name="Link Budget with interference",
        start_time=start_time,
        end_time=stop_time,
    )

    lb = LinkBudget(scenario=scenario, with_environmental_losses=False, with_interference=True)
    lb_results_with_interference = lb.analyze()

    interf_data = lb_results_with_interference[gs_asset, main_sc][0]
    link_stats = interf_data.stats

    t_matlab = [Time.from_utc(t_str) for t_str in mat_dict["tStr"]]
    t_ephemerista = interf_data.times
    dt_matlab = [(t - t_matlab[0]).to_decimal_seconds() for t in t_matlab]
    dt_ephemerista = [(t - t_ephemerista[0]).to_decimal_seconds() for t in t_ephemerista]

    # reference interference data from MATLAB
    matlab_ref_df = pd.DataFrame(
        {
            "c_n0": np.interp(dt_ephemerista, dt_matlab, mat_dict["CNoDownlink"][0]),
            "eb_n0": np.interp(dt_ephemerista, dt_matlab, mat_dict["ebnoDownlink"][0]),
            "margin_without_interf": np.interp(dt_ephemerista, dt_matlab, mat_dict["marginWithoutInterference"][0]),
            "c_n0i0": np.interp(dt_ephemerista, dt_matlab, mat_dict["CNoPlusInterference"][0]),
            "eb_n0i0": np.interp(dt_ephemerista, dt_matlab, mat_dict["ebNoPlusInterference"][0]),
            "margin_with_interf": np.interp(dt_ephemerista, dt_matlab, mat_dict["marginWithInterference"][0]),
            "downlink_rx_power_in": np.interp(dt_ephemerista, dt_matlab, mat_dict["downlinkPowerRxInput"][0]),
            "interference_power_w": np.interp(dt_ephemerista, dt_matlab, mat_dict["interferencePowerRxInputActual"][0]),
            "noise_plus_interference_power": np.interp(
                dt_ephemerista, dt_matlab, mat_dict["noisePlusInterferencePower"][0]
            ),
        }
    )

    # Compare link budget and interference data
    for i in range(len(t_ephemerista)):
        interf_stats = link_stats[i].interference_stats
        assert interf_stats
        matlab_ref_data = matlab_ref_df.iloc[i]

        assert matlab_ref_data["c_n0"] == pytest.approx(link_stats[i].c_n0, abs=0.01)
        assert matlab_ref_data["eb_n0"] == pytest.approx(link_stats[i].eb_n0, abs=0.01)
        assert matlab_ref_data["margin_without_interf"] == pytest.approx(link_stats[i].margin, abs=0.01)

        assert matlab_ref_data["c_n0i0"] == pytest.approx(interf_stats.c_n0i0, abs=1.0)
        assert matlab_ref_data["eb_n0i0"] == pytest.approx(interf_stats.eb_n0i0, abs=1.0)
        assert matlab_ref_data["margin_with_interf"] == pytest.approx(interf_stats.margin_with_interference, abs=1.0)
