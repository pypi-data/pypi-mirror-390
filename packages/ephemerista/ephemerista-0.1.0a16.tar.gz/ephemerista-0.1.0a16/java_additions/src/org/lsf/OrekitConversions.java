package org.lsf;

import java.util.ArrayList;

import org.orekit.frames.Frame;
import org.orekit.frames.FramesFactory;
import org.orekit.propagation.BoundedPropagator;
import org.orekit.time.AbsoluteDate;
import org.orekit.time.TimeScalesFactory;
import org.orekit.utils.TimeStampedPVCoordinates;

public class OrekitConversions {
    public static final AbsoluteDate J2000_TAI_EPOCH = new AbsoluteDate(2000, 1, 1, 12, 0, 0.0,
            TimeScalesFactory.getTAI());

    public static final Frame ICRF = FramesFactory.getGCRF();

    public static AbsoluteDate j2000TaiToAbsoluteDate(double j2000_seconds_TAI) {
        return new AbsoluteDate(J2000_TAI_EPOCH, j2000_seconds_TAI, TimeScalesFactory.getTAI());
    }

    public static AbsoluteDate[] j2000TaiToAbsoluteDate(double[] j2000_seconds_TAI) {
        AbsoluteDate[] out = new AbsoluteDate[j2000_seconds_TAI.length];
        for (int i = 0; i < out.length; i++) {
            out[i] = j2000TaiToAbsoluteDate(j2000_seconds_TAI[i]);
        }
        return out;
    }

    public static double[][] exportStates2D(BoundedPropagator prop, double[] times_j2000_TAI) {
        // Relative times to minDate

        ArrayList<double[]> statesArray = new ArrayList<double[]>();
        TimeStampedPVCoordinates tpv;
        double[] pos_km;
        double[] vel_km_s;
        AbsoluteDate curDate;
        AbsoluteDate minDate = prop.getMinDate();
        AbsoluteDate maxDate = prop.getMaxDate();

        AbsoluteDate[] dates = j2000TaiToAbsoluteDate(times_j2000_TAI);

        double timeStart_j2000 = times_j2000_TAI[0];
        int j;
        for (int i = 0; i < times_j2000_TAI.length; i++) {
            curDate = dates[i];
            if ((curDate.isBeforeOrEqualTo(maxDate)) && (curDate.isAfterOrEqualTo(minDate))) {
                tpv = prop.propagate(curDate).getPVCoordinates(ICRF);
                pos_km = tpv.getPosition().scalarMultiply(1e-3).toArray();
                vel_km_s = tpv.getVelocity().scalarMultiply(1e-3).toArray();
                double[] state = new double[7];
                state[0] = times_j2000_TAI[i] - timeStart_j2000;
                for (j = 0; j < 3; j++) {
                    state[j + 1] = pos_km[j];
                }
                for (j = 0; j < 3; j++) {
                    state[j + 4] = vel_km_s[j];
                }
                statesArray.add(state);
            }
        }

        double[][] out = new double[statesArray.size()][7];
        return statesArray.toArray(out);
    }

    public static double[][] exportStates2D(BoundedPropagator prop, double dt) {
        ArrayList<double[]> statesArray = new ArrayList<double[]>();
        TimeStampedPVCoordinates tpv;
        double[] pos_km;
        double[] vel_km_s;
        AbsoluteDate minDate = prop.getMinDate();
        AbsoluteDate maxDate = prop.getMaxDate();
        AbsoluteDate curDate = minDate;

        int j;
        while (curDate.isBeforeOrEqualTo(maxDate)) {
            tpv = prop.propagate(curDate).getPVCoordinates(ICRF);
            pos_km = tpv.getPosition().scalarMultiply(1e-3).toArray();
            vel_km_s = tpv.getVelocity().scalarMultiply(1e-3).toArray();
            double[] state = new double[7];
            state[0] = curDate.durationFrom(minDate);
            for (j = 0; j < 3; j++) {
                state[j + 1] = pos_km[j];
            }
            for (j = 0; j < 3; j++) {
                state[j + 4] = vel_km_s[j];
            }
            statesArray.add(state);

            curDate = curDate.shiftedBy(dt);
        }

        double[][] out = new double[statesArray.size()][7];
        return statesArray.toArray(out);
    }
}
