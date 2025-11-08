import numpy as np
from pytest import approx

from ephemerista.comms.antennas import DipolePattern, ParabolicPattern
from ephemerista.comms.frequencies import Frequency
from ephemerista.comms.receiver import ComplexReceiver
from ephemerista.comms.utils import wavelength

frequency = Frequency.gigahertz(29.0)

parabolic = ParabolicPattern(diameter=0.98, efficiency=0.45)


def test_wavelength():
    act = wavelength(frequency)
    exp = 0.010337670965517241
    assert act == approx(exp)


def test_parabolic_beamwidth():
    exp = np.deg2rad(0.7371800047831003)
    act = parabolic.beamwidth(frequency)
    assert act == approx(exp)


def test_parabolic_peak_gain():
    exp = 46.01119000490658
    actual_gain = parabolic.gain(frequency, 0.0)
    actual_peak_gain = parabolic.peak_gain(frequency)
    assert actual_gain == approx(exp)
    assert actual_peak_gain == approx(exp)


def test_parabolic_gain_array():
    theta_array = np.array([0.0, np.pi])
    peak_gain = parabolic.peak_gain(frequency)
    gain_array = parabolic.gain(frequency, theta_array)
    assert gain_array[0] == peak_gain
    assert gain_array[-1] < -50  # should be a very small value


def test_parabolic_gain_hpbw():
    """
    Compute the gain at the half power beamwidth
    It's a zero of the Bessel function so it should be very very small
    """
    beamwidth = parabolic.beamwidth(frequency)
    actual_gain = parabolic.gain(frequency, beamwidth)
    assert actual_gain < -100.0


def test_half_wavelength_dipole_zero_gain():
    dipole_halfwavelength = DipolePattern(length=wavelength(frequency) / 2)
    act = dipole_halfwavelength.gain(frequency, 0.0)
    assert act < -50.0  # very very small gain


def test_half_wavelength_dipole_peak_gain_array():
    dipole_halfwavelength = DipolePattern(length=wavelength(frequency) / 2)
    exp = 2.15  # dBi

    theta_array = np.array([-np.pi / 2, np.pi / 2])  # peak gains are at pi/2 and -pi/2
    gain_array = dipole_halfwavelength.gain(frequency, theta_array)
    for act_gain in gain_array:
        assert act_gain == approx(exp, abs=1e-3)


def test_short_dipole_peak_gain():
    dipole_short = DipolePattern(length=wavelength(frequency) / 100)  # very short dipole
    peak_gain_exp = 1.76  # https://en.wikipedia.org/wiki/Dipole_antenna#Dipole_antennas_of_various_lengths
    assert dipole_short.peak_gain(frequency) == approx(peak_gain_exp, abs=0.1)


def test_1_25_wavelength_dipole_peak_gain():
    dipole_short = DipolePattern(length=1.25 * wavelength(frequency))
    peak_gain_exp = 5.2  # https://en.wikipedia.org/wiki/Dipole_antenna#Dipole_antennas_of_various_lengths
    assert dipole_short.peak_gain(frequency) == approx(peak_gain_exp, abs=0.1)


def test_1_5_wavelength_dipole_peak_gain_array():
    dipole_1_5_wavelength = DipolePattern(length=3 * wavelength(frequency) / 2)
    exp = 3.5  # dBi

    theta_array = np.array(
        [np.pi / 4, 3 * np.pi / 4, 5 * np.pi / 4, 7 * np.pi / 4]
    )  # peak gains are at 45, 135, 225 and 315°
    gain_array = dipole_1_5_wavelength.gain(frequency, theta_array)
    for act_gain in gain_array:
        assert act_gain == approx(exp, abs=0.1)


def test_receiver():
    rx = ComplexReceiver(frequency=Frequency.gigahertz(20.0), lna_gain=20, lna_noise_figure=4, noise_figure=5, loss=3)
    act_noise_temp = rx.noise_temperature
    exp_noise_temp = 627.0605214
    assert act_noise_temp == approx(exp_noise_temp)
    act_system_temp = rx.system_noise_temperature
    exp_system_temp = 904.53084061
    assert act_system_temp == approx(exp_system_temp)


def test_frequency_band():
    freq = Frequency.megahertz(70.0)
    assert freq.band == "VHF"


def test_frequency_units():
    assert Frequency(1).hertz == 1
    assert Frequency.kilohertz(1).hertz == 1000
    assert Frequency.megahertz(1).hertz == 1000000
    assert Frequency.gigahertz(1).hertz == 1000000000
    assert Frequency.terahertz(1).hertz == 1000000000000


def test_parabolic_from_beamdwidth():
    beamwidth = 0.1
    f = Frequency.gigahertz(2.0)
    parabol = ParabolicPattern.from_beamwidth(beamwidth, f)
    assert parabol.beamwidth(f) == approx(beamwidth, rel=0.01)
