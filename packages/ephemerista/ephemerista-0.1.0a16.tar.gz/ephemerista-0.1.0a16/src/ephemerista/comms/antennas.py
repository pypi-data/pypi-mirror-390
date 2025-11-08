"""The antennas.py module.

This module provides several classes for modelling radio antennas and their gain patterns.
"""

import abc
import math
import os
from typing import Literal, Self

import branca
import folium
import geojsoncontour
import numpy as np
import numpy.typing as npt
import pandas as pd
import plotly.graph_objects as go
import pydantic_numpy.typing as pnd
import scipy
from folium import plugins as folium_plugins
from matplotlib import pyplot as plt
from numpy.typing import ArrayLike
from pydantic import Field, PrivateAttr
from pydantic.json_schema import SkipJsonSchema
from scipy.interpolate import griddata

from ephemerista import BaseModel, Vec3
from ephemerista.comms.frequencies import Frequency
from ephemerista.comms.utils import to_db, wavelength
from ephemerista.coords.twobody import TwoBody
from ephemerista.math import cone_vectors
from ephemerista.propagators.orekit.conversions import time_to_abs_date

ANTENNA_DISCRIMINATOR = "antenna_type"
PATTERN_DISCRIMINATOR = "pattern_type"

"""
When dividing by a quantity, if this quantity is lower than this threshold,
an alternate formulation will be used to avoid division by zero
"""
DIV_BY_ZERO_LIMIT = 1e-6

"""
Represents the lowest gain value in linear representation, because zero gain
would lead to an error when converting to dB.
This value represents a signal strength in dB so low that no link will probably be possible.
"""
MINF_GAIN_LINEAR = 1e-12

SHORT_DIPOLE_LIMIT = 0.1  # when length/wavelength lower than this value, it is officially a short dipole


class Antenna(BaseModel, abc.ABC):
    """Abstract base class for antenna models."""

    design_frequency: Frequency | None = Field(default=None, description="The design frequency of the antenna")
    boresight_vector: Vec3 = Field(
        description="""The boresight vector of the antenna in the local reference frame (LVLH when attached to a
        spacecraft, SEZ when attached to a ground station)""",
        default=(0.0, 0.0, 1.0),
    )

    @abc.abstractmethod
    def gain(self, frequency: Frequency, angle: float) -> float:
        """Return the gain of the antenna for a given frequency and elevation."""
        raise NotImplementedError()

    @abc.abstractmethod
    def beamwidth(self, frequency: Frequency) -> float:
        """Return the half-power beamwidth of the antenna for a given frequency."""
        raise NotImplementedError()

    @property
    def boresight_array(self) -> np.ndarray:
        """numpy.ndarray: boresight vector."""
        return np.array(self.boresight_vector)

    def viz_cone_3d(
        self,
        frequency: Frequency,
        sc_state: TwoBody,
        beamwidth_deg: float | None = None,
        cone_length: float | None = None,  # cone length in kilometers
        opacity: float = 0.5,
        name: str | None = None,
        **kwargs,
    ) -> go.Surface:
        """
        Plot the antenna's beamwidth as a 3D cone.

        Notes
        -----
        The beamwidth is optional. If None, the antenna's beamwidth will be used.
        All keywords arguments are passed to plotly's go.Surface method to tune the plot.
        """
        # TODO: make the sc_state param optional. That would require the following:
        #     - enforcing cone_length is not None
        #     - use the antenna's boresight vector in LVLH frame without converting it to ECI frame
        #         (which means the 3D visualization will be in LVLH coordinate system)
        if not beamwidth_deg:
            beamwidth_deg = np.rad2deg(self.beamwidth(frequency))

        sat_pos = sc_state.to_cartesian().position
        if not cone_length:
            cone_length = np.linalg.norm(sat_pos)

        if not name:
            name = "Antenna cone"

        eci_from_lvlh = sc_state.to_cartesian().rotation_lvlh()
        boresight_eci = eci_from_lvlh @ self.boresight_array

        angle_res_deg = 10.0
        cone_dirs, _ = cone_vectors(
            boresight_eci, theta_deg=beamwidth_deg, angle_res_deg=angle_res_deg, include_endpoint=True
        )
        cone_lengths = np.linspace(0, cone_length, 10)
        cone_dirs_3d = np.zeros((len(cone_lengths), cone_dirs.shape[0], cone_dirs.shape[1]))
        for i, cone_len in enumerate(cone_lengths):
            cone_dirs_3d[i, :, :] = cone_len * cone_dirs

        cone_vec_3d = cone_dirs_3d + sat_pos

        viz_cone = go.Surface(
            x=cone_vec_3d[:, :, 0],
            y=cone_vec_3d[:, :, 1],
            z=cone_vec_3d[:, :, 2],
            showscale=False,
            opacity=opacity,
            surfacecolor=np.linalg.norm(cone_dirs_3d, axis=2),
            name=name,
            **kwargs,
        )
        return viz_cone


