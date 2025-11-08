"""The main `ephemerista` package."""

import os
from pathlib import Path
from typing import Annotated, Literal

import lox_space as lox
import orekit_jpype
import pydantic
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseModel(pydantic.BaseModel):
    """A customised `pydantic.BaseModel` that is the base class for all Ephemerista models."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


UT1Provider = lox.UT1Provider
Ephemeris = lox.SPK

EOP_PROVIDER: UT1Provider | None = None
EPHEMERIS: Ephemeris | None = None

JAR_FILE = "ephemeristaJava-0.0.1-SNAPSHOT.jar"


def init(
    *,
    eop_path: str | os.PathLike | None = None,
    spk_path: str | os.PathLike | None = None,
    jvm_path: str | os.PathLike | None = None,
    orekit_data: str | list[str] | os.PathLike | list[os.PathLike] | Literal["package"] = "package",
):
    """Initialise Ephemerista.

    This function loads the required data files and starts a JVM to enable the Orekit-based functionality of
    Ephemerista.

    Parameters
    ----------
    eop_path: str | os.PathLike, optional
        Path to the Earth Orientation Parameters file, e.g. ``finals2000A.all.csv`
    spk_path: str | os.PathLike, optional
        Path to a planetary ephemeris in SPK format
    jvm_path: str | os.PathLike, optional
        Path to a Java Virtual Machine (JVM) installation. By default the bundled JVM from ``jdk4py`` is used.
    orekit_data: str | os.PathLike, optional
        Path to an Orekit data package. The default assumes that the data package was installed as a Python package.
    """
    if eop_path:
        global EOP_PROVIDER  # noqa: PLW0603
        EOP_PROVIDER = lox.UT1Provider(str(eop_path))

    if spk_path:
        global EPHEMERIS  # noqa: PLW0603
        EPHEMERIS = lox.SPK(str(spk_path))

    ephemerista_jar = Path(__file__).parent / "jars" / JAR_FILE

    if not ephemerista_jar.is_file():
        msg = f"{ephemerista_jar} not found"
        raise FileNotFoundError(msg)

    additional_classpaths = [str(ephemerista_jar)]

    if (jvm_path is None) and ("JAVA_HOME" not in os.environ):
        import jdk4py  # noqa: PLC0415

        os.environ["JAVA_HOME"] = str(jdk4py.JAVA_HOME)

    orekit_jpype.initVM(additional_classpaths=additional_classpaths, jvmpath=jvm_path)

    filenames: str | list[str] | None = None
    from_pip_library = orekit_data == "package"

    if not from_pip_library:
        if isinstance(orekit_data, list):
            filenames = [str(f) for f in orekit_data]
        else:
            filenames = str(orekit_data)

    orekit_jpype.pyhelpers.setup_orekit_data(filenames=filenames, from_pip_library=from_pip_library)  # type: ignore


class MissingProviderError(Exception):
    """EOP provider was requested but was not initialised via `init`."""

    pass


def get_eop_provider() -> UT1Provider | None:
    """Return the EOP provider or ``None`` if it is uninitialised."""
    return EOP_PROVIDER


def eop_provider() -> UT1Provider:
    """Return the EOP provider.

    Raises
    ------
    MissingProviderError
        If the provider is not initialised.
    """
    provider = get_eop_provider()
    if not provider:
        msg = "no EOP provider is available. Try calling `epehemerista.init`"
        raise MissingProviderError(msg)
    return provider


class MissingEphemerisError(Exception):
    """Ephemeris was requested but was not initialised via `init`."""

    pass


def get_ephemeris() -> Ephemeris | None:
    """Return the ephemeris or ``None`` if it is uninitialised."""
    return EPHEMERIS


def ephemeris() -> Ephemeris:
    """Return the ephemeris.

    Raises
    ------
    MissingEphemerisError
        If the ephemeris was uninitialised.
    """
    ephemeris = get_ephemeris()
    if not ephemeris:
        msg = "no ephemeris is available. Try calling `epehemerista.init`"
        raise MissingEphemerisError(msg)
    return ephemeris


def _annotate_vec3_field(s):
    # Assumes there's only one vec3 per form
    s["$id"] = "/schemas/vec3"


type Vec3 = Annotated[
    tuple[float, float, float],
    Field(..., json_schema_extra=_annotate_vec3_field),
]
