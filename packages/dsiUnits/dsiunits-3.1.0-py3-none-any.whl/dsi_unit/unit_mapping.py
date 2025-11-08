"""Mappings and sets regarding the DSI units and their representations.

All data is defined following the BIPM brochure:
https://www.bipm.org/en/publications/si-brochure

D-SI PREFIXES
-------------
The information about all prefixes is contained within a single mapping, defined by the following elements:
    {prefix: (utf, latex, scale), ...}

prefix : str
    Name that the prefix takes. This is also the keyword for the internal mapping.
utf : str
    Symbol for the prefix within the utf-8 format.
latex : str
    LaTex code that defines the prefix.
scale : float | int
    Value that corresponds to the prefix. The value is represented as a float number for all
    real prefixes and as an integer for all digital prefixes.

D-SI UNITS
----------
All mappings contained within this class are defined with the following entries:
    {unit: (utf, latex, conversion_tree), ...}

unit : str
    Name of the unit in lowercase. Units defined by multiple words remain as a single word
    without spaces.
    For example, 'degree Celsius' is represented as 'degreecelsius'.
latex : str
    Latex representation of the unit.
conversion_tree : list of tuple[str, int, int]
    Tree containing the conversion from the current unit to its base unit. Each tuple defines:
        - The name of the base unit to convert.
        - The exponent of the base unit.
        - The factor that multiplies the base unit.
    For example, a Coulomb conversion tree is defined as [('second', 1, 1), ('ampere', 1, 1)],
    representing the mathematical equation '1 C = 1 s·A'
    This conversion is only available for those non-base units.
"""

from __future__ import annotations

import itertools
from math import pi

# ------------- DSI CONVENTIONAL PREFIXES MAPPING ------------------ #
_DSI_CONVENTIONAL_PREFIX_MAP: dict[str, tuple[str, str, float]] = {
    "quecto": ("q", r"\mathrm{q}", 1e-30),
    "ronto": ("r", r"\mathrm{r}", 1e-27),
    "yocto": ("y", r"\mathrm{y}", 1e-24),
    "zepto": ("z", r"\mathrm{z}", 1e-21),
    "atto": ("a", r"\mathrm{a}", 1e-18),
    "femto": ("f", r"\mathrm{f}", 1e-15),
    "pico": ("p", r"\mathrm{p}", 1e-12),
    "nano": ("n", r"\mathrm{n}", 1e-9),
    "micro": ("µ", r"\mbox{µ}", 1e-6),
    "milli": ("m", r"\mathrm{m}", 1e-3),
    "centi": ("c", r"\mathrm{c}", 1e-2),
    "deci": ("d", r"\mathrm{d}", 1e-1),
    "": ("", "", 1.0),
    "deca": ("da", r"\mathrm{da}", 1e1),
    "hecto": ("h", r"\mathrm{h}", 1e2),
    "kilo": ("k", r"\mathrm{k}", 1e3),
    "mega": ("M", r"\mathrm{M}", 1e6),
    "giga": ("G", r"\mathrm{G}", 1e9),
    "tera": ("T", r"\mathrm{T}", 1e12),
    "peta": ("P", r"\mathrm{P}", 1e15),
    "exa": ("E", r"\mathrm{E}", 1e18),
    "zetta": ("Z", r"\mathrm{Z}", 1e21),
    "yotta": ("Y", r"\mathrm{Y}", 1e24),
    "ronna": ("R", r"\mathrm{R}", 1e27),
    "quetta": ("Q", r"\mathrm{Q}", 1e30),
}