class SimpleAntenna(Antenna):
    """The `SimpleAntenna` class.

    This class provides a simplified antenna model that uses fixed gain and half-power beamwidth values.
    """

    antenna_type: Literal["simple"] = Field(
        default="simple", alias="type", repr=False, frozen=True, description="Simple antenna type"
    )
    gain_db: float = Field(ge=0.0, json_schema_extra={"title": "Gain"}, description="Antenna gain in dBi")
    beamwidth_deg: float = Field(ge=0.0, json_schema_extra={"title": "Beamwidth"}, description="Beamwidth in degrees")

    def gain(self, frequency: Frequency, angle: float) -> float:  # noqa: ARG002
        """Return the gain of the antenna for a given frequency and elevation."""
        return self.gain_db

    def beamwidth(self, frequency: Frequency) -> float:  # noqa: ARG002
        """Return the half-power beamwidth of the antenna for a given frequency."""
        return np.deg2rad(self.beamwidth_deg)


class Pattern(BaseModel, abc.ABC):
    """Abstract base class for gain patterns."""

    @abc.abstractmethod
    def gain(self, frequency: Frequency, angle: float) -> float:
        """Return the gain of the antenna for a given frequency and elevation."""
        raise NotImplementedError()

    @abc.abstractmethod
    def beamwidth(self, frequency: Frequency) -> float:
        """Return the half-power beamwidth of the antenna for a given frequency in radians."""
        raise NotImplementedError()


