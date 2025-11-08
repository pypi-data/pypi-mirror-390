from __future__ import annotations

import contextlib
import math
import warnings
from fractions import Fraction

from dsi_unit.unit_mapping import DSI_UNIT_TO_LATEX_MAP, PREFIX_TO_LATEX_MAP, PREFIX_TO_SCALE_MAP, UNIT_TO_BASE_TREE_MAP


class DsiUnitNode:
    """one node of the D-SI tree, containing prefix, unit, power."""

    # this class variable will store the DsiParserInstance obtained from the singleton constructed
    dsi_parser_instance = None
    # by the initialize_parser() class method by lazy loading, so the instance is created when
    # the first node is created and not before DsiParser is fully defined

    @classmethod
    def initialize_parser(cls):
        # fixme: Not on the top level due to circular import.
        from dsi_unit.dsi_parser import DsiParser  # noqa: PLC0415

        cls.dsi_parser_instance = DsiParser()

    def __init__(
        self,
        prefix: str,
        unit: str,
        exponent: Fraction | float | int | str = Fraction(1),
        valid: bool = True,
        scale_factor: float = 1.0,
    ):  # Adding scale factor with default value 1.0
        if DsiUnitNode.dsi_parser_instance is None:
            DsiUnitNode.initialize_parser()
        self.prefix = prefix
        self.unit = unit
        self.valid = valid
        if isinstance(exponent, (float, int)):
            exponent = Fraction(exponent)
        elif isinstance(exponent, str):
            if exponent == "":
                exponent = Fraction(1)
            else:
                try:
                    exponent = Fraction(exponent).limit_denominator(self.dsi_parser_instance.max_denominator)
                except ValueError:
                    warnings.warn(f"Exponent «{exponent}» is not a number!", RuntimeWarning, stacklevel=2)
        self.exponent = exponent
        self.scale_factor = scale_factor  # Adding scale factor with default value 1.0

    def to_latex(self) -> str:
        """Generates a latex string from a node.

        Returns
        -------
            str: latex representation
        """
        latex_string = PREFIX_TO_LATEX_MAP[self.prefix] if self.prefix else ""
        try:
            latex_string += DSI_UNIT_TO_LATEX_MAP[self.unit]
        except KeyError as err:
            latex_string += r"{\color{red}\mathrm{" + self.unit + r"}}"
            if self.valid:
                raise RuntimeError(
                    "Found invalid unit in valid node, this should not happen! Report this incident at: "
                    "https://gitlab1.ptb.de/digitaldynamicmeasurement/dsiUnits/-/issues/new"
                ) from err
        if isinstance(self.exponent, str):
            # exponent is str this shouldn't happen!
            latex_string += r"^{{\color{red}\mathrm{" + self.exponent + r"}}}"
            if self.valid:
                raise RuntimeError(
                    "Found invalid unit in valid node, this should not happen! Report this incident at: "
                    "https://gitlab1.ptb.de/digitaldynamicmeasurement/dsiUnits/-/issues/new"
                )
        elif self.exponent != 1:
            if self.exponent.denominator != 1:  # exponent is not an integer
                if self.exponent.denominator == 2:  # square root
                    latex_string = r"\sqrt{" + latex_string
                else:  # higher roots need an extra argument
                    latex_string = r"\sqrt[" + str(self.exponent.denominator) + "]{" + latex_string
                    if self.exponent.numerator != 1:  # keep anything in the numerator of the exponent in the exponent
                        latex_string += "^{" + str(self.exponent.numerator) + "}"
                latex_string += r"}"

            else:
                latex_string += r"^{" + str(self.exponent) + r"}"

        if self.unit == "":
            latex_string = r"{\color{red}" + latex_string + r"}"
            if self.valid:
                raise RuntimeError(
                    "Found invalid unit in valid node, this should not happen! Report this incident at: "
                    "https://gitlab1.ptb.de/digitaldynamicmeasurement/dsiUnits/-/issues/new"
                )

        return latex_string

    def to_base_units(self, complete: bool = False) -> list[DsiUnitNode]:
        """
        Converts this node to its base unit representation.
        Adjusts the scale factor during the conversion. Optionally resolves to kg, s, and m units,
        including converting ampere, volt, and mole to their kg, s, and m equivalents when kgs is True.

        Args:
            kgs (bool): If true, also resolves volt to kg, s, and m units.

        Returns
        -------
            List['DsiUnitNode']: List of nodes representing the base units or kg, s, m equivalents.
        """
        # Adjust the scale factor for the prefix
        prefix_scale = PREFIX_TO_SCALE_MAP.get(self.prefix, 1)
        adjusted_scale_factor = self.scale_factor * prefix_scale**self.exponent

        with contextlib.suppress(KeyError):
            # Convert to base units if it's a derived unit
            base_unit_tree = UNIT_TO_BASE_TREE_MAP[self.unit]
            base_units = []
            for idx, (base_unit, exponent, scale_factor) in enumerate(base_unit_tree):
                # Apply the adjusted scale factor only to the first base unit
                final_scale_factor = math.pow(adjusted_scale_factor * scale_factor, self.exponent) if idx == 0 else 1.0
                base_units.append(DsiUnitNode("", base_unit, exponent * self.exponent, scale_factor=final_scale_factor))
            return base_units
        kgs_unit_names = {"volt", "percent", "ppm", "byte", "bit"}
        if complete and self.unit in kgs_unit_names:
            # Additional logic for converting ampere, volt, and mole to kg, s, and m equivalents
            kgs_units_info = UNIT_TO_BASE_TREE_MAP[self.unit]
            kgs_units = []
            for idx, (kgs_unit, exponent, scale_factor) in enumerate(kgs_units_info):
                final_scale_factor = math.pow(adjusted_scale_factor * scale_factor, self.exponent) if idx == 0 else 1.0
                kgs_units.append(DsiUnitNode("", kgs_unit, exponent * self.exponent, scale_factor=final_scale_factor))
            return kgs_units

        # Return the node as is if it's already a base unit, with adjusted scale factor
        return [DsiUnitNode("", self.unit, self.exponent, scale_factor=adjusted_scale_factor)]

    def __hash__(self) -> int:
        """Hashable value of the class."""
        return hash(f"{self.prefix};{self.unit};{self.exponent};{self.scale_factor}")

    def __eq__(self, other: DsiUnitNode) -> bool:
        """Checks if two nodes are identical after sorting their nodes alphabetically."""
        return (
            self.prefix == other.prefix
            and self.unit == other.unit
            and self.exponent == other.exponent
            and self.scale_factor == other.scale_factor
        )

    def __str__(self) -> str:
        """String representation of the DsiUnitNode."""
        result = rf"\{self.prefix}" if self.prefix != "" else ""
        result += rf"\{self.unit}"
        if self.exponent != 1:
            result += r"\tothe{" + str(self.exponent).replace("/", "_") + "}"
        return result

    def is_scaled(self, other: DsiUnitNode) -> float | math.nan:
        """Computes and returns the scale factor.

        Checks the scale factor among the 'self' instance and other DsiUnitNode, returning 'nan' when the factor
        is not scalable.
        """
        # fixme: the name of the function does not correspond to its operations.
        if self.unit == other.unit and self.exponent == other.exponent:
            return (
                PREFIX_TO_SCALE_MAP[other.prefix] ** other.exponent / PREFIX_TO_SCALE_MAP[self.prefix] ** self.exponent
            )
        return math.nan

    def remove_prefix(self) -> DsiUnitNode:
        """Removes the prefix from the node and adjusts the scale factor accordingly."""
        if self.prefix != "":
            self.scale_factor *= PREFIX_TO_SCALE_MAP[self.prefix]
            self.scale_factor **= self.exponent  # TODO check this
            self.prefix = ""
        return self
