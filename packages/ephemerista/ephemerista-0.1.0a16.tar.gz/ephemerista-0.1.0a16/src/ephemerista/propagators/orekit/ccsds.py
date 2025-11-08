"""The ccsds.py module.

This module contains functions for importing and exporting CCSDS Orbital Data Messages (ODM).
"""

from enum import Enum, auto
from pathlib import Path

import numpy as np

from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import Cartesian, TwoBody
from ephemerista.propagators.orekit.conversions import (
    abs_date_to_time,
    cartesian_to_tpv,
    time_to_abs_date,
    tpv_to_cartesian,
)


class CcsdsFileFormat(Enum):
    """An enum for specifying the type of ODM file format."""

    KVN = auto()
    XML = auto()


def parse_oem(path: str | Path, dt: float) -> Trajectory:
    """Parse an OEM into a `Trajectory`."""
    from org.orekit.files.ccsds.ndm import ParserBuilder  # type: ignore  # noqa: PLC0415

    oem_parser = ParserBuilder().buildOemParser()

    from org.orekit.data import DataSource  # type: ignore  # noqa: PLC0415

    oem = oem_parser.parse(DataSource(path))

    sat_map = oem.getSatellites()
    if sat_map.size() != 1:
        msg = f"{sat_map.size()} satellites found in the OEM file, while we only support one satellite per OEM file"
        raise ValueError(msg)

    sat_ephem = sat_map.values().toArray()[0]
    bounded_propagator = sat_ephem.getPropagator()
    time_start = abs_date_to_time(bounded_propagator.getMinDate())

    from org.lsf.OrekitConversions import exportStates2D  # type: ignore  # noqa: PLC0415

    # Exporting states to 2D array in Java, and writing the memory content to a numpy array
    states_array = np.asarray(memoryview(exportStates2D(bounded_propagator, dt)))

    return Trajectory(start_time=time_start, states=states_array)


def write_oem(traj: Trajectory, path: str | Path, dt: float, file_format: CcsdsFileFormat) -> None:
    """Export a `Trajectory` as an OEM."""
    from java.io import FileWriter  # type: ignore  # noqa: PLC0415
    from java.util import ArrayList  # type: ignore  # noqa: PLC0415
    from org.orekit.bodies import CelestialBodyFactory  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.definitions import BodyFacade, FrameFacade, TimeSystem  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.ndm import WriterBuilder  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.ndm.odm import OdmHeader  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.ndm.odm.oem import (  # type: ignore  # noqa: PLC0415
        OemMetadata,
        OemWriter,
        StreamingOemWriter,
    )
    from org.orekit.files.ccsds.utils.generation import KvnGenerator, XmlGenerator  # type: ignore  # noqa: PLC0415
    from org.orekit.frames import FramesFactory  # type: ignore  # noqa: PLC0415
    from org.orekit.propagation import SpacecraftState  # type: ignore  # noqa: PLC0415
    from org.orekit.propagation.analytical import Ephemeris  # type: ignore  # noqa: PLC0415
    from org.orekit.utils import AbsolutePVCoordinates  # type: ignore  # noqa: PLC0415

    writer_builder = WriterBuilder()

    metadata = OemMetadata(4)
    metadata.setObjectName("DUMMY_OBJECT_NAME")
    metadata.setObjectID("DUMMY_NORAD_ID")
    central_body = CelestialBodyFactory.getBody(traj.origin.name)
    metadata.setCenter(BodyFacade(traj.origin.name.upper(), central_body))
    icrf = FramesFactory.getGCRF()
    metadata.setReferenceFrame(FrameFacade.map(icrf))
    metadata.setTimeSystem(TimeSystem.TAI)

    header = OdmHeader()
    header.setOriginator("EPHEMERISTA")

    out_writer = FileWriter(path)

    if file_format == CcsdsFileFormat.KVN:
        generator = KvnGenerator(out_writer, OemWriter.KVN_PADDING_WIDTH, "stdout", 86400.0, 0)
    elif file_format == CcsdsFileFormat.XML:
        generator = XmlGenerator(
            out_writer, XmlGenerator.DEFAULT_INDENT, "stdout", 86400.0, True, XmlGenerator.NDM_XML_V3_SCHEMA_LOCATION
        )

    sw = StreamingOemWriter(generator, writer_builder.buildOemWriter(), header, metadata)

    state_list = ArrayList()

    for cart_icrf in traj.cartesian_states:
        tpv_icrf = cartesian_to_tpv(cart_icrf)
        state_list.add(SpacecraftState(AbsolutePVCoordinates(icrf, tpv_icrf)))

    ephemeris = Ephemeris(state_list, 4)

    ephemeris.getMultiplexer().clear()
    ephemeris.getMultiplexer().add(dt, sw.newSegment())

    ephemeris.propagate(ephemeris.getMinDate(), ephemeris.getMaxDate())

    sw.close()
    out_writer.close()