# ------------- DSI DIGITAL PREFIXES MAPPING ------------------ #
_DSI_DIGITAL_PREFIX_MAP: dict[str, tuple[str, str, int]] = {
    "": ("", "", 1),  # Empty prefix for digital units too
    "kibi": ("ki", r"\mathrm{Ki}", 1024),
    "mebi": ("Mi", r"\mathrm{Mi}", 1048576),
    "gibi": ("Gi", r"\mathrm{Gi}", 1073741824),
    "tebi": ("Ti", r"\mathrm{Ti}", 1099511627776),
    "pebi": ("Pi", r"\mathrm{Pi}", 1125899906842624),
    "exbi": ("Ei", r"\mathrm{Ei}", 1152921504606846976),
    "zebi": ("Zi", r"\mathrm{Zi}", 1180591620717411303424),
    "yobi": ("Yi", r"\mathrm{Yi}", 1208925819614629174706176),
}

# ------------- COMBINED MAPPING FOR BACKWARDS COMPATIBILITY ------------------ #
_DSI_PREFIX_MAP: dict[str, tuple[str, str, float]] = {
    **_DSI_CONVENTIONAL_PREFIX_MAP,
    **{
        prefix: (utf, latex, float(scale))
        for prefix, (utf, latex, scale) in _DSI_DIGITAL_PREFIX_MAP.items()
        if prefix != ""
    },
}

# Create separate mappings for conventional and digital prefixes
CONVENTIONAL_PREFIX_TO_LATEX_MAP = {prefix: latex for prefix, (_, latex, _) in _DSI_CONVENTIONAL_PREFIX_MAP.items()}
DIGITAL_PREFIX_TO_LATEX_MAP = {prefix: latex for prefix, (_, latex, _) in _DSI_DIGITAL_PREFIX_MAP.items()}

# Backwards compatibility - unified mappings
UTF_TO_PREFIX_MAP = {utf: prefix for prefix, (utf, _, _) in _DSI_PREFIX_MAP.items()}
PREFIX_TO_UTF_MAP = {prefix: utf for prefix, (utf, _, _) in _DSI_PREFIX_MAP.items()}
PREFIX_TO_LATEX_MAP = {prefix: latex for prefix, (_, latex, _) in _DSI_PREFIX_MAP.items()}
PREFIX_TO_SCALE_MAP = {prefix: scale for prefix, (_, _, scale) in _DSI_PREFIX_MAP.items()}
SCALE_TO_PREFIX_MAP = {scale: prefix for prefix, (_, _, scale) in _DSI_PREFIX_MAP.items()}