class ParabolicPattern(Pattern):
    """The `ParabolicPattern` class.

    This class models the gain pattern of a parabolic antenna.
    """

    pattern_type: Literal["parabolic"] = Field(
        default="parabolic", alias="type", repr=False, frozen=True, description="Parabolic pattern type"
    )
    diameter: float = Field(gt=0.0, description="Antenna diameter in meters")
    efficiency: float = Field(gt=0.0, le=1.0, default=0.65, description="Antenna efficiency, between 0 and 1")

    _bessel_first_root: float = PrivateAttr(default=scipy.special.jn_zeros(1, 1)[0])

    @classmethod
    def from_beamwidth(cls, beamwidth: float, frequency: Frequency) -> Self:
        """
        Build an equivalent parabolic antenna from the given beamwidth and frequency.

        Parameters
        ----------
        beamwidth : float
            Half-power beamwidth in radians
        frequency : Frequency
            Frequency
        """
        return cls(diameter=1.22 * wavelength(frequency.hertz) / beamwidth)

    @property
    def area(self) -> float:
        """float: area of the parabolic antenna."""
        return math.pi * self.diameter**2 / 4

    def beamwidth(self, frequency: Frequency) -> float:
        """Return the half-power beamwidth of the antenna for a given frequency in radians."""
        return np.arcsin(self._bessel_first_root * wavelength(frequency.hertz) / np.pi / self.diameter)

    def peak_gain(self, frequency: Frequency) -> float:
        """Return the peak gain of the parabolic antenna for a given frequency."""
        lamb = wavelength(frequency.hertz)
        g = to_db(4 * math.pi * self.area / lamb**2)
        return g + to_db(self.efficiency)

    def gain(self, frequency: Frequency, angle: ArrayLike) -> np.ndarray:
        """Return the gain of the parabolic antenna for a given frequency and elevation.

        Notes
        -----
        Assumes an uniform illuminated aperture (i.e. taper parameter tau = 1.0)

        References
        ----------
        Equation (17) of https://web.archive.org/web/20160101021857/https://library.nrao.edu/public/memos/alma/memo456.pdf.
        """
        u = np.pi * self.diameter / wavelength(frequency.hertz) * np.sin(angle)

        with np.testing.suppress_warnings() as sup:
            # Ugly but otherwise we get 'RuntimeWarning: invalid value encountered in scalar divide' warnings,
            # but we actually don't use the values issuing these warnings thanks to the np.where call
            sup.filter(RuntimeWarning)

            pattern_loss_linear = np.where(
                np.abs(u) < DIV_BY_ZERO_LIMIT,  # Preventing division by zero at zero angle
                1.0,  # Maximum gain (relative to peak gain)
                np.square(2 * scipy.special.jv(1, u) / u),
            )
            # Setting very low gain at angles higher than 45 degrees
            # This is because the pattern equation used is symmetrical, that would result in
            # the backlobe having the same gain as the main lobe, which is wrong...

            # Besides, this equation also does not model spillover radation from the feed missing the reflector,
            # so it does not make sense to use it for high angles.
            # For basically any parabolic antenna, if the depointing is higher than 45 degrees,
            # you will barely receive anything...
            pattern_loss_linear = np.where(
                np.cos(angle) < np.cos(np.pi / 2),
                MINF_GAIN_LINEAR,  # very small value otherwise conversion to dB fails
                pattern_loss_linear,
            )

            return self.peak_gain(frequency=frequency) + to_db(pattern_loss_linear)


class GaussianPattern(Pattern):
    """The `GaussianPattern` class.

    This class models a Gaussian gain pattern.
    """

    pattern_type: Literal["gaussian"] = Field(default="gaussian", alias="type", description="Gaussian antenna pattern")
    diameter: float = Field(gt=0.0, description="Antenna diameter in meters")
    efficiency: float = Field(gt=0.0, le=1.0, description="Antenna efficiency, between 0 and 1")

    def beamwidth(self, frequency: Frequency) -> float:
        """Return the half-power beamwidth of the antenna for a given frequency in radians.

        References
        ----------
        https://uk.mathworks.com/help/satcom/ref/satcom.satellitescenario.transmitter.gaussianantenna.html.
        """
        return np.deg2rad(70 * wavelength(frequency.hertz) / self.diameter)

    def peak_gain(self, frequency: Frequency) -> float:
        """Return the peak gain of the Gaussian antenna for a given frequency."""
        lamb = wavelength(frequency.hertz)
        return to_db(self.efficiency * (math.pi * self.diameter / lamb) ** 2)

    def gain(self, frequency: Frequency, angle: ArrayLike) -> np.ndarray:
        """Return the gain of the Gaussian antenna for a given frequency and elevation.

        References
        ----------
        https://uk.mathworks.com/help/satcom/ref/satcom.satellitescenario.transmitter.gaussianantenna.html.
        """
        pattern_loss_linear = np.exp(-(4 * np.log(2) * ((angle / self.beamwidth(frequency)) ** 2)))

        # Note: MATLAB's gaussianAntenna implementation does not use a gain floor.
        # The pure Gaussian formula can produce extremely low gains (< -1000 dB) at large
        # off-boresight angles, which MATLAB handles through numerical underflow to zero.

        return self.peak_gain(frequency=frequency) + to_db(pattern_loss_linear)