def parse_omm(path: str | Path) -> Cartesian:
    """Parse an OMM as a `Cartesian` state."""
    from org.orekit.files.ccsds.ndm import ParserBuilder  # type: ignore  # noqa: PLC0415

    omm_parser = ParserBuilder().buildOmmParser()

    from org.orekit.data import DataSource  # type: ignore  # noqa: PLC0415

    omm = omm_parser.parseMessage(DataSource(path))
    sc_state = omm.generateSpacecraftState()

    from org.orekit.frames import FramesFactory  # type: ignore  # noqa: PLC0415

    tpv_icrf = sc_state.getPVCoordinates(FramesFactory.getGCRF())
    return tpv_to_cartesian(tpv_icrf)


def write_omm(cart: TwoBody, path: str | Path, file_format: CcsdsFileFormat) -> None:
    """Export `Cartesian` or `Keplerian` state as an OMM."""
    from java.io import FileWriter  # type: ignore  # noqa: PLC0415
    from org.orekit.bodies import CelestialBodyFactory  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.definitions import BodyFacade, FrameFacade, TimeSystem  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.ndm import WriterBuilder  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.ndm.odm import (  # type: ignore  # noqa: PLC0415
        CartesianCovariance,
        KeplerianElements,
        OdmHeader,
        SpacecraftParameters,
        UserDefined,
    )
    from org.orekit.files.ccsds.ndm.odm.omm import (  # type: ignore  # noqa: PLC0415
        OmmData,
        OmmMetadata,
        OmmTle,
        OmmWriter,
    )
    from org.orekit.files.ccsds.section import Segment  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.utils.generation import KvnGenerator, XmlGenerator  # type: ignore  # noqa: PLC0415
    from org.orekit.frames import FramesFactory  # type: ignore  # noqa: PLC0415
    from org.orekit.orbits import PositionAngleType  # type: ignore  # noqa: PLC0415
    from org.orekit.utils import Constants  # type: ignore  # noqa: PLC0415

    writer_builder = WriterBuilder()

    metadata = OmmMetadata()
    metadata.setObjectName("DUMMY_OBJECT_NAME")
    metadata.setObjectID("DUMMY_NORAD_ID")
    central_body = CelestialBodyFactory.getBody(cart.origin.name)
    metadata.setCenter(BodyFacade(cart.origin.name.upper(), central_body))
    icrf = FramesFactory.getGCRF()
    metadata.setReferenceFrame(FrameFacade.map(icrf))
    metadata.setTimeSystem(TimeSystem.TAI)
    metadata.setMeanElementTheory("JUST_OSCULATING_ELEMENTS_REALLY")

    omm_writer = writer_builder.buildOmmWriter()

    header = OdmHeader()
    header.setOriginator("EPHEMERISTA")

    out_writer = FileWriter(path)

    if file_format == CcsdsFileFormat.KVN:
        generator = KvnGenerator(out_writer, OmmWriter.KVN_PADDING_WIDTH, "stdout", 86400.0, 0)
    elif file_format == CcsdsFileFormat.XML:
        generator = XmlGenerator(
            out_writer, XmlGenerator.DEFAULT_INDENT, "stdout", 86400.0, True, XmlGenerator.NDM_XML_V3_SCHEMA_LOCATION
        )

    omm_writer.writeHeader(generator, header)

    kepl = cart.to_keplerian()
    kepl_els_orekit = KeplerianElements()
    kepl_els_orekit.setEpoch(time_to_abs_date(kepl.time))
    kepl_els_orekit.setA(1e3 * kepl.semi_major_axis)
    kepl_els_orekit.setE(kepl.eccentricity)
    kepl_els_orekit.setI(kepl.inclination)
    kepl_els_orekit.setRaan(kepl.ascending_node)
    kepl_els_orekit.setPa(kepl.periapsis_argument)
    kepl_els_orekit.setAnomaly(kepl.mean_anomaly)
    kepl_els_orekit.setAnomalyType(PositionAngleType.MEAN)
    kepl_els_orekit.setMu(Constants.IAU_2015_NOMINAL_EARTH_GM)

    mass = 1000.0
    omm_data = OmmData(
        kepl_els_orekit,
        # jpype overloads the @ operator for type casting
        SpacecraftParameters @ None,  # type: ignore
        OmmTle @ None,  # type: ignore
        CartesianCovariance @ None,  # type: ignore
        UserDefined(),
        mass,
    )

    omm_writer.writeSegment(generator, Segment(metadata, omm_data))

    omm_writer.writeFooter(generator)

    out_writer.close()