# ------------- DSI UNITS MAPPING ------------------ #
_BASE_DSI_UNIT_MAP: dict[str, tuple[str, str]] = {
    "ampere": ("A", r"\mathrm{A}"),
    "candela": ("cd", r"\mathrm{cd}"),
    "kelvin": ("K", r"\mathrm{K}"),
    "kilogram": ("kg", r"\mathrm{kg}"),
    "metre": ("m", r"\mathrm{m}"),
    "mole": ("mol", r"\mathrm{mol}"),
    "one": ("1", "1"),
    "second": ("s", r"\mathrm{s}"),
}
_DERIVED_DSI_UNIT_MAP: dict[str, tuple[str, str, list[tuple[str, int, float]]]] = {
    "becquerel": ("Bq", r"\mathrm{Bq}", [("second", -1, 1)]),  # 1 Bq = 1/s
    "coulomb": ("C", r"\mathrm{C}", [("second", 1, 1), ("ampere", 1, 1)]),  # 1 C = 1 s·A
    "degreecelsius": ("℃", r"^\circ\mathrm{C}", [("degreecelsius", 1, 1)]),
    "farad": (
        "F",
        r"\mathrm{F}",
        [("kilogram", -1, 1), ("metre", -2, 1), ("second", 4, 1), ("ampere", 2, 1)],  # 1 F = 1 kg⁻¹·m⁻²·s⁴·A²
    ),
    "gram": ("g", r"\mathrm{g}", [("kilogram", 1, 0.001)]),  # 1 gram = 0.001 kilograms
    "gray": ("Gy", r"\mathrm{Gy}", [("metre", 2, 1), ("second", -2, 1)]),  # 1 Gy = 1 m²/s²
    "henry": (
        "H",
        r"\mathrm{H}",
        [("kilogram", 1, 1), ("metre", 2, 1), ("second", -2, 1), ("ampere", -2, 1)],  # 1 H = 1 kg·m²/s²·A²
    ),
    "hertz": ("Hz", r"\mathrm{Hz}", [("second", -1, 1)]),  # 1 Hz = 1/s
    "joule": ("J", r"\mathrm{J}", [("kilogram", 1, 1), ("metre", 2, 1), ("second", -2, 1)]),  # 1 J = 1 kg·m²/s²
    "katal": ("kat", r"\mathrm{kat}", [("mole", 1, 1), ("second", -1, 1)]),  # 1 kat = 1 mol/s
    "lumen": ("lm", r"\mathrm{lm}", [("candela", 1, 1), ("steradian", 1, 1)]),  # 1 lm = 1 cd·sr
    "lux": ("lx", r"\mathrm{lx}", [("candela", 1, 1), ("steradian", 1, 1), ("metre", -2, 1)]),  # 1 lx = 1 cd·sr/m²
    "newton": ("N", r"\mathrm{N}", [("kilogram", 1, 1), ("metre", 1, 1), ("second", -2, 1)]),  # 1 N = 1 kg·m/s²
    "ohm": (
        "Ω",
        r"\Omega",
        [("kilogram", 1, 1), ("metre", 2, 1), ("second", -3, 1), ("ampere", -2, 1)],  # 1 Ω = 1 kg·m²/s³·A⁻²
    ),
    "percent": ("%", r"\%", [("one", 1, 0.01)]),
    "ppm": ("ppm", r"\mathrm{ppm}", [("one", 1, 1e-6)]),
    "pascal": ("Pa", r"\mathrm{Pa}", [("kilogram", 1, 1), ("metre", -1, 1), ("second", -2, 1)]),  # 1 Pa = 1 kg/m·s²
    "radian": ("rad", r"\mathrm{rad}", [("radian", 1, 1)]),
    "siemens": (
        "S",
        r"\mathrm{S}",
        [("kilogram", -1, 1), ("metre", -2, 1), ("second", 3, 1), ("ampere", 2, 1)],  # 1 S = 1 kg⁻¹·m⁻²·s³·A²
    ),
    "sievert": ("Sv", r"\mathrm{Sv}", [("metre", 2, 1), ("second", -2, 1)]),  # 1 Sv = 1 m²/s²
    "steradian": ("sr", r"\mathrm{sr}", [("steradian", 1, 1)]),
    "tesla": ("T", r"\mathrm{T}", [("kilogram", 1, 1), ("second", -2, 1), ("ampere", -1, 1)]),  # 1 T = 1 kg/s²·A
    "volt": (
        "V",
        r"\mathrm{V}",
        [("kilogram", 1, 1), ("metre", 2, 1), ("second", -3, 1), ("ampere", -1, 1)],  # 1 V = 1 kg·m²/s³·A
    ),
    "watt": ("W", r"\mathrm{W}", [("kilogram", 1, 1), ("metre", 2, 1), ("second", -3, 1)]),  # 1 W = 1 kg·m²/s³
    "weber": (
        "Wb",
        r"\mathrm{Wb}",
        [("kilogram", 1, 1), ("metre", 2, 1), ("second", -2, 1), ("ampere", -1, 1)],  # 1 Wb = 1 kg·m²/s²·A
    ),
}
_NON_SI_UNIT_MAP: dict[str, tuple[str, str, list[tuple[str, int, float]]]] = {
    "angstrom": ("Å", r"\mbox{Å}", [("metre", 1, 1e-10)]),  # 1 Å = 1 * 10⁻¹⁰ m
    "astronomicalunit": ("au", r"\mathrm{au}", [("metre", 1, 149597870700)]),  # 1 AU = 149597870700 m
    "atomicmassunit": (
        "u",
        r"\mathrm{u}",
        [("kilogram", 1, 1.66053906660e-27)],  # 1 a.u. mass = 1.66053906660 * 10⁻²⁷ kg
    ),
    "arcminute": ("′", r"'", [("radian", 1, pi / 10800)]),  # 1 arcminute = π/10800 radians
    "arcsecond": ("″", r"''", [("radian", 1, pi / 648000)]),  # 1 arcsecond = π/648000 radians
    "barn": ("b", r"\mathrm{b}", [("metre", 2, 1e-28)]),  # 1 barn = 1 * 10⁻²⁸ m²
    "bel": (
        "B",
        r"\mathrm{B}",
        [("decibel", 1, 1 / 10)],  # Bel is a logarithmic unit for ratios of power, not directly convertible
    ),
    "bit": ("bit", r"\mathrm{bit}", [("bit", 1, 1)]),
    "byte": ("B", r"\mathrm{Byte}", [("bit", 1, 8)]),
    "dalton": ("Da", r"\mathrm{Da}", [("kilogram", 1, 1.66053906660e-27)]),  # 1 Da = 1.66053906660 * 10⁻²⁷ kg
    "day": ("d", r"\mathrm{d}", [("second", 1, 86_400)]),  # 1 day = 86,400 seconds
    "decibel": (
        "dB",
        r"\mathrm{dB}",
        [("decibel", 1, 1)],  # Decibel is a logarithmic unit for ratios of power, not directly convertible
    ),
    "degree": ("°", r"^\circ", [("radian", 1, pi / 180)]),  # 1 degree = π/180 radians
    "electronvolt": ("eV", r"\mathrm{eV}", [("joule", 1, 1.602176634e-19)]),  # 1 eV = 1.602176634 * 10⁻¹⁹ J
    "hectare": ("ha", r"\mathrm{ha}", [("metre", 2, 10000)]),  # 1 ha = 10000 m²
    "hour": ("h", r"\mathrm{h}", [("second", 1, 3600)]),  # 1 hour = 3600 seconds
    "knot": ("kn", r"\mathrm{kn}", [("metre", 1, 1852 / 3600), ("second", -1, 1)]),  # 1 knot = 1852/3600 m/s
    "litre": (
        "l",  # Defined as lowercase 'l' following the brochure convention.
        r"\mathrm{l}",
        [("metre", 3, 0.001)],  # 1 L = 0.001 m³
    ),
    "minute": ("min", r"\mathrm{min}", [("second", 1, 60)]),  # 1 minute = 60 seconds
    "nauticalmile": ("NM", r"\mathrm{NM}", [("metre", 1, 1852)]),  # 1 nautical mile = 1852 m
    "neper": (
        "Np",
        r"\mathrm{Np}",
        [("neper", 1, 1)],  # Neper is a logarithmic unit for ratios of measurements, not directly convertible
    ),
    "tonne": ("t", r"\mathrm{t}", [("kilogram", 1, 1000)]),  # 1 t = 1000 kg
}
_DISCOURAGED_UNIT_MAP: dict[str, tuple[str, str, list[tuple[str, int, float]]]] = {
    "atomicunittime": (  # https://physics.nist.gov/cgi-bin/cuu/Value?aut
        "a.u. time",
        r"\frac{\hbar}{m}_e \cdot c^2}",
        [("second", 1, 2.4188843265864e-17)],  # 1 a.u. time = 2.4188843265864e-17 s
    ),
    "bar": ("bar", r"\mathrm{bar}", [("pascal", 1, 100000)]),  # 1 bar = 100000 Pa
    "bohr": (  # https://physics.nist.gov/cgi-bin/cuu/CCValue?bohrrada0
        "a₀",
        "a_0",
        [("metre", 1, 5.29177210903e-11)],  # 1 Bohr radius = 5.29177210903 * 10⁻¹¹ m
    ),
    "clight": (  # https://physics.nist.gov/cgi-bin/cuu/Value?c
        "c",
        r"\mathrm{c}",
        [("metre", 1, 299792458), ("second", -1, 1)],  # 1 c = 299792458 m/s
    ),
    "electronmass": (  # https://physics.nist.gov/cgi-bin/cuu/Value?me
        "mₑ",
        "m_e",
        [("kilogram", 1, 9.1093837139e-31)],  # 1 m_e = 9.10938356 * 10⁻³¹ kg
    ),
    "elementarycharge": (  # https://physics.nist.gov/cgi-bin/cuu/Value?e
        "e",
        "e",
        [("coulomb", 1, 1.602176634e-19)],  # 1 e = 1.602176634 * 10⁻¹⁹ C
    ),
    "hartree": (  # https://physics.nist.gov/cgi-bin/cuu/Value?hrj
        "Eₕ",
        r"E_\mathrm{h}",
        [("joule", 1, 4.3597447222060e-18)],  # 1 Hartree = 4.3597447222071 * 10⁻¹⁸ J
    ),
    "mmHg": ("mmHg", r"\mathrm{mmHg}", [("pascal", 1, 133.322387415)]),  # 1 mmHg = 133.322387415 Pa
    "naturalunittime": (  # https://physics.nist.gov/cgi-bin/cuu/Value?nut
        "n.u. time",
        r"\frac{\hbar}{m}_e \cdot c^2}",
        [
            ("second", 1, 1.28808866644e-21)
        ],  # 1 natural unit of time = 1.28808866644 * 10⁻²¹ s https://physics.nist.gov/cgi-bin/cuu/Value?nut
    ),
    "planckbar": (  # https://physics.nist.gov/cgi-bin/cuu/Value?Ahbar|search_for=atomic+unit+of+action
        "ħ",
        r"{\hbar}",
        [("joule", 1, 1.054571817e-34), ("second", 1, 1)],  # 1 ħ 1.054 571 68 * 10⁻³⁴ J·s
    ),
}