MSI_FIELDS = (
    "NAME",
    "MAKE",
    "FREQUENCY",
    "H_WIDTH",
    "V_WIDTH",
    "FRONT_TO_BACK",
    "GAIN",
    "TILT",
    "POLARIZATION",
    "COMMENT",
)


class UndefinedBeamwidthError(Exception):
    """Raise if the MSI Planet file did not provide a beamwidth."""

    pass


class MSIPatternData(BaseModel):
    """The `MSIPatternData` class.

    This class models the data contained in an MSI Planet file.
    """

    name: str = Field(description="Name of the antenna")
    make: str | None = Field(default=None, description="Manufacturer of the antenna")
    frequency: Frequency = Field(description="Design frequency of the antenna in Hz")
    h_width: float | None = Field(default=None, description="Horizontal 3 dB beamwidth")
    v_width: float | None = Field(default=None, description="Vertical 3 dB beamwidth")
    front_to_back: float | None = Field(default=None, description="Front-to-back ratio in dB")
    peak_gain: float = Field(description="Peak gain of the antenna in dBd or dBi")
    gain_unit: Literal["dBd", "dBi"] = Field(description="Unit of the peak gain")
    tilt: float | None = Field(default=None, description="Electrical tilt of the main beam in degrees")
    comment: str | None = Field(default=None)
    horizontal: SkipJsonSchema[pnd.Np1DArrayFp64]
    vertical: SkipJsonSchema[pnd.Np1DArrayFp64]


class MSIPattern(Pattern):
    """The `MSIPattern` class.

    This class provides the ability to import custom antenna pattern from other applications as
    MSI Planet files.
    """

    pattern_type: Literal["msi"] = Field(default="msi", alias="type", repr=False, frozen=True)
    filename: str = Field(description="Name of the MSI file")
    content: str = Field(description="Content of the MSI file")
    _pattern: MSIPatternData = PrivateAttr()

    def __init__(self, **data):
        super().__init__(**data)

        lines = self.content.splitlines()

        fields: dict[str, str | float | npt.ArrayLike | Frequency | None] = {
            field.lower(): next((line.split(maxsplit=1)[-1].strip() for line in lines if line.startswith(field)), None)
            for field in MSI_FIELDS
        }

        if fields["gain"] and isinstance(fields["gain"], str):
            peak_gain, gain_unit = fields["gain"].split()
            fields["peak_gain"] = float(peak_gain)
            fields["gain_unit"] = gain_unit

        if fields["frequency"] and isinstance(fields["frequency"], str):
            frequency_mhz = fields["frequency"]
            fields["frequency"] = Frequency.megahertz(float(frequency_mhz))

        h_start = lines.index("HORIZONTAL 360") + 1
        v_start = lines.index("VERTICAL 360") + 1

        fields["horizontal"] = np.array([float(line.split()[-1]) for line in lines[h_start : v_start - 1]])
        fields["vertical"] = np.array([float(line.split()[-1]) for line in lines[v_start:]])

        self._pattern = MSIPatternData.model_validate(fields)

    @classmethod
    def read_file(cls, file: str | os.PathLike) -> Self:
        """Read an MSI Planet file."""
        with open(file) as f:
            content = f.read()

        return cls(filename=str(file), content=content)

    @property
    def frequency(self) -> Frequency:
        """Frequency: the design frequency for which the pattern is valid."""
        return self._pattern.frequency

    def beamwidth(self, frequency: Frequency) -> float:  # noqa: ARG002
        """Return the half-power beamwidth of the antenna pattern."""
        if not self._pattern.v_width:
            raise UndefinedBeamwidthError
        return self._pattern.v_width

    def gain(self, frequency: Frequency, angle: float) -> float:
        """Return the gain of the antenna pattern for a given frequency and elevation.

        Notes
        -----
        This method will throw an exception if the frequency of the MSI file and the given frequency
        are not within the same frequency band.
        """
        if frequency.band != self._pattern.frequency.band:
            msg = f"gain pattern is defined for {self._pattern.frequency} Hz but {frequency.hertz} Hz are required"
            raise ValueError(msg)
        angle = np.degrees(np.where(angle < -np.pi / 2, angle + 2 * np.pi, angle) + np.pi / 2)
        gain = self._pattern.peak_gain - np.interp(angle, np.arange(0, 360), self._pattern.vertical)
        if self._pattern.gain_unit == "dBd":
            return gain + 2.15
        else:
            return gain


