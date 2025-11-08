package org.lsf;

import org.hipparchus.ode.nonstiff.DormandPrince853Integrator;
import org.orekit.bodies.CelestialBody;
import org.orekit.bodies.CelestialBodyFactory;
import org.orekit.forces.drag.IsotropicDrag;
import org.orekit.forces.gravity.potential.GravityFieldFactory;
import org.orekit.forces.gravity.potential.UnnormalizedSphericalHarmonicsProvider;
import org.orekit.forces.radiation.IsotropicRadiationSingleCoefficient;
import org.orekit.models.earth.atmosphere.NRLMSISE00;
import org.orekit.models.earth.atmosphere.data.CssiSpaceWeatherData;
import org.orekit.orbits.Orbit;
import org.orekit.propagation.semianalytical.dsst.DSSTPropagator;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTAtmosphericDrag;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTNewtonianAttraction;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTSolarRadiationPressure;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTTesseral;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTThirdBody;
import org.orekit.propagation.semianalytical.dsst.forces.DSSTZonal;
import org.orekit.utils.Constants;
import org.orekit.utils.TimeStampedPVCoordinates;

public class SemiAnalyticalPropagatorRef extends OrekitPropagatorRef {

    public SemiAnalyticalPropagatorRef(TimeStampedPVCoordinates state_init, double prop_min_step, double prop_max_step, double prop_init_step,
            double prop_position_error, double mass, double cross_section, int[] grav_degree_order,
            String[] third_bodies, double c_r, boolean enable_srp, double c_d, boolean enable_drag) {
        super(state_init, prop_min_step, prop_max_step, prop_init_step, prop_position_error, mass, cross_section, grav_degree_order,
                third_bodies, c_r, enable_srp, c_d, enable_drag);
    }

    public void setup_propagator(Orbit orbit_sample) {
        double[][] tol = DSSTPropagator.tolerances(this.prop_position_error, orbit_sample);

        DormandPrince853Integrator integrator = new DormandPrince853Integrator(this.prop_min_step, this.prop_max_step,
                tol[0], tol[1]);
        integrator.setInitialStepSize(this.prop_init_step);

        this._orekit_prop = new DSSTPropagator(integrator);

        this.setup_force_models();
    }

    public void setup_force_models() {
        ((DSSTPropagator) this._orekit_prop).addForceModel(new DSSTNewtonianAttraction(Constants.EIGEN5C_EARTH_MU));

        if (this.grav_degree_order.length == 2) {

            UnnormalizedSphericalHarmonicsProvider gravity_provider = GravityFieldFactory.getUnnormalizedProvider(
                    this.grav_degree_order[0], this.grav_degree_order[1]);

            DSSTZonal zonal = new DSSTZonal(gravity_provider);
            ((DSSTPropagator) this._orekit_prop).addForceModel(zonal);

            DSSTTesseral tesseral = new DSSTTesseral(
                    this._wgs84_ellipsoid.getBodyFrame(), this._wgs84_ellipsoid.getSpin(), gravity_provider);
            ((DSSTPropagator) this._orekit_prop).addForceModel(tesseral);

        }

        for (String body : this.third_bodies) {
            try {
                CelestialBody body_orekit = CelestialBodyFactory.getBody(body);
                ((DSSTPropagator) this._orekit_prop)
                        .addForceModel(new DSSTThirdBody(body_orekit, Constants.EIGEN5C_EARTH_MU));

            } catch (NullPointerException e) {
                // TODO: handle exception
            }
        }

        if (this.enable_srp) {

            IsotropicRadiationSingleCoefficient isotropic_rad = new IsotropicRadiationSingleCoefficient(
                    this.cross_section, this.c_r);

            ((DSSTPropagator) this._orekit_prop).addForceModel(new DSSTSolarRadiationPressure(this._sun,
                    this._wgs84_ellipsoid, isotropic_rad, Constants.EIGEN5C_EARTH_MU));

        }
        if (this.enable_drag) {

            CssiSpaceWeatherData cswl = new CssiSpaceWeatherData("SpaceWeather-All-v1.2.txt");

            NRLMSISE00 atmosphere = new NRLMSISE00(cswl, this._sun, this._wgs84_ellipsoid);

            IsotropicDrag isotropic_drag = new IsotropicDrag(this.cross_section, this.c_d);

            ((DSSTPropagator) this._orekit_prop)
                    .addForceModel(new DSSTAtmosphericDrag(atmosphere, isotropic_drag, Constants.EIGEN5C_EARTH_MU));
        }
    }
}
