"""The propagators.orekit package.

This package provides orbit propagators based on Orekit.
"""

import abc
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import Field, PrivateAttr

from ephemerista import BaseModel
from ephemerista.bodies import Origin
from ephemerista.coords.trajectories import Trajectory
from ephemerista.coords.twobody import Cartesian, TwoBodyType
from ephemerista.propagators import Propagator
from ephemerista.propagators.events import StoppingEvent
from ephemerista.propagators.orekit.conversions import (
    cartesian_to_tpv,
    time_to_abs_date,
    time_to_j2000_tai,
    tpv_to_cartesian,
)
from ephemerista.time import Time


class OrekitPropagatorParams(BaseModel):
    """Common parameters for Orekit-based propagators."""

    prop_min_step: float = Field(gt=0.0, default=0.001, description="Propagator's minimum time step, in s")
    prop_max_step: float = Field(gt=0.0, default=3600.0, description="Propagator's maximum time step, in s")
    prop_init_step: float = Field(gt=0.0, default=60.0, description="Propagator's initial time step, in s")
    prop_position_error: float = Field(gt=0.0, default=10.0, description="Targeted integrator precision, in m")

    mass: float = Field(gt=0.0, default=1000.0, description="Spacecraft mass, in kg")
    cross_section: float = Field(ge=0.0, default=1.0, description="Spacecraft cross-section, in m^2")

    grav_degree_order: tuple[int, int] | None = Field(
        default=(4, 4), description="Degree/order of the gravity spherical harmonics model"
    )

    third_bodies: list[Origin] = Field(default=[], description="List of third-bodies to use as perturbators")

    c_r: float = Field(ge=0.0, default=0.75, description="Reflection coefficient for solar radiation pressure")
    enable_srp: bool = Field(default=False, description="Flag to enable solar radiation pressure")

    c_d: float = Field(ge=0.0, default=2.0, description="Drag coefficient")
    enable_drag: bool = Field(default=False, description="Flag to enable atmospheric drag")