class DipolePattern(Pattern):
    """The `DipolePattern` class.

    This class models the gain pattern of a dipole antenna.
    """

    pattern_type: Literal["dipole"] = Field(default="dipole", alias="type", description="Dipole pattern type")
    length: float = Field(gt=0.0, description="Antenna length in meters")

    def beamwidth(self, frequency: Frequency) -> float:  # noqa: ARG002
        """
        Return the beamwidth of the dipole pattern.

        Notes
        -----
        Always returns 180 degrees, because the concept of beamwidth is undefined with dipole antennas:
        a dipole antennas has several main lobes of sometimes different widths.
        """
        return np.pi

    def gain_pattern(self, frequency: Frequency, angle: ArrayLike) -> np.ndarray:
        """
        Return the gain relative to the peak gain, in linear units, between 0 and 1.

        References
        ----------
        Source 1: Slide 17 of https://www.brown.edu/research/labs/mittleman/sites/brown.edu.research.labs.mittleman/files/uploads/lecture25.pdf
        Source 2: https://www.antenna-theory.com/antennas/dipole.php
        Source 3: https://en.wikipedia.org/wiki/Dipole_antenna#Short_dipole
        Source 4: https://www.antenna-theory.com/antennas/shortdipole.php.
        """
        with np.testing.suppress_warnings() as sup:
            # TODO: Ugly but otherwise we get 'RuntimeWarning: divide by zero encountered in scalar divide' warnings,
            # but we actually don't use the values issuing these warnings thanks to the np.where call
            sup.filter(RuntimeWarning)

            k = 2 * np.pi / wavelength(frequency=frequency.hertz)
            kl2 = k * self.length / 2

            return np.where(
                np.abs(np.sin(angle)) < DIV_BY_ZERO_LIMIT,  # Avoid division by zero when np.sin(angle) is small
                MINF_GAIN_LINEAR,  # very small value otherwise the conversion to dB is not happy
                np.where(
                    self.length / wavelength(frequency=frequency.hertz) < SHORT_DIPOLE_LIMIT,
                    np.square(np.sin(angle)),  # Alternative formulation for short dipole
                    np.square((np.cos(kl2 * np.cos(angle)) - np.cos(kl2)) / np.sin(angle)),  # General dipole
                ),
            )

    def directivity(self, frequency: Frequency) -> float:
        """Return the directivity of the dipole pattern for a given frequency."""
        integral, _ = scipy.integrate.quad(
            lambda angle, frequency: self.gain_pattern(frequency=frequency, angle=angle) * np.sin(angle),
            0,
            np.pi,
            args=(frequency,),
        )
        return 2 / integral

    def peak_gain(self, frequency: Frequency) -> float:
        """Return the peak gain of the dipole pattern for a given frequency."""
        optimum = scipy.optimize.minimize_scalar(lambda x: -to_db(self.gain_pattern(frequency=frequency, angle=x)))
        return -optimum.fun + to_db(self.directivity(frequency=frequency))

    def gain(self, frequency: Frequency, angle: ArrayLike) -> np.ndarray:
        """Return the gain of the dipole pattern for a given frequency and elevation."""
        return to_db(self.directivity(frequency=frequency)) + to_db(self.gain_pattern(frequency=frequency, angle=angle))


type PatternType = ParabolicPattern | DipolePattern | GaussianPattern | MSIPattern