DSI_UNIT_TO_UTF_MAP = {
    unit: utf
    for unit, (utf, _, _) in itertools.chain(
        _DERIVED_DSI_UNIT_MAP.items(), _NON_SI_UNIT_MAP.items(), _DISCOURAGED_UNIT_MAP.items()
    )
} | {unit: utf for unit, (utf, _) in _BASE_DSI_UNIT_MAP.items()}
UTF_TO_UNIT_MAP = {utf: unit for unit, utf in DSI_UNIT_TO_UTF_MAP.items()}
UTF_TO_UNIT_MAP.update(B="byte")  # Both 'Byte' and 'bel' have the same utf symbol 'B'.
DSI_UNIT_TO_LATEX_MAP = {
    unit: latex
    for unit, (_, latex, _) in itertools.chain(
        _DERIVED_DSI_UNIT_MAP.items(), _NON_SI_UNIT_MAP.items(), _DISCOURAGED_UNIT_MAP.items()
    )
} | {unit: latex for unit, (_, latex) in _BASE_DSI_UNIT_MAP.items()}
UNIT_TO_BASE_TREE_MAP = {
    unit: tree
    for unit, (_, _, tree) in itertools.chain(
        _DERIVED_DSI_UNIT_MAP.items(), _NON_SI_UNIT_MAP.items(), _DISCOURAGED_UNIT_MAP.items()
    )
}

# ------------- DSI SPECIAL CASES ------------------ #
# R010 - Units without prefixes:
NO_PREFIX_UNITS = {"day", "decibel", "degreecelsius", "hectare", "hour", "kilogram", "minute", "mmHg"}
# R010, R014 - Units without prefixes and without exponents:
NO_PREFIX_N_EXPONENT_UNITS = {"one", "ppm", "percent"}
# R011, R012 - Units that don't allow some prefixes:
INVALID_UNITS_PREFIXES_MAP = {"gram": "kilo", "bel": "deci"}
# Units that can use digital prefixes (only bit and byte):
DIGITAL_PREFIX_UNITS = {"bit", "byte"}
