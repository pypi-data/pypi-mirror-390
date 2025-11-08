"""The semianalytical.py module.

This module provides the `SemiAnalytical` class which wraps the Draper Semi-Analytical Satellite Theory (DSST)
from Orekit.
"""

from typing import Literal

from pydantic import Field

from ephemerista.propagators.orekit import OrekitPropagator


class SemiAnalyticalPropagator(OrekitPropagator):
    """The SemiAnalyticalPropagator class."""

    propagator_type: Literal["semianalytical"] = Field(
        default="semianalytical", frozen=True, repr=False, alias="type", description="The type of the propagator"
    )

    def _setup_propagator(self, orbit_sample):
        from org.orekit.propagation.semianalytical.dsst import DSSTPropagator  # type: ignore  # noqa: PLC0415

        tol = DSSTPropagator.tolerances(self.params.prop_position_error, orbit_sample)
        from org.hipparchus.ode.nonstiff import DormandPrince853Integrator  # type: ignore  # noqa: PLC0415

        integrator = DormandPrince853Integrator(self.params.prop_min_step, self.params.prop_max_step, tol[0], tol[1])
        integrator.setInitialStepSize(self.params.prop_init_step)

        # Set up propagator and force models
        self._orekit_prop = DSSTPropagator(integrator)

        self._setup_force_models()

    def _setup_force_models(self):
        from org.orekit.propagation.semianalytical.dsst.forces import (  # noqa: PLC0415
            DSSTNewtonianAttraction,  # type: ignore
        )
        from org.orekit.utils import Constants as OrekitConstants  # type: ignore  # noqa: PLC0415

        self._orekit_prop.addForceModel(DSSTNewtonianAttraction(OrekitConstants.EIGEN5C_EARTH_MU))

        if self.params.grav_degree_order:
            from org.orekit.forces.gravity.potential import GravityFieldFactory  # type: ignore  # noqa: PLC0415

            gravity_provider = GravityFieldFactory.getUnnormalizedProvider(
                self.params.grav_degree_order[0], self.params.grav_degree_order[1]
            )
            from org.orekit.propagation.semianalytical.dsst.forces import (  # type: ignore  # noqa: PLC0415
                DSSTTesseral,
                DSSTZonal,
            )

            zonal = DSSTZonal(gravity_provider)
            self._orekit_prop.addForceModel(zonal)

            tesseral = DSSTTesseral(
                self._wgs84_ellipsoid.getBodyFrame(), self._wgs84_ellipsoid.getSpin(), gravity_provider
            )
            self._orekit_prop.addForceModel(tesseral)

        from java.lang import NullPointerException  # type: ignore  # noqa: PLC0415
        from org.orekit.bodies import CelestialBodyFactory  # type: ignore  # noqa: PLC0415
        from org.orekit.propagation.semianalytical.dsst.forces import DSSTThirdBody  # type: ignore  # noqa: PLC0415

        for body in self.params.third_bodies:
            try:  # CelestialBodyFactory.getBody throws a NullPointerException if the body is not supported by Orekit
                body_orekit = CelestialBodyFactory.getBody(body.name)
                self._orekit_prop.addForceModel(DSSTThirdBody(body_orekit, OrekitConstants.EIGEN5C_EARTH_MU))
            except NullPointerException as exc:
                msg = f"Body {body.name} unsupported for Orekit third-body attraction"
                raise ValueError(msg) from exc

        if self.params.enable_srp:
            from org.orekit.forces.radiation import IsotropicRadiationSingleCoefficient  # type: ignore  # noqa: PLC0415

            isotropic_rad = IsotropicRadiationSingleCoefficient(self.params.cross_section, self.params.c_r)
            from org.orekit.bodies import CelestialBodyFactory  # type: ignore  # noqa: PLC0415
            from org.orekit.propagation.semianalytical.dsst.forces import (  # noqa: PLC0415
                DSSTSolarRadiationPressure,  # type: ignore
            )

            self._orekit_prop.addForceModel(
                DSSTSolarRadiationPressure(
                    self._sun, self._wgs84_ellipsoid, isotropic_rad, OrekitConstants.EIGEN5C_EARTH_MU
                )
            )

        if self.params.enable_drag:
            from org.orekit.models.earth.atmosphere.data import CssiSpaceWeatherData  # type: ignore  # noqa: PLC0415

            cswl = CssiSpaceWeatherData("SpaceWeather-All-v1.2.txt")

            from org.orekit.models.earth.atmosphere import NRLMSISE00  # type: ignore  # noqa: PLC0415

            atmosphere = NRLMSISE00(cswl, self._sun, self._wgs84_ellipsoid)

            from org.orekit.forces.drag import IsotropicDrag  # type: ignore  # noqa: PLC0415

            isotropic_drag = IsotropicDrag(self.params.cross_section, self.params.c_d)
            from org.orekit.propagation.semianalytical.dsst.forces import (  # noqa: PLC0415
                DSSTAtmosphericDrag,  # type: ignore
            )

            self._orekit_prop.addForceModel(
                DSSTAtmosphericDrag(atmosphere, isotropic_drag, OrekitConstants.EIGEN5C_EARTH_MU)
            )