class ComplexAntenna(Antenna):
    """The `ComplexAntenna` class.

    This class models a complex antenna with a specified antenna gain pattern.
    """

    antenna_type: Literal["complex"] = Field(
        default="complex", alias="type", repr=False, frozen=True, description="Complex antenna type"
    )
    pattern: PatternType = Field(discriminator=PATTERN_DISCRIMINATOR, description="Pattern type discriminator")

    def gain(self, frequency: Frequency, angle: ArrayLike) -> np.ndarray:
        """Return the gain of the antenna for the given frequency and elevation."""
        return self.pattern.gain(frequency, angle)

    def beamwidth(self, frequency: Frequency) -> float:
        """Return the half-power beamwidth of the antenna for the given frequency."""
        return self.pattern.beamwidth(frequency)

    def peak_gain(self, frequency: Frequency) -> float:
        """Return the peak gain of the antenna for the given frequency."""
        return self.pattern.peak_gain(frequency=frequency)

    def plot_pattern(
        self,
        frequency: Frequency,
        fig_style: Literal["polar", "linear"] = "polar",
        trace_name: str | None = None,
        *,
        relative_to_peak: bool = False,
    ) -> go.Scatterpolar | go.Scatter | None:
        """Plot the antenna gain pattern."""
        theta_array = np.arange(-np.pi, np.pi, 1e-3)
        gain_array = self.gain(frequency=frequency, angle=theta_array)
        if relative_to_peak:
            gain_array = gain_array - self.peak_gain(frequency=frequency)

        if fig_style == "polar":
            return go.Scatterpolar(
                r=gain_array,
                theta=np.rad2deg(theta_array),
                mode="lines",
                name=trace_name,
            )

        elif fig_style == "linear":
            return go.Scatter(y=gain_array, x=np.rad2deg(theta_array), mode="lines", name=trace_name)

    def plot_contour_2d(self, frequency: Frequency, sc_state: TwoBody, gain_dynamic: float = 75) -> folium.Map:
        """
        Create a folium interactive map with the antenna beam contour.

        References
        ----------
        Largely inspired by https://github.com/python-visualization/folium/issues/958#issuecomment-427156672.
        """
        gain_coords_df = self.to_geo_df(frequency, sc_state)

        # Setup colormap
        colors = ["#f0f921", "#febd2a", "#f48849", "#db5c68", "#b83289", "#8b0aa5", "#5302a3"]
        vmax = gain_coords_df["gain"].max()
        gain_coords_df = gain_coords_df.loc[gain_coords_df["gain"] >= vmax - gain_dynamic]
        vmin = gain_coords_df["gain"].min()
        levels = len(colors)

        # Make a grid
        x_arr = np.linspace(gain_coords_df["lon_deg"].min(), gain_coords_df["lon_deg"].max(), 800)
        y_arr = np.linspace(gain_coords_df["lat_deg"].min(), gain_coords_df["lat_deg"].max(), 800)
        x_mesh, y_mesh = np.meshgrid(x_arr, y_arr)

        # Grid the values
        z_mesh = griddata(
            (gain_coords_df["lon_deg"], gain_coords_df["lat_deg"]),
            gain_coords_df["gain"],
            (x_mesh, y_mesh),
            method="linear",
        )

        # Gaussian filter the grid to make it smoother
        sigma = [5, 5]

        # Set up the folium plot
        geomap = folium.Map(
            [gain_coords_df["lat_deg"].mean(), gain_coords_df["lon_deg"].mean()], zoom_start=4, tiles="cartodbpositron"
        )

        # Plot the contour plot on folium
        folium.GeoJson(
            geojsoncontour.contourf_to_geojson(
                contourf=plt.contourf(
                    x_mesh,
                    y_mesh,
                    scipy.ndimage.gaussian_filter(z_mesh, sigma, mode="constant"),
                    levels - 1,
                    alpha=0.9,
                    colors=colors,
                    linestyles="None",
                    vmin=vmin,
                    vmax=vmax,
                ),
                min_angle_deg=3.0,
                ndigits=5,
                stroke_width=1,
                fill_opacity=0.8,
            ),
            style_function=lambda x: {
                "color": x["properties"]["stroke"],
                "weight": x["properties"]["stroke-width"],
                "fillColor": x["properties"]["fill"],
                "opacity": 0.6,
            },
        ).add_to(geomap)

        # Add the colormap to the folium map
        geomap.add_child(
            branca.colormap.LinearColormap(colors, vmin=vmin, vmax=vmax, caption="Gain [dB]").to_step(levels)
        )

        # Fullscreen mode
        folium_plugins.Fullscreen(position="topright", force_separate_button=True).add_to(geomap)

        if plt.get_backend() == "module://matplotlib_inline.backend_inline" and len(plt.get_fignums()) > 0:
            # Close matplotlib plot opened by plt.contourf, annoying when working in a jupyter notebook
            plt.close("all")

        return geomap

    def to_geo_df(self, frequency: Frequency, sc_state: TwoBody) -> pd.DataFrame:
        """Return a dataframe containing the ground coordinates of the antenna beam (i.e. gain)."""
        # TODO: project the vectors onto the Earth spheroid without resorting to Orekit.
        from org.hipparchus.geometry.euclidean.threed import Line, Vector3D  # type: ignore  # noqa: PLC0415
        from org.orekit.frames import FramesFactory  # type: ignore  # noqa: PLC0415
        from org.orekit.models.earth import ReferenceEllipsoid  # type: ignore  # noqa: PLC0415
        from org.orekit.utils import IERSConventions  # type: ignore  # noqa: PLC0415

        icrf = FramesFactory.getGCRF()  # Earth-centered ICRF

        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)

        wgs84_ellipsoid = ReferenceEllipsoid.getWgs84(itrf)
        orekit_date = time_to_abs_date(sc_state.time)

        theta_res_deg = 0.5
        phi_res_deg = 1.0
        theta_array = np.arange(0, np.pi / 2, np.deg2rad(theta_res_deg))
        gain_array = self.gain(frequency=frequency, angle=theta_array)

        eci_from_lvlh = sc_state.to_cartesian().rotation_lvlh()
        sc_pos_eci = 1e3 * sc_state.to_cartesian().position
        sc_pos_orekit = Vector3D(sc_pos_eci)
        boresight_eci = eci_from_lvlh @ self.boresight_array

        records = []
        # Convert theta array to boresight vectors
        for theta_deg, gain in zip(np.rad2deg(theta_array), gain_array, strict=False):
            if theta_deg > 90:  # noqa: PLR2004
                continue

            # Because antennas as of now are phi-invariant and only depend on theta, we generate a cone and a phi array
            cone_vecs_eci, phi_array = cone_vectors(v1=boresight_eci, theta_deg=theta_deg, angle_res_deg=phi_res_deg)

            for phi_deg, cone_vec_eci in zip(np.rad2deg(phi_array), cone_vecs_eci, strict=False):
                cone_line = Line.fromDirection(sc_pos_orekit, Vector3D(cone_vec_eci), 1.0)
                geodetic_point = wgs84_ellipsoid.getIntersectionPoint(cone_line, sc_pos_orekit, icrf, orekit_date)
                if not geodetic_point:
                    #  No intersection point was found
                    continue

                records.append(
                    {
                        "theta_deg": theta_deg,
                        "phi_deg": phi_deg,
                        "gain": gain,
                        "lat_deg": np.rad2deg(geodetic_point.getLatitude()),
                        "lon_deg": np.rad2deg(geodetic_point.getLongitude()),
                    }
                )

        gain_coords_df = pd.DataFrame.from_records(records)

        return gain_coords_df


type AntennaType = SimpleAntenna | ComplexAntenna
