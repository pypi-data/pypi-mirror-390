"""Methods for parsing a string into a DsiUnit."""

from __future__ import annotations

import difflib
import re
import warnings
from fractions import Fraction
from typing import Iterable

from dsi_unit._warnings import NonDsiUnitWarning
from dsi_unit.dsi_unit_node import DsiUnitNode
from dsi_unit.unit_mapping import (
    DSI_UNIT_TO_LATEX_MAP,
    DSI_UNIT_TO_UTF_MAP,
    PREFIX_TO_LATEX_MAP,
    UTF_TO_PREFIX_MAP,
    UTF_TO_UNIT_MAP,
)


class DsiParser:
    """Parser to parse D-SI unit string into a tree."""

    _instance = None
    __dsi_version = "2.2.0"
    __dsi_schema_url = "https://www.ptb.de/si/v2.2.0/SI_Format.xsd"
    __dsi_repository_url = "https://gitlab1.ptb.de/d-ptb/d-si/xsd-d-si"

    _defaults = {"create_per_by_division": True, "max_denominator": 10000}

    @property
    def dsi_version(self) -> str:
        """Version corresponding the supported DSI version schema."""
        return self.__dsi_version

    @property
    def dsi_schema_url(self) -> str:
        """URL to the current supported DSI version schema."""
        return self.__dsi_schema_url

    @property
    def dsi_repository_url(self) -> str:
        """URL to the gitlab repo."""
        return self.__dsi_repository_url

    def __new__(cls) -> DsiParser:
        """Setting all instances to call always the same instance."""
        if cls._instance is None:
            cls._instance = super(DsiParser, cls).__new__(cls)
            # Initialize configuration options
            for key, value in cls._defaults.items():
                setattr(cls._instance, key, value)
        return cls._instance

    def parse(self, dsi_string: str) -> tuple[str, list[list[DsiUnitNode]], list, bool]:
        """Parses a D-SI string into a tree structure.

        Parameters
        ----------
        dsi_string: str
            D-SI unit as a raw string.

        Raises
        ------
            RuntimeWarning: Double backslashes in D-SI string
            RuntimeWarning: Empty D-SI string

        Returns
        -------
            dsiTree: dsiTree object containing the D-SI unit
        """
        warning_messages = []
        if dsi_string == "":
            warning_messages.append(msg := "Given D-SI string is empty!")
            warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
            return (
                "NULL",
                [[DsiUnitNode("", "NULL", valid=False)]],
                warning_messages,
                True,  # non_dsi_unit
            )

        # Catch any double (triple...) backslash:s
        while r"\\" in dsi_string:
            warning_messages.append(
                msg := f"Double backslash found in string, treating as one backslash: «{dsi_string}»"
            )
            warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
            dsi_string = dsi_string.replace(r"\\", "\\")

        if not dsi_string.startswith(("\\", "|")):
            # if the string does not start with a backslash or |, it is not a D-SI unit, so we will try if
            # its BIMP-RP syntax
            return self._parse_bipm_rp(dsi_string)

        if dsi_string[0] == "|":
            warnings.warn("Parsing a correctly marked non D-SI unit!", NonDsiUnitWarning, stacklevel=2)
            return dsi_string[1:], [[DsiUnitNode("", dsi_string[1:], valid=False)]], [], True

        if " " in dsi_string:
            warning_messages.append(
                msg := (
                    "Given D-SI string contains spaces! "
                    "If this is a space-separated list, please parse each unit separately. "
                    "Removing spaces and assuming single unit."
                )
            )
            warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
            dsi_string = dsi_string.replace(" ", "")

        tree, fraction_warnings = self._parse_dsi_fraction(dsi_string)
        warning_messages += fraction_warnings
        for i, node in enumerate(tree):
            tree[i], fractionless_warnings = self._parse_fractionless_dsi(node)
            warning_messages += fractionless_warnings
        return dsi_string, tree, warning_messages, False

    @staticmethod
    def _parse_dsi_fraction(dsi_string: str) -> tuple[list[str], list[str]]:
        """Parses D-SI fraction into list of fraction elements.

        Args:
            dsi_string (str): D-SI unit raw string

        Raises
        ------
            RuntimeWarning: String must not contain more than one "per",
                            as defined in the D-SI specs

        Returns
        -------
            list: Strings separated by the "per"
            list: Warning messages of problems encountered while parsing
        """
        warning_messages = []
        # Splitting over 'per' and ignoring 'percent' as a possible split match.
        tree = re.split(r"\\per(?!cent)", dsi_string)
        for subtree in list(tree):
            if len(subtree) == 0:
                warning_messages.append(
                    msg := r"The dsi string contains a \per missing a numerator or denominator! "
                    f"Given string: {dsi_string}"
                )
                warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                tree.remove(subtree)
        if len(tree) > 2:
            warning_messages.append(
                msg := rf"The dsi string contains more than one \per, does not match specs! Given string: {dsi_string}"
            )
            warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
        return tree, warning_messages

    @staticmethod
    def _parse_fractionless_dsi(dsi_string: str) -> tuple[list[DsiUnitNode], list[str]]:
        """Parses D-SI unit string without fractions.

        Args:
            dsi_string (str): D-SI unit raw string, not containing any fractions

        Raises
        ------
            RuntimeWarning: If string does not meet the specs

        Returns
        -------
            list: List of nodes
            list: Warning messages of problems encountered while parsing
        """
        warning_messages = []
        items = dsi_string.split("\\")
        if items[0] == "":  # First item of List should be empty, remove it
            items.pop(0)
        else:
            warning_messages.append(msg := f"String should start with \\, string given was «{dsi_string}»")
            warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
        nodes = []

        prefix, unit = "", ""
        exponent_str, exponent = "", ""
        valid = True
        item = items.pop(0)
        while True:
            if item in PREFIX_TO_LATEX_MAP:
                prefix = item
                try:
                    item = items.pop(0)
                except IndexError:
                    item = ""
            if item in DSI_UNIT_TO_LATEX_MAP:
                unit = item
                try:
                    item = items.pop(0)
                except IndexError:
                    item = ""
            # if re.match(r"tothe\{[^{}]*}", item):  # used to be elif
            if re.match(r"tothe.*", item):
                if not re.match(r"tothe\{[^{}]*}", item):
                    exponent_str = item.replace("tothe", "")
                    warning_messages.append(
                        msg := (
                            f"The fragment {item} looks like an exponent, but does not contain {{ }}! "
                            f"Treating {exponent_str} as the exponent!"
                        )
                    )
                    valid = False
                    warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                else:
                    split_str = item.split("{")[1].split("}")
                    exponent_str = item.split("{")[1].split("}")[0]
                    if len(split_str[1]) > 0:
                        warning_messages.append(
                            msg := (
                                f"The fragment {item} contained something after the }} that could not be parsed! "
                                f"You most likely forgot a \\, inserting as new fragment…"
                            )
                        )
                        warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                        valid = False
                        items = [split_str[1]] + items

                try:
                    exponent_str_fraction = exponent_str.replace("_", "/")
                    exponent = Fraction(exponent_str_fraction).limit_denominator()
                except ValueError:
                    warning_messages.append(msg := f"The exponent «{exponent_str}» is not a number!")
                    warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                    valid = False
                    exponent = exponent_str
                try:
                    item = items.pop(0)
                except IndexError:
                    item = ""
            if (prefix, unit, exponent) == ("", "", ""):
                unit = item
                try:
                    item = items.pop(0)
                except IndexError:
                    item = ""
                closest_matches = get_closest_str(unit)
                if len(closest_matches) > 0:
                    closest_matches_str = "\\" + ", \\".join(closest_matches)
                    warning_messages.append(
                        msg := f"The identifier «{unit}» does not match any D-SI units! Did you mean one "
                        f"of these «{closest_matches_str}»?"
                    )
                    warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                    valid = False
                else:
                    warning_messages.append(msg := rf"The identifier «{unit}» does not match any D-SI units!")
                    warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                    valid = False
            elif unit == "":
                item_str = ""
                if prefix != "":
                    item_str = item_str + "\\" + prefix
                if exponent_str != "":
                    item_str = item_str + r"\tothe{" + str(exponent_str) + r"}"
                warning_messages.append(msg := f"This D-SI unit seems to be missing the base unit! «{item_str}»")
                warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                valid = False
            nodes.append(DsiUnitNode(prefix, unit, exponent, valid=valid))
            if (len(items) == 0) and (item == ""):
                break
            prefix, unit, exponent = "", "", ""
            valid = True
        return nodes, warning_messages

    @staticmethod
    def dsi_str_from_nodes(node_list: Iterable[str]) -> str:
        """Converts a list of nodes to a D-SI string."""
        dsi_str = ""
        for idx, unit_fraction in enumerate(node_list):
            if idx > 0:
                dsi_str += r"\per"
            for node in unit_fraction:
                dsi_str += str(node)
        return dsi_str

    def info(self) -> tuple[str, str, str, str]:
        """General information about the D-SI parser."""
        print(
            info_str := (
                f"D-SI Parser Version: {self} using D-SI Schema Version: {self.__dsi_version}  from: "
                f"{self.__dsi_repository_url} using D-SI Schema: {self.__dsi_schema_url}."
            )
        )
        return info_str, self.__dsi_version, self.__dsi_schema_url, self.__dsi_repository_url

    def reset_to_defaults(self):
        """Resets the parser to its default configuration."""
        for key, value in self._defaults.items():
            setattr(self, key, value)

    @staticmethod
    def _parse_bipm_rp(rp_string: str) -> tuple[str, list[list[DsiUnitNode]], list[str], bool]:
        """
        Parses BIPM-RP or PID-style strings like 'kg.mm2.ns-2.℃' into D-SI trees.
        Accepts exponents in the form '2' or as fractions like '1_2' (1/2) or '2_3' (2/3).

        Returns
        -------
            (str, list[list[DsiUnitNode]], list of warnings, bool isNonDsi)
        """
        warning_messages = []
        node_list = []

        components = rp_string.strip().split(".")
        for comp in components:
            # Updated regex: group 1 matches the letter part, group 2 optionally
            # matches an exponent that can include an underscore (e.g., 1_2)
            match = re.fullmatch(r"([a-zA-ZµΩ℃°]+)([-+]?[0-9]+(?:_[0-9]+)?)?", comp)
            if not match:
                warning_messages.append(msg := f"Invalid BIPM-RP component: «{comp}»")
                warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                return rp_string, [[DsiUnitNode("", rp_string, valid=False)]], warning_messages, True

            prefix_and_unit = match.group(1)
            exponent_str = match.group(2)
            # Parse the exponent: check for the underscore indicating a fraction format
            if exponent_str:
                if "_" in exponent_str:
                    num, den = exponent_str.split("_")
                    try:
                        exponent = Fraction(int(num), int(den))
                    except ValueError:
                        warning_messages.append(msg := f"Invalid fraction format in exponent: «{exponent_str}»")
                        warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                        return rp_string, [[DsiUnitNode("", rp_string, valid=False)]], warning_messages, True
                else:
                    exponent = Fraction(exponent_str)
            else:
                exponent = Fraction(1)

            if prefix_and_unit in UTF_TO_UNIT_MAP or prefix_and_unit in DSI_UNIT_TO_UTF_MAP:
                # No prefix within the parsed unit.
                # The unit was parsed with its symbol as 'kg' or with its name as 'kilogram'.
                matched_unit = UTF_TO_UNIT_MAP.get(prefix_and_unit, prefix_and_unit)
                matched_prefix = ""
            else:
                # Iterating over all prefixes (starting from the longest ones)
                for prefix in sorted(UTF_TO_PREFIX_MAP.keys(), key=len, reverse=True):
                    if (possible_unit := prefix_and_unit.removeprefix(prefix)) in UTF_TO_UNIT_MAP:
                        matched_unit = UTF_TO_UNIT_MAP[possible_unit]
                        matched_prefix = UTF_TO_PREFIX_MAP[prefix]
                        break
                else:
                    warning_messages.append(msg := f"Unknown unit in BIPM-RP string: «{prefix_and_unit}»")
                    warnings.warn(msg, category=RuntimeWarning, stacklevel=2)
                    return rp_string, [[DsiUnitNode("", rp_string, valid=False)]], warning_messages, True

            node_list.append(DsiUnitNode(matched_prefix, matched_unit, exponent))

        return rp_string, [node_list], warning_messages, False


def get_closest_str(unknown_str: str) -> list[str]:
    """Returns the closest string and type of the given string.

    Args:
        unknownStr (str): string to be compared

    Returns
    -------
        str: closest string
        str: type of closest string
    """
    possible_dsi_keys = PREFIX_TO_LATEX_MAP.keys() | DSI_UNIT_TO_LATEX_MAP.keys() | {"tothe", "per"}
    return difflib.get_close_matches(unknown_str, possible_dsi_keys, n=3, cutoff=0.66)
