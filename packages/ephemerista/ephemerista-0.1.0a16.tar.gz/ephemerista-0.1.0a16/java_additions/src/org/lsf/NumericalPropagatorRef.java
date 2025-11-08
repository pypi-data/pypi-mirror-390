package org.lsf;

import org.hipparchus.ode.nonstiff.DormandPrince853Integrator;
import org.orekit.bodies.CelestialBody;
import org.orekit.bodies.CelestialBodyFactory;
import org.orekit.forces.drag.DragForce;
import org.orekit.forces.drag.IsotropicDrag;
import org.orekit.forces.gravity.HolmesFeatherstoneAttractionModel;
import org.orekit.forces.gravity.NewtonianAttraction;
import org.orekit.forces.gravity.ThirdBodyAttraction;
import org.orekit.forces.gravity.potential.GravityFieldFactory;
import org.orekit.forces.gravity.potential.NormalizedSphericalHarmonicsProvider;
import org.orekit.forces.radiation.IsotropicRadiationSingleCoefficient;
import org.orekit.forces.radiation.SolarRadiationPressure;
import org.orekit.models.earth.atmosphere.NRLMSISE00;
import org.orekit.models.earth.atmosphere.data.CssiSpaceWeatherData;
import org.orekit.orbits.Orbit;
import org.orekit.propagation.numerical.NumericalPropagator;
import org.orekit.utils.Constants;
import org.orekit.utils.TimeStampedPVCoordinates;

public class NumericalPropagatorRef extends OrekitPropagatorRef {
    public NumericalPropagatorRef(TimeStampedPVCoordinates state_init, double prop_min_step, double prop_max_step, double prop_init_step,
            double prop_position_error, double mass, double cross_section, int[] grav_degree_order,
            String[] third_bodies, double c_r, boolean enable_srp, double c_d, boolean enable_drag) {
        super(state_init, prop_min_step, prop_max_step, prop_init_step, prop_position_error, mass, cross_section, grav_degree_order,
                third_bodies, c_r, enable_srp, c_d, enable_drag);
    }

    public void setup_propagator(Orbit orbit_sample) {
        double[][] tol = NumericalPropagator.tolerances(this.prop_position_error, orbit_sample, orbit_sample.getType());

        DormandPrince853Integrator integrator = new DormandPrince853Integrator(this.prop_min_step, this.prop_max_step,
                tol[0], tol[1]);
        integrator.setInitialStepSize(this.prop_init_step);

        this._orekit_prop = new NumericalPropagator(integrator);

        this.setup_force_models();
    }

    public void setup_force_models() {
        ((NumericalPropagator) this._orekit_prop).addForceModel(new NewtonianAttraction(Constants.EIGEN5C_EARTH_MU));

        if (this.grav_degree_order.length == 2) {

            NormalizedSphericalHarmonicsProvider gravity_provider = GravityFieldFactory.getNormalizedProvider(
                    this.grav_degree_order[0], this.grav_degree_order[1]);

            HolmesFeatherstoneAttractionModel gravity_attraction_model = new HolmesFeatherstoneAttractionModel(
                    this._wgs84_ellipsoid.getBodyFrame(), gravity_provider);
            ((NumericalPropagator) this._orekit_prop).addForceModel(gravity_attraction_model);

        }

        for (String body : this.third_bodies) {
            try {
                CelestialBody body_orekit = CelestialBodyFactory.getBody(body);
                ((NumericalPropagator) this._orekit_prop).addForceModel(new ThirdBodyAttraction(body_orekit));

            } catch (NullPointerException e) {
                // TODO: handle exception
            }
        }

        if (this.enable_srp) {

            IsotropicRadiationSingleCoefficient isotropic_rad = new IsotropicRadiationSingleCoefficient(
                    this.cross_section, this.c_r);

            ((NumericalPropagator) this._orekit_prop)
                    .addForceModel(new SolarRadiationPressure(this._sun, this._wgs84_ellipsoid, isotropic_rad));

        }
        if (this.enable_drag) {

            CssiSpaceWeatherData cswl = new CssiSpaceWeatherData("SpaceWeather-All-v1.2.txt");

            NRLMSISE00 atmosphere = new NRLMSISE00(cswl, this._sun, this._wgs84_ellipsoid);

            IsotropicDrag isotropic_drag = new IsotropicDrag(this.cross_section, this.c_d);

            ((NumericalPropagator) this._orekit_prop).addForceModel(new DragForce(atmosphere, isotropic_drag));
        }
    }
}
