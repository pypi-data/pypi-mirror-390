"""The numerical.py module.

This module provides the `NumericalPropagator` class which wraps the numerical propgator from Orekit.
"""

from typing import Literal

from pydantic import Field

from ephemerista.propagators.orekit import OrekitPropagator


class NumericalPropagator(OrekitPropagator):
    """The NumericalPropagator class."""

    propagator_type: Literal["numerical"] = Field(
        default="numerical", frozen=True, repr=False, alias="type", description="The type of the propagator"
    )

    def _setup_propagator(self, orbit_sample):
        from org.orekit.propagation.numerical import (  # noqa: PLC0415
            NumericalPropagator as OrekitNumericalPropagator,  # type: ignore
        )

        tol = OrekitNumericalPropagator.tolerances(
            self.params.prop_position_error, orbit_sample, orbit_sample.getType()
        )
        from org.hipparchus.ode.nonstiff import DormandPrince853Integrator  # type: ignore  # noqa: PLC0415

        integrator = DormandPrince853Integrator(self.params.prop_min_step, self.params.prop_max_step, tol[0], tol[1])
        integrator.setInitialStepSize(self.params.prop_init_step)

        # Set up propagator and force models
        self._orekit_prop = OrekitNumericalPropagator(integrator)
        self._orekit_prop.setOrbitType(orbit_sample.getType())

        self._setup_force_models()

    def _setup_force_models(self):
        from org.orekit.forces.gravity import NewtonianAttraction  # type: ignore  # noqa: PLC0415
        from org.orekit.utils import Constants as OrekitConstants  # type: ignore  # noqa: PLC0415

        self._orekit_prop.addForceModel(NewtonianAttraction(OrekitConstants.EIGEN5C_EARTH_MU))

        if self.params.grav_degree_order:
            from org.orekit.forces.gravity.potential import GravityFieldFactory  # type: ignore  # noqa: PLC0415

            gravity_provider = GravityFieldFactory.getNormalizedProvider(
                self.params.grav_degree_order[0], self.params.grav_degree_order[1]
            )
            from org.orekit.forces.gravity import HolmesFeatherstoneAttractionModel  # type: ignore  # noqa: PLC0415

            gravity_attraction_model = HolmesFeatherstoneAttractionModel(
                self._wgs84_ellipsoid.getBodyFrame(), gravity_provider
            )
            self._orekit_prop.addForceModel(gravity_attraction_model)

        from java.lang import NullPointerException  # type: ignore  # noqa: PLC0415
        from org.orekit.bodies import CelestialBodyFactory  # type: ignore  # noqa: PLC0415
        from org.orekit.forces.gravity import ThirdBodyAttraction  # type: ignore  # noqa: PLC0415

        for body in self.params.third_bodies:
            try:  # CelestialBodyFactory.getBody throws a NullPointerException if the body is not supported by Orekit
                body_orekit = CelestialBodyFactory.getBody(body.name)
                self._orekit_prop.addForceModel(ThirdBodyAttraction(body_orekit))
            except NullPointerException as exc:
                msg = f"Body {body.name} unsupported for Orekit third-body attraction"
                raise ValueError(msg) from exc

        if self.params.enable_srp:
            from org.orekit.forces.radiation import IsotropicRadiationSingleCoefficient  # type: ignore  # noqa: PLC0415

            isotropic_rad = IsotropicRadiationSingleCoefficient(self.params.cross_section, self.params.c_r)
            from org.orekit.bodies import CelestialBodyFactory  # type: ignore  # noqa: PLC0415
            from org.orekit.forces.radiation import SolarRadiationPressure  # type: ignore  # noqa: PLC0415

            self._orekit_prop.addForceModel(SolarRadiationPressure(self._sun, self._wgs84_ellipsoid, isotropic_rad))

        if self.params.enable_drag:
            from org.orekit.models.earth.atmosphere.data import CssiSpaceWeatherData  # type: ignore  # noqa: PLC0415

            cswl = CssiSpaceWeatherData("SpaceWeather-All-v1.2.txt")

            from org.orekit.models.earth.atmosphere import NRLMSISE00  # type: ignore  # noqa: PLC0415

            atmosphere = NRLMSISE00(cswl, self._sun, self._wgs84_ellipsoid)

            from org.orekit.forces.drag import IsotropicDrag  # type: ignore  # noqa: PLC0415

            isotropic_drag = IsotropicDrag(self.params.cross_section, self.params.c_d)
            from org.orekit.forces.drag import DragForce  # type: ignore  # noqa: PLC0415

            self._orekit_prop.addForceModel(DragForce(atmosphere, isotropic_drag))