def parse_opm(path: str | Path) -> Cartesian:
    """Parse an OPM into a `Cartesian` state."""
    from org.orekit.files.ccsds.ndm import ParserBuilder  # type: ignore  # noqa: PLC0415

    opm_parser = ParserBuilder().buildOpmParser()

    from org.orekit.data import DataSource  # type: ignore  # noqa: PLC0415

    opm = opm_parser.parseMessage(DataSource(path))
    sc_state = opm.generateSpacecraftState()
    # TODO: extract mass, cross-section, etc. e.g. sc_state.getMass()  # https://www.orekit.org/site-orekit-development/apidocs/org/orekit/propagation/SpacecraftState.html

    from org.orekit.frames import FramesFactory  # type: ignore  # noqa: PLC0415

    tpv_icrf = sc_state.getPVCoordinates(FramesFactory.getGCRF())
    return tpv_to_cartesian(tpv_icrf)


def write_opm(cart: TwoBody, path: str | Path, file_format: CcsdsFileFormat) -> None:
    """Write a `Cartesian` or `Keplerian` state into an OPM file."""
    from java.io import FileWriter  # type: ignore  # noqa: PLC0415
    from java.util import ArrayList  # type: ignore  # noqa: PLC0415
    from org.orekit.bodies import CelestialBodyFactory  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.definitions import BodyFacade, FrameFacade, TimeSystem  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.ndm import WriterBuilder  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.ndm.odm import (  # type: ignore  # noqa: PLC0415
        CartesianCovariance,
        KeplerianElements,
        OdmCommonMetadata,
        OdmHeader,
        SpacecraftParameters,
        StateVector,
        UserDefined,
    )
    from org.orekit.files.ccsds.ndm.odm.opm import OpmData, OpmWriter  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.section import Segment  # type: ignore  # noqa: PLC0415
    from org.orekit.files.ccsds.utils.generation import KvnGenerator, XmlGenerator  # type: ignore  # noqa: PLC0415
    from org.orekit.frames import FramesFactory  # type: ignore  # noqa: PLC0415

    writer_builder = WriterBuilder()

    metadata = OdmCommonMetadata()
    metadata.setObjectName("DUMMY_OBJECT_NAME")
    metadata.setObjectID("DUMMY_NORAD_ID")
    central_body = CelestialBodyFactory.getBody(cart.origin.name)
    metadata.setCenter(BodyFacade(cart.origin.name.upper(), central_body))
    icrf = FramesFactory.getGCRF()
    metadata.setReferenceFrame(FrameFacade.map(icrf))
    metadata.setTimeSystem(TimeSystem.TAI)

    opm_writer = writer_builder.buildOpmWriter()

    header = OdmHeader()
    header.setOriginator("EPHEMERISTA")

    out_writer = FileWriter(path)

    if file_format == CcsdsFileFormat.KVN:
        generator = KvnGenerator(out_writer, OpmWriter.KVN_PADDING_WIDTH, "stdout", 86400.0, 0)
    elif file_format == CcsdsFileFormat.XML:
        generator = XmlGenerator(
            out_writer, XmlGenerator.DEFAULT_INDENT, "stdout", 86400.0, True, XmlGenerator.NDM_XML_V3_SCHEMA_LOCATION
        )

    opm_writer.writeHeader(generator, header)

    state_vec_orekit = StateVector()
    state_vec_orekit.setEpoch(time_to_abs_date(cart.time))
    cart = cart.to_cartesian()
    for i in range(0, 3):
        state_vec_orekit.setP(i, 1e3 * cart.position[i])
        state_vec_orekit.setV(i, 1e3 * cart.velocity[i])

    mass = 1000.0
    opm_data = OpmData(
        state_vec_orekit,
        KeplerianElements @ None,  # type: ignore
        SpacecraftParameters @ None,  # type: ignore
        CartesianCovariance @ None,  # type: ignore
        ArrayList(),
        UserDefined(),
        mass,
    )

    opm_writer.writeSegment(generator, Segment(metadata, opm_data))

    opm_writer.writeFooter(generator)

    out_writer.close()