class OrekitPropagator(Propagator, abc.ABC):
    """Abstract base class for Orekit-based propagtors.

    Notes
    -----
    If a gravity potential coefficients files is supplied, the default Orekit ones (Earth EIGEN-6S) will be
    discarded before adding the provided coefficient file, so use with care.
    """

    state_init: TwoBodyType = Field(description="Initial state vector", discriminator="state_type")
    params: OrekitPropagatorParams = Field(default=OrekitPropagatorParams())

    _orekit_prop: Any = PrivateAttr()
    _wgs84_ellipsoid: Any = PrivateAttr()
    _sun: Any = PrivateAttr()
    _icrf: Any = PrivateAttr()

    def __init__(
        self,
        *,
        params: OrekitPropagatorParams | None = None,
        gravity_file: Path | None = None,
        **data,
    ):
        super().__init__(**data)

        if params is None:
            self.params = OrekitPropagatorParams(**data)

        self.add_gravity_file(gravity_file)

        self._setup_orekit_objs()

    def add_gravity_file(self, gravity_file: Path | None = None):
        """Load a custom gravity file."""
        if gravity_file is None:
            return

        from java.io import File  # type: ignore  # noqa: PLC0415
        from org.orekit.data import DataContext, DirectoryCrawler  # type: ignore  # noqa: PLC0415
        from org.orekit.errors import OrekitException  # type: ignore  # noqa: PLC0415
        from org.orekit.forces.gravity.potential import (  # type: ignore  # noqa: PLC0415
            EGMFormatReader,
            GravityFieldFactory,
            GRGSFormatReader,
            ICGEMFormatReader,
            SHMFormatReader,
        )

        gravity_readers = [EGMFormatReader, GRGSFormatReader, ICGEMFormatReader, SHMFormatReader]

        dm = DataContext.getDefault().getDataProvidersManager()
        GravityFieldFactory.clearPotentialCoefficientsReaders()

        folder = gravity_file.parent
        dm.addProvider(DirectoryCrawler(File(str(folder.absolute()))))  # add folder to Orekit data providers manager

        for gravity_reader in gravity_readers:
            try:
                coeff_reader = gravity_reader(gravity_file.name, True)
                GravityFieldFactory.addPotentialCoefficientsReader(coeff_reader)
                GravityFieldFactory.readGravityField(4, 4)  # Test reading until degree/order 4
                break
            except OrekitException:
                # This format reader was the wrong one, we clear the list of readers and will try the next one
                GravityFieldFactory.clearPotentialCoefficientsReaders()
                continue

    def _setup_orekit_objs(self):
        from org.orekit.frames import FramesFactory  # type: ignore  # noqa: PLC0415

        self._icrf = FramesFactory.getGCRF()  # Earth-centered ICRF
        from org.orekit.utils import IERSConventions  # type: ignore  # noqa: PLC0415

        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, False)
        from org.orekit.models.earth import ReferenceEllipsoid  # type: ignore  # noqa: PLC0415

        self._wgs84_ellipsoid = ReferenceEllipsoid.getWgs84(itrf)

        from org.orekit.bodies import CelestialBodyFactory  # type: ignore  # noqa: PLC0415

        self._sun = CelestialBodyFactory.getSun()

        from org.orekit.orbits import CartesianOrbit, EquinoctialOrbit  # type: ignore  # noqa: PLC0415
        from org.orekit.utils import Constants as OrekitConstants  # type: ignore  # noqa: PLC0415

        tpv_icrf = cartesian_to_tpv(self.state_init.to_cartesian())
        orbit_init_cart = CartesianOrbit(tpv_icrf, self._icrf, OrekitConstants.EIGEN5C_EARTH_MU)
        orbit_init_equinoctial = EquinoctialOrbit(orbit_init_cart)
        self._setup_propagator(orbit_init_equinoctial)
        self.set_initial_state(self.state_init)

    @abc.abstractmethod
    def _setup_propagator(self, orbit_sample): ...

    def set_initial_state(self, state_init: TwoBodyType):
        """Update the initial state of the propagator."""
        from org.orekit.orbits import CartesianOrbit, EquinoctialOrbit  # type: ignore  # noqa: PLC0415
        from org.orekit.utils import Constants as OrekitConstants  # type: ignore  # noqa: PLC0415

        tpv_icrf = cartesian_to_tpv(state_init.to_cartesian())
        orbit_init_cart = CartesianOrbit(tpv_icrf, self._icrf, OrekitConstants.EIGEN5C_EARTH_MU)
        orbit_init_equinoctial = EquinoctialOrbit(orbit_init_cart)
        from org.orekit.propagation import SpacecraftState  # type: ignore  # noqa: PLC0415

        state_init_orekit = SpacecraftState(orbit_init_equinoctial, self.params.mass)
        self._orekit_prop.resetInitialState(state_init_orekit)

    def _add_stop_condition(self, stop_cond: StoppingEvent):
        if stop_cond == StoppingEvent.PERIAPSIS:
            from org.orekit.propagation.events import ApsideDetector  # type: ignore  # noqa: PLC0415
            from org.orekit.propagation.events.handlers import StopOnIncreasing  # type: ignore  # noqa: PLC0415

            periapsis_detector = ApsideDetector(self._orekit_prop.getInitialState().getOrbit()).withHandler(
                StopOnIncreasing()
            )
            self._orekit_prop.addEventDetector(periapsis_detector)
        elif stop_cond == StoppingEvent.APOAPSIS:
            from org.orekit.propagation.events import ApsideDetector  # type: ignore  # noqa: PLC0415
            from org.orekit.propagation.events.handlers import StopOnDecreasing  # type: ignore  # noqa: PLC0415

            apoapsis_detector = ApsideDetector(self._orekit_prop.getInitialState().getOrbit()).withHandler(
                StopOnDecreasing()
            )
            self._orekit_prop.addEventDetector(apoapsis_detector)

    def propagate(
        self,
        time: Time | list[Time],
        stop_conds: list[StoppingEvent] | None = None,
    ) -> Cartesian | Trajectory:
        """
        Propagate the state.

        Parameters
        ----------
        time: Time | list[Time]
            Either a single `Time` or a list of `Time`s.

        Returns
        -------
        Cartesian | Trajectory
            Either a single `Cartesian` state for a discrete input or a `Trajectory` for a list.

        Notes
        -----
        When stopping conditions are defined, the Trajectory will end at the stopping condition so
        it won't contain all the states requested in the input Time list.
        """
        self.set_initial_state(self.state_init)

        if stop_conds:
            self._orekit_prop.clearEventsDetectors()
            for stop_cond in stop_conds:
                self._add_stop_condition(stop_cond)

        if isinstance(time, Time):
            state_end = self._orekit_prop.propagate(time_to_abs_date(time))
            return tpv_to_cartesian(state_end.getPVCoordinates())
        else:
            eph_generator = self._orekit_prop.getEphemerisGenerator()
            time_start = time[0]
            time_end = time[-1]
            self._orekit_prop.propagate(time_to_abs_date(time_end))
            bounded_propagator = eph_generator.getGeneratedEphemeris()

            from org.lsf.OrekitConversions import exportStates2D  # type: ignore  # noqa: PLC0415

            # Exporting states to 2D array in Java, and writing the memory content to a numpy array
            time_j2000_list = [time_to_j2000_tai(t) for t in time]  # TODO: prevent using a for loop
            states_array = np.asarray(memoryview(exportStates2D(bounded_propagator, time_j2000_list)))

            return Trajectory(start_time=time_start, states=states_array)
