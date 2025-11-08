"""Functions for generate regex expressions."""

from typing import Sequence

from dsi_unit.unit_mapping import (
    CONVENTIONAL_PREFIX_TO_LATEX_MAP,
    DIGITAL_PREFIX_TO_LATEX_MAP,
    DIGITAL_PREFIX_UNITS,
    DSI_UNIT_TO_LATEX_MAP,
    INVALID_UNITS_PREFIXES_MAP,
    NO_PREFIX_N_EXPONENT_UNITS,
    NO_PREFIX_UNITS,
)

_DEFAULT_EXP_REGEX = r"(\\tothe\{-?\d+([\._]\d+)?\})?"


def generate_regex(xsd_flavoured: bool = False) -> str:
    """
    Generate a regex that matches D-SI unit strings, as well as other unit strings if they are marked with | as the
    first character. This matches the requirements for the si:unitType in the DCC.

    Parameters
    ----------
    xsd_flavoured : bool, default=False
        If True, generates a regex that can be used in a XSD schema for XML.
        If False, a regex is generated that can be used with most major regex implementations,
        for example python or JavaScript.
    """
    dsi_regex = _get_dsi_regex()
    non_dsi_regex = r"(\|.*)"

    unit_regex = rf"({dsi_regex}|{non_dsi_regex})"
    return rf"\s*{unit_regex}\s*" if xsd_flavoured else rf"^{unit_regex}$"


def generate_list_regex(xsd_flavoured: bool = False) -> str:
    """
    Generate a regex that matches a whitespace-separated list of D-SI units. May be used for a si:unitXMLListType
    in the DCC.

    Parameters
    ----------
    xsd_flavoured : bool, default=False
        If True, generates a regex that can be used in a XSD schema for XML.
        If False, a regex is generated that can be used with most major regex implementations,
        for example python or JavaScript.
    """
    dsi_regex = _get_dsi_regex()
    non_dsi_regex = r"(\|\S*)"  # for the list, whitespace chars are not allowed in units
    unit_regex = f"({dsi_regex}|{non_dsi_regex})"

    unit_list_regex = rf"({unit_regex}(\s{unit_regex})*)"
    return rf"\s*{unit_list_regex}\s*" if xsd_flavoured else rf"^{unit_list_regex}$"


def _get_dsi_regex() -> str:
    """Generate a regex that matches D-SI unit strings."""
    conventional_prefixes_set = set(CONVENTIONAL_PREFIX_TO_LATEX_MAP)
    conventional_prefixes_set.remove("")

    digital_prefixes_set = set(DIGITAL_PREFIX_TO_LATEX_MAP)
    digital_prefixes_set.remove("")

    # These units can't have a prefix (R010, \one is treated separately in R014).
    no_prefix_regex = f"({_get_unit_regex(NO_PREFIX_UNITS)}{_DEFAULT_EXP_REGEX})"

    # Digital prefix units (bit and byte) - can only use digital prefixes
    digital_unit_regex = (
        f"({_get_prefix_regex(DIGITAL_PREFIX_TO_LATEX_MAP)}{_get_unit_regex(DIGITAL_PREFIX_UNITS)}{_DEFAULT_EXP_REGEX})"
    )

    # gram can't have prefix kilo (R011)
    # bel can't have prefix deci (R012)
    invalid_prefix_regex_list = [
        rf"({_get_prefix_regex(conventional_prefixes_set - {prefix})}(\\{unit}){_DEFAULT_EXP_REGEX})"
        for unit, prefix in INVALID_UNITS_PREFIXES_MAP.items()
        if unit not in DIGITAL_PREFIX_UNITS  # Don't apply conventional prefix rules to digital units
    ]

    # \one, \percent and \ppm can't have prefix or exponent (R010 and R014)
    no_exp_regex = _get_unit_regex(NO_PREFIX_N_EXPONENT_UNITS)

    # all other cases (conventional units with conventional prefixes)
    default_prefix_regex = _get_prefix_regex(CONVENTIONAL_PREFIX_TO_LATEX_MAP)
    extended_no_prefix_units = (
        NO_PREFIX_UNITS
        | NO_PREFIX_N_EXPONENT_UNITS
        | INVALID_UNITS_PREFIXES_MAP.keys()
        | DIGITAL_PREFIX_UNITS  # Exclude digital units from conventional prefix handling
    )
    default_unit_regex = _get_unit_regex(
        [unit for unit in DSI_UNIT_TO_LATEX_MAP if unit not in extended_no_prefix_units]
    )
    default_regex = f"({default_prefix_regex}{default_unit_regex}{_DEFAULT_EXP_REGEX})"

    dsi_regex_without_per = (
        f"({'|'.join([no_prefix_regex, digital_unit_regex, no_exp_regex, default_regex, *invalid_prefix_regex_list])})+"
    )

    return rf"({dsi_regex_without_per}(\\per{dsi_regex_without_per})?)"


def _get_prefix_regex(prefixes: dict) -> str:
    """
    Generate a regex that matches any of the prefixes in the dict, or an empty string (so, no prefix). The prefixes
    shall be given without the leading backslash, it will be added for the regex.
    """
    return f"{_get_unit_regex(prefixes)}?"


def _get_unit_regex(units: Sequence[str]) -> str:
    """
    Generate a regex that matches any of the units in the list/set. The units shall be given without the leading
    backslash, it will be added for the regex.
    """
    if isinstance(units, dict):
        units = units.keys()
    joined_units = "|".join(rf"(\\{item})" for item in units if item)  # Skip empty strings
    return f"({joined_units})"
