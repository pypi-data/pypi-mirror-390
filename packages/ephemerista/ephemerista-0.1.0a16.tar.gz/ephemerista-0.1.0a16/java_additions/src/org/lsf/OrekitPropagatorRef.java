package org.lsf;

import org.orekit.bodies.CelestialBody;
import org.orekit.bodies.CelestialBodyFactory;
import org.orekit.frames.Frame;
import org.orekit.frames.FramesFactory;
import org.orekit.models.earth.ReferenceEllipsoid;
import org.orekit.orbits.CartesianOrbit;
import org.orekit.orbits.EquinoctialOrbit;
import org.orekit.orbits.Orbit;
import org.orekit.propagation.BoundedPropagator;
import org.orekit.propagation.EphemerisGenerator;
import org.orekit.propagation.Propagator;
import org.orekit.propagation.SpacecraftState;
import org.orekit.propagation.events.ApsideDetector;
import org.orekit.propagation.events.handlers.StopOnDecreasing;
import org.orekit.propagation.events.handlers.StopOnIncreasing;
import org.orekit.time.AbsoluteDate;
import org.orekit.utils.Constants;
import org.orekit.utils.IERSConventions;
import org.orekit.utils.TimeStampedPVCoordinates;

public abstract class OrekitPropagatorRef {
    public TimeStampedPVCoordinates state_init;

    public double prop_min_step = 0.001;
    public double prop_max_step = 3600.0;
    public double prop_init_step = 60.0;
    public double prop_position_error = 10.0;

    public double mass = 1000.0;
    public double cross_section = 1.0;

    public int[] grav_degree_order = { 4, 4 };

    public String[] third_bodies;

    public double c_r = 0.75;
    public boolean enable_srp = false;

    public double c_d = 2.0;
    public boolean enable_drag = false;

    public Propagator _orekit_prop;
    public ReferenceEllipsoid _wgs84_ellipsoid;
    public CelestialBody _sun;
    public Frame _icrf;

    public OrekitPropagatorRef(TimeStampedPVCoordinates state_init, double prop_min_step, double prop_max_step, double prop_init_step,
            double prop_position_error, double mass, double cross_section, int[] grav_degree_order,
            String[] third_bodies, double c_r, boolean enable_srp, double c_d, boolean enable_drag) {
        this.state_init = state_init;
        this.prop_min_step = prop_min_step;
        this.prop_max_step = prop_max_step;
        this.prop_init_step = prop_init_step;
        this.prop_position_error = prop_position_error;
        this.mass = mass;
        this.cross_section = cross_section;
        this.grav_degree_order = grav_degree_order;
        this.third_bodies = third_bodies;
        this.c_r = c_r;
        this.enable_srp = enable_srp;
        this.c_d = c_d;
        this.enable_drag = enable_drag;
        this.setup_orekit_objs();
    }

    public void setup_orekit_objs() {
        this._icrf = FramesFactory.getGCRF();

        Frame itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, false);

        this._wgs84_ellipsoid = ReferenceEllipsoid.getWgs84(itrf);

        this._sun = CelestialBodyFactory.getSun();

        CartesianOrbit orbit_init_cart = new CartesianOrbit(this.state_init, this._icrf, Constants.EIGEN5C_EARTH_MU);
        EquinoctialOrbit orbit_init_equinoctial = new EquinoctialOrbit(orbit_init_cart);

        this.setup_propagator(orbit_init_equinoctial);
        this.set_initial_state(this.state_init);
    }

    public abstract void setup_propagator(Orbit orbit_sample);

    public void set_initial_state(TimeStampedPVCoordinates tpv_icrf) {
        CartesianOrbit orbit_init_cart = new CartesianOrbit(tpv_icrf, this._icrf, Constants.EIGEN5C_EARTH_MU);
        EquinoctialOrbit orbit_init_equinoctial = new EquinoctialOrbit(orbit_init_cart);

        SpacecraftState state_init_orekit = new SpacecraftState(orbit_init_equinoctial, this.mass);
        this._orekit_prop.resetInitialState(state_init_orekit);
    }

    public void add_stop_condition(Event stop_cond) {
        if (stop_cond == Event.PERIAPSIS) {

            ApsideDetector periapsis_detector = new ApsideDetector(this._orekit_prop.getInitialState().getOrbit())
                    .withHandler(
                            new StopOnIncreasing());
            this._orekit_prop.addEventDetector(periapsis_detector);
        } else if (stop_cond == Event.APOAPSIS) {
            ApsideDetector apoapsis_detector = new ApsideDetector(this._orekit_prop.getInitialState().getOrbit())
                    .withHandler(
                            new StopOnDecreasing());
            this._orekit_prop.addEventDetector(apoapsis_detector);
        }
    }

    public TimeStampedPVCoordinates propagate(
            AbsoluteDate time,
            Event[] stop_conds) {

        this._orekit_prop.clearEventsDetectors();
        for (Event stop_cond : stop_conds) {
            this.add_stop_condition(stop_cond);
        }
        SpacecraftState state_end = this._orekit_prop.propagate(time);
        return state_end.getPVCoordinates();
    }

    public double[][] propagate(
            double[] times_j2000_TAI,
            AbsoluteDate time_end,
            Event[] stop_conds) {

        this._orekit_prop.clearEventsDetectors();
        for (Event stop_cond : stop_conds) {
            this.add_stop_condition(stop_cond);
        }
        EphemerisGenerator eph_generator = this._orekit_prop.getEphemerisGenerator();
        this._orekit_prop.propagate(time_end);
        BoundedPropagator bounded_propagator = eph_generator.getGeneratedEphemeris();

        return OrekitConversions.exportStates2D(bounded_propagator, times_j2000_TAI);
    }
}
