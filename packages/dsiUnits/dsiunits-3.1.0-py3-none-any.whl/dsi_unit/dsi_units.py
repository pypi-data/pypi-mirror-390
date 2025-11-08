from __future__ import annotations

import copy
import math
import numbers
import warnings
from fractions import Fraction
from typing import Optional

from dsi_unit.dsi_parser import DsiParser
from dsi_unit.dsi_unit_node import DsiUnitNode
from dsi_unit.unit_mapping import (
    DSI_UNIT_TO_UTF_MAP,
    PREFIX_TO_SCALE_MAP,
    PREFIX_TO_UTF_MAP,
    SCALE_TO_PREFIX_MAP,
    UTF_TO_PREFIX_MAP,
    UTF_TO_UNIT_MAP,
)

DsiParserInstance = DsiParser()


class DsiUnit:
    def __new__(cls, dsi_string: Optional[str | DsiUnit] = None) -> DsiUnit:
        """If the argument is already a DsiUnit instance, return it directly."""
        if isinstance(dsi_string, cls):
            return dsi_string
        return super().__new__(cls)

    def __init__(self, dsi_string: str | DsiUnit):
        """Constructor."""
        # Prevent reinitialization if this instance was already created.
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True
        self._hash_value = None
        try:
            self.dsi_string, self.tree, self.warnings, self.non_dsi_unit = DsiParserInstance.parse(dsi_string)
            self.valid = len(self.warnings) == 0
            self.scale_factor = 1.0
        except Exception as e:  # noqa: BLE001
            warnings.warn(str(e), stacklevel=2)
            self.dsi_string = dsi_string
            self.tree = []
            self.warnings = [str(e)]
            self.non_dsi_unit = False
            self.valid = False

    @classmethod
    def from_dsi_tree(
        cls,
        dsi_string: str,
        dsi_tree: Optional[list[str]] = None,
        warning_messages: Optional[list[str]] = None,
        non_dsi_unit: bool = False,
        scale_factor: float = 1.0,
    ) -> DsiUnit:
        if warning_messages is None:
            warning_messages = []
        if dsi_tree is None:
            dsi_tree = []
        if non_dsi_unit:
            dsi_tree = [dsi_string]
        elif dsi_string == "" and len(dsi_tree) > 0:
            dsi_string = DsiParserInstance.dsi_str_from_nodes(dsi_tree)
        instance = cls.__new__(cls)
        instance.dsi_string = dsi_string
        instance.tree = dsi_tree
        instance.warnings = warning_messages
        instance.non_dsi_unit = non_dsi_unit
        instance.valid = len(warning_messages) == 0
        instance.scale_factor = scale_factor
        instance._initialized = True
        instance._hash_value = None
        return instance

    def to_latex(self, wrapper: str = "$$", prefix: str = "", suffix: str = "") -> str:
        """Converts D-SI unit string to LaTeX.

        Parameters
        ----------
        wrapper: str, optional
            String to be added both in the beginning and the end of the LaTeX string.
            As default, a latex string is wrapped among '$$' as $${{LATEX}}$$.
        prefix: str, optional
            String to be added at the beginning of the LaTeX string, after the wrapper. No prefix is added as default.
        suffix: str, optional
            String to be added at the end of the LaTeX string, before the wrapper. No suffix is added as default.

        Returns
        -------
        The corresponding LaTeX code
        """
        if len(self.tree) == 0:
            if len(prefix) + len(suffix) > 0:
                return wrapper + prefix + suffix + wrapper
            return ""
        if self.non_dsi_unit:
            latex_string = rf"\textpipe\mathrm{{{self.dsi_string.removeprefix('|')}}}"
            return wrapper + prefix + latex_string + suffix + wrapper
        if len(self.tree) == 1:  # no fractions
            latex_string = "".join(node.to_latex() for node in self.tree[0])
        elif len(self.tree) == 2:  # one fraction
            latex_string = r"\frac"
            for frac in self.tree:
                latex_string += f"{{{''.join(node.to_latex() for node in frac)}}}"
        else:  # more than one fraction
            latex_string = r"".join(node.to_latex() for node in self.tree[0])
            for frac in self.tree[1:]:
                latex_string += r"{\color{red}/}" + "".join(node.to_latex() for node in frac)
        if self.scale_factor != 1.0:
            latex_string = str(self.scale_factor) + r"\cdot" + latex_string
        return wrapper + prefix + latex_string + suffix + wrapper

    def to_utf8(self) -> str:
        """Converts D-SI unit string to a compact UTF-8 format."""

        def exponent_to_utf8(exp: str | int | float) -> str:
            """Converts numerical exponents to UTF-8 subscript."""
            # Mapping for common exponents to UTF-8
            superscripts = {
                "1": "¹",
                "2": "²",
                "3": "³",
                "4": "⁴",
                "5": "⁵",
                "6": "⁶",
                "7": "⁷",
                "8": "⁸",
                "9": "⁹",
                "0": "⁰",
                "-": "⁻",
                ".": "˙",
                "/": "ᐟ",  # Glyph: ᐟ Unicode name: CANADIAN SYLLABICS FINAL P Code point: U+141F
                "+": "⁺",
            }
            # Convert fractional exponents to a more readable format if needed
            return "".join(superscripts.get(char, char) for char in str(exp))

        if self.non_dsi_unit:
            return f"|{self.dsi_string}" if not self.dsi_string.startswith("|") else self.dsi_string
        utf8_array = []
        for unit_fraction in self.tree:
            fraction_utf8_array = []
            for node in unit_fraction:
                # Fetch UTF-8 unit representation
                unit_str = DSI_UNIT_TO_UTF_MAP.get(node.unit, f"⚠{node.unit}⚠")

                # Handle prefix (if any) and unit
                prefix_str = PREFIX_TO_UTF_MAP.get(node.prefix, f"⚠{node.prefix}⚠") if node.prefix else ""
                utf8_str = f"{prefix_str}{unit_str}"  # Direct concatenation for compactness

                # Handle exponent, converting to UTF-8 subscript, if not 1
                if node.exponent and node.exponent != 1:
                    utf8_str += exponent_to_utf8(node.exponent)

                fraction_utf8_array.append(utf8_str)

            # Join units within the same fraction with a dot for compactness
            utf8_array.append("".join(fraction_utf8_array))
        scale_factor_str = str(self.scale_factor) + "*" if self.scale_factor != 1.0 else ""
        # Handle fractions, join numerator and denominator with a slash for division
        return scale_factor_str + " / ".join(utf8_array).replace(" ", "")

    def to_sirp(self, pid: bool = False) -> str:
        """
        Converts this D-SI unit to BIPM SI Reference Point (SI RP) endpoint syntax
        or full PID syntax if `pid=True`.

        Args:
            pid (bool): If True, generate full PID URL instead of compact RP string.

        Returns
        -------
            str: Compact SI RP string or full PID URL.
        """
        unit_copy = copy.deepcopy(self)
        unit_copy._remove_per()

        if unit_copy.scale_factor != 1.0:
            try:
                prefix_name = SCALE_TO_PREFIX_MAP[unit_copy.scale_factor]
            except KeyError as err:
                raise NotImplementedError(f"Unsupported scale factor for SI RP: {unit_copy.scale_factor}") from err
            if len(unit_copy.tree) and len(unit_copy.tree[0]):
                unit_copy.tree[0][0].prefix = prefix_name

        parts = []
        for node in unit_copy.tree[0]:
            if not float(node.exponent).is_integer():
                warnings.warn(
                    "Using suggested integer fraction representation with '_' as seperator from Issue: "
                    "https://github.com/TheBIPM/SI_Digital_Framework/issues/2",
                    stacklevel=2,
                )
                exp = f"{node.exponent.numerator}_{node.exponent.denominator}"
            else:
                exp = int(node.exponent)

            if pid:
                # Full PID format
                prefix = UTF_TO_PREFIX_MAP[PREFIX_TO_UTF_MAP.get(node.prefix, "")]
                unit = UTF_TO_UNIT_MAP.get(DSI_UNIT_TO_UTF_MAP.get(node.unit, node.unit), node.unit)
                if unit == "degreecelsius":
                    unit = "degreeCelsius"
            else:
                # Short RP format
                prefix = PREFIX_TO_UTF_MAP[node.prefix]
                unit = DSI_UNIT_TO_UTF_MAP.get(node.unit, "")
            token = prefix + unit

            if exp != 1:
                token += str(exp)
            parts.append(token)

        simp_repr = ".".join(parts)
        if self._hash_value is None:
            self._hash_value = hash(simp_repr)
        if pid:
            simp_repr = "https://si-digital-framework.org/SI/units/" + simp_repr
        return simp_repr

    def to_base_unit_tree(self, complete: bool = False) -> DsiUnit:
        """Converts the entire D-SI tree to its base unit representation."""
        base_unit_tree = []
        for unit_fraction in self.tree:
            base_fraction = []
            for node in unit_fraction:
                base_fraction.extend(node.to_base_units())
            base_unit_tree.append(base_fraction)
        unconsolidated_tree = DsiUnit.from_dsi_tree(
            dsi_string=self.dsi_string, dsi_tree=base_unit_tree, warning_messages=self.warnings
        )
        reduced = unconsolidated_tree.reduce_fraction()
        # if kgms True we do a second round but resolve volt ampere mole this round
        if complete:
            base_unit_tree = []
            for unit_fraction in self.tree:
                base_fraction = []
                for node in unit_fraction:
                    base_fraction.extend(node.to_base_units(complete=complete))
                base_unit_tree.append(base_fraction)
            unconsolidated_tree = DsiUnit.from_dsi_tree(
                dsi_string=self.dsi_string, dsi_tree=base_unit_tree, warning_messages=self.warnings
            )
            reduced = unconsolidated_tree.reduce_fraction()
        return reduced

    def reduce_fraction(self) -> DsiUnit:
        """
        Creates a new _dsiTree instance with reduced fractions.
        - Consolidates nodes with the same base unit by multiplying scales and summing exponents.
        - Sorts the nodes alphabetically by unit.
        - The first node carries the overall scale factor.
        """
        if len(self.tree) > 2:
            raise RuntimeError("D-SI tree with more than two fractions cannot be reduced.")

        consolidated_nodes = []

        # Handling single and two-node cases
        if len(self.tree) == 1:
            consolidated_nodes = self.tree[0]
        elif len(self.tree) == 2:
            # Copy nodes from the first fraction
            consolidated_nodes = list(self.tree[0])

            # Copy nodes from the second fraction, adjusting the exponents
            for node in self.tree[1]:
                # Inverting the exponent for nodes in the denominator
                inverted_exponent = -1 * node.exponent
                fractional_scale_factor = 1 / node.scale_factor**node.exponent
                consolidated_nodes.append(
                    DsiUnitNode(node.prefix, node.unit, inverted_exponent, scale_factor=fractional_scale_factor)
                )

        # Consolidating nodes with the same unit
        i = 0
        while i < len(consolidated_nodes):
            j = i + 1
            while j < len(consolidated_nodes):
                if consolidated_nodes[i].unit == consolidated_nodes[j].unit:
                    # Consolidate nodes
                    # consolidated_nodes[i].scale_factor * consolidated_nodes[j].scale_factor
                    prefix_scale_i = PREFIX_TO_SCALE_MAP[consolidated_nodes[i].prefix]
                    prefix_scale_j = PREFIX_TO_SCALE_MAP[consolidated_nodes[j].prefix]
                    combined_prefix_scale = prefix_scale_i * prefix_scale_j
                    # we won't allow prefixes in consolidated nodes since we don't want to have prefixes in
                    # the base units
                    consolidated_nodes[i].prefix = ""
                    consolidated_nodes[i].scale_factor *= consolidated_nodes[j].scale_factor * combined_prefix_scale
                    if combined_prefix_scale != 1:
                        raise RuntimeError("Prefixes in base units are not allowed")
                    exponent = consolidated_nodes[i].exponent + consolidated_nodes[j].exponent
                    consolidated_nodes[i].exponent = exponent
                    del consolidated_nodes[j]
                else:
                    j += 1
            i += 1

        # Calculate overall scale factor and apply it to the first node
        overall_scale_factor = 1.0
        for node in consolidated_nodes:
            overall_scale_factor *= node.scale_factor
        #    node.scale_factor = 1.0  # Reset scale factor for individual nodes
        # Sort nodes alphabetically by unit
        consolidated_nodes.sort(key=lambda x: x.unit)
        nodes_wo_power_zero = []
        for node in consolidated_nodes:
            if node.exponent != 0:
                nodes_wo_power_zero.append(node)
        # ok all nodes have been power of zero so we deleted them and end up with one or bytes or bits as
        # unit and 1.0 as exponent
        if len(nodes_wo_power_zero) == 0:
            had_bytes = any(node.unit == "byte" for fraction in self.tree for node in fraction)
            had_bits = any(node.unit == "bit" for fraction in self.tree for node in fraction)
            if had_bytes and had_bits:
                raise RuntimeError(
                    "Can't have bytes and bits in the same unit this should have been consolidated "
                    "already in the parser."
                )
            if had_bytes:
                unit = "byte"
            elif had_bits:
                unit = "bit"
            else:
                unit = "one"
            nodes_wo_power_zero.append(DsiUnitNode("", unit, 1.0, scale_factor=overall_scale_factor))
        consolidated_nodes = nodes_wo_power_zero
        # Check for ones and delete them if they are not the only node ad set there exponent to 1.0 since 1^x = 1
        if len(consolidated_nodes) > 1:
            consolidated_nodes = [node for node in consolidated_nodes if node.unit != "one"]
        elif consolidated_nodes[0].unit == "one":
            consolidated_nodes[0].exponent = 1.0
        # Create and return a new instance of _dsiTree with consolidated nodes
        return DsiUnit.from_dsi_tree(
            dsi_string=self.dsi_string,
            dsi_tree=[consolidated_nodes],
            warning_messages=self.warnings,
            non_dsi_unit=False,
            scale_factor=overall_scale_factor,
        )

    def _remove_per(self):
        r"""Moving all units from the denominator into the numerator.

        Any unit that contains a division (e.g.: 'm/s') defines the division with the keyword '\per'.
        This method transforms the unit to express it without the '\per' operator.

        Examples
        --------
        Initial unit:
            String = r'\metre\per\second'
            Symbol = 'm/s'
            Tree = ([\metre], [\second])
        Transformed unit:
            String = r'\metre\second\tothe{-1}'
            Symbol = 'ms^-1'
            Tree = ([\metre, \second\tothe{-1}])

        Initial unit:
            String = r'\pico\coulomb\per\metre\second\tothe{-2}'
            Symbol = 'pC/ms⁻²'
            Tree = ([\pico\coulomb], [\metre, \second\tothe{-2}])
        Transformed unit:
            String = r'\pico\coulomb\metre\tothe{-1}\second\tothe{2}'
            Symbol = 'pCm⁻¹s²'
            Tree = ([\pico\coulomb, \metre\tothe{-1}, \second\tothe{2}])
        """
        if len(self.tree) == 2:
            for node in self.tree[1]:
                node.exponent *= -1
                self.tree[0].append(node)
            self.tree.pop(1)

    def neg_exponents_to_per(self) -> DsiUnit:
        """Converts negative exponents to the denominator of the fraction."""
        for node in self.tree[0]:  # numerator
            if node.exponent < 0:
                node.exponent = -node.exponent
                node.scale_factor = 1 / node.scale_factor
                try:
                    self.tree[1].append(DsiUnitNode("", node.unit, node.exponent, scale_factor=node.scale_factor))
                except IndexError:  # if we have only the numerator list we need to add the denominator list
                    self.tree.append([DsiUnitNode("", node.unit, node.exponent, scale_factor=node.scale_factor)])
                self.tree[0].remove(node)
        if len(self.tree) == 2:  # we have a numerator and a denominator so we must treat the denominator as well
            for node in self.tree[1]:  # numerator
                if node.exponent < 0:
                    node.exponent = -node.exponent
                    node.scale_factor = 1 / node.scale_factor
                    self.tree[0].append(DsiUnitNode("", node.unit, node.exponent, scale_factor=node.scale_factor))
                    self.tree[1].remove(DsiUnitNode)
        if len(self.tree[0]) == 0:
            self.tree[0].append(DsiUnitNode("", "one", 1.0))
        return self

    def sort_tree(self):
        """Sorts each fraction's nodes alphabetically by their units."""
        for unit_fraction in self.tree:
            unit_fraction.sort(key=lambda node: node.unit)

    def __eq__(self, other: DsiUnit) -> bool:
        """Checks if two D-SI trees are identical after sorting their nodes alphabetically."""
        if not isinstance(other, DsiUnit):
            return False
        if self.non_dsi_unit or other.non_dsi_unit:
            return self.tree == other.tree
        # Todo: consider sorting
        return hash(self) == hash(other)

    def get_scale_factor(self, other: DsiUnit) -> float:
        """Get the factor with which the units can be converted into each other. x self == 1 other.

        Args:
            other (DsiUnit): Unit to compare against

        Returns
        -------
            float: scale factor. scale factor * self == 1 * other
        """
        scale_factor, _ = self._calculate_scale_factor_and_common_unit(other, complete=True)
        return scale_factor

    def is_scalable(self, other: DsiUnit) -> bool:
        """Returns whether the two units can be converted into each other.

        Args:
            other (DsiUnit): Unit to compare against

        Returns
        -------
            bool: whether the two units can be converted into each other
        """
        return bool(self.get_scale_factor(other))

    def get_base_unit(self, other: DsiUnit) -> Optional[DsiUnit]:
        """Get the common base unit for the two units, if it exists.

        Args:
            other (DsiUnit): Unit to compare against

        Returns
        -------
            DsiUnit: common base unit
        """
        _, common_unit = self._calculate_scale_factor_and_common_unit(other, complete=True)
        if common_unit is None:
            return None
        base_unit = common_unit.reduce_fraction()
        base_unit.tree[0][0].scale_factor = 1.0  # TODO: check if this should be a Fraction
        return base_unit

    def is_scalably_equal_to(
        self, other: DsiUnit, complete: bool = False
    ) -> tuple[float | math.nan, Optional[DsiUnit]]:
        """
        Checks if two D-SI units are scalably equal and returns the scale factor and base unit, without modifying
        the units involved.

        Args:
            other (DsiUnit): The other D-SI unit to compare against.
            complete (bool): A flag to determine whether the units should be resolved completely to base units.

        Returns
        -------
            (float, DsiUnit):
                - A tuple containing the scale factor as a float. If the units are not scalable, returns math.nan.
                - The second element is the base unit of the calling object or None if not scalable.

        Behavior:
            - First, it checks if `other` is of type `DsiUnit`. If not, it returns math.nan and None.
            - It sorts and compares the two trees. If they are identical, it returns a scale factor of 1.0 and the
                calling unit.
            - If they are not identical, it attempts to compute the scale factor by iterating through the tree nodes
                and checking for scaling relationships.
            - If direct comparison fails and complete == True, it converts both trees to their base unit
                representations, sorts them, and attempts to compute a scaling factor in the base units.

        Raises
        ------
            RuntimeError: If there are multiple fractions in the base unit trees during comparison.
        """
        warnings.warn(
            "This function is deprecated. Please use one of the following functions instead: "
            "get_scale_factor, is_scalable, get_base_unit",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._calculate_scale_factor_and_common_unit(other, complete=complete)

    def _calculate_scale_factor_and_common_unit(
        self, other: DsiUnit, complete: bool = False
    ) -> tuple[float | math.nan, Optional[DsiUnit]]:
        if not isinstance(other, DsiUnit):
            return math.nan, None

        sorted_self = copy.deepcopy(self)
        sorted_self.sort_tree()
        sorted_other = copy.deepcopy(other)
        sorted_other.sort_tree()
        # okay now check if is identical
        if sorted_self.tree == sorted_other.tree:
            return 1.0, self
        scale_factor = 1
        for frac_idx, unit_fraction in enumerate(sorted_self.tree):
            try:
                if len(unit_fraction) != len(sorted_other.tree[frac_idx]):
                    scale_factor = math.nan
                    break
                for node_idx, node in enumerate(unit_fraction):
                    scale_factor *= node.is_scaled(sorted_other.tree[frac_idx][node_idx])
            except IndexError:
                # if we get here we have a fraction in one tree that is not in the other in this case we
                # resolve to base units and compare
                scale_factor = math.nan
                break
        if not math.isnan(scale_factor):
            return scale_factor, self
        # Convert both trees to their base unit representations
        # we need to do double conversion since eV-->J-->kgm²s⁻²
        # TODO find more elegant way  for this
        self_base_unit_tree = self.to_base_unit_tree(complete=complete).to_base_unit_tree(complete=complete)
        other_base_unit_tree = other.to_base_unit_tree(complete=complete).to_base_unit_tree(complete=complete)

        # Sort both trees
        self_base_unit_tree.sort_tree()
        other_base_unit_tree.sort_tree()
        # Check if units match
        if len(self_base_unit_tree.tree) != len(other_base_unit_tree.tree):
            return math.nan, None
        # Calculate scale factor
        scale_factor = 1.0
        if len(self_base_unit_tree.tree) != 1 or len(other_base_unit_tree.tree) != 1:
            raise RuntimeError(
                "D-SI tree with more than one fraction cannot be compared. And should not exist here since "
                "we consolidated earlier."
            )
        for self_node, other_node in zip(self_base_unit_tree.tree[0], other_base_unit_tree.tree[0]):
            if self_node.unit != other_node.unit or self_node.exponent != other_node.exponent:
                return math.nan, None
            scale_factor *= other_node.scale_factor / self_node.scale_factor
        # resetting scale_factor to 1.0
        scale_factor = other_base_unit_tree.scale_factor / self_base_unit_tree.scale_factor
        # TODO check resetting the scale factors of the base units is a good idea ... but we calculated the
        #  scale factor and returned it so it should be fine
        self_base_unit_tree.scale_factor = 1.0
        for fraction in self_base_unit_tree.tree:
            for node in fraction:
                node.scale_factor = 1.0
        return scale_factor, self_base_unit_tree

    @property
    def is_adimensional(self) -> bool:
        """Whether if the current DsiUnit is adimensional (the result operation of all the units is 'one').

        Warns
        -----
        UserWarning
            When a unit is adimensional but there is a conversion factor among them that is different to 1.

        Examples
        --------
        '\\one'
            This example is clear, as this one is already the final goal.
        '\volt\\per\volt'
            The result is a straightforward '\\one'.
        '\\joule\\per\\kilogram\\metre\tothe{2}\\second\tothe{-2}'
            While the operation might not look directly adimensional, a 'joule' is defined as 'kg * m ** 2 / (s ** 2)'
            in the base SI units. Thus, by converting all the units to their bases and resolving the equation, the
            result is also '\\one'.
        '\\hour\\per\\second'
            Considering generalized units, this is '\time\\per\time'. Thus, the unit IS adimensional.
            However, one hour is 3600 seconds. This is a factor that should be considered even if the unit is
            adimensional.
        """
        base_unit_tree = self.to_base_unit_tree()
        # Checking if it is adimensional as the final tree should be [[\one]]
        if len(base_unit_tree.tree) > 1:
            return False
        if len(base_unit_tree.tree[0]) > 1:
            return False
        if base_unit_tree.tree[0][0].unit != "one":
            return False
        if base_unit_tree.scale_factor != 1:
            warnings.warn(
                f"The unit {self!s} is adimensional, but it has a scale factor different than 1.", stacklevel=2
            )
        return True

    def __str__(self) -> str:
        """String representation of the class."""
        result = ""
        if self.non_dsi_unit:
            if self.dsi_string[0] != "|":
                return "|" + self.dsi_string
            return self.dsi_string
        if self.scale_factor != 1.0:
            result += str(self.scale_factor) + "*"
        for node in self.tree[0]:
            result += str(node)
        if len(self.tree) == 2:
            result += r"\per"
            for node in self.tree[1]:
                result += str(node)
        return result

    def __hash__(self) -> int:
        """The hash value is defined as the hash from the BIMP representation.

        Once the representation is called for the first time, the hash is then stored. If the hash is called before
        the `to_sirp()` method for the first time, then the logic calls this method to update the
        stored hash value.
        """
        if self._hash_value is None:
            self.to_sirp()
        return self._hash_value

    def __repr__(self) -> str:
        """String representation of the class."""
        content_str = self.to_utf8()
        if not self.valid:
            content_str += "INVALID"
        if self.warnings:
            content_str += f" {len(self.warnings)} WARNINGS"
        # Simple representation: class name and D-SI string
        return f"{content_str}"

    def __pow__(self, other: numbers.Real | DsiUnit) -> DsiUnit:
        """Power operations with '**' as the operator."""
        if not isinstance(other, numbers.Real):
            raise TypeError("Exponent must be a real number")
        if self.non_dsi_unit:
            raise RuntimeError("Can't do math with non-DSI units")
        result_node_list = copy.deepcopy(self.tree)
        for unit_fraction in result_node_list:
            for node in unit_fraction:
                node.remove_prefix()
                exponent = node.exponent * other
                node.exponent = Fraction(exponent).limit_denominator(DsiParserInstance.max_denominator)
                node.scale_factor **= other
        result_tree = DsiUnit.from_dsi_tree(dsi_string="", dsi_tree=result_node_list, warning_messages=self.warnings)
        result_tree = result_tree.reduce_fraction()
        if len(self.tree) == 2:  # check if we had a per representation
            result_tree.neg_exponents_to_per()
        return result_tree

    def __mul__(self, other: DsiUnit) -> DsiUnit:
        """Performing a multiplication operation by the '*' operator."""
        if self.non_dsi_unit or other.non_dsi_unit:
            raise RuntimeError("Can't do math with non-DSI units")
        convert_to_per = len(self.tree) + len(other.tree) > 2
        result_node_list = copy.deepcopy(self.tree)
        for idx, unit_fraction in enumerate(other.tree):
            if idx > 1:
                raise RuntimeError("D-SI tree with more than one fraction cannot be multiplied")
            try:
                result_node_list[idx].extend(copy.deepcopy(unit_fraction))
            except IndexError:
                result_node_list.append(copy.deepcopy(unit_fraction))  # there was no fraction so we add it
        for fraction_components in result_node_list:
            for node in fraction_components:
                node.remove_prefix()
        result_tree = DsiUnit.from_dsi_tree(dsi_string="", dsi_tree=result_node_list, warning_messages=self.warnings)
        result_tree = result_tree.reduce_fraction()
        if convert_to_per:
            result_tree = result_tree.neg_exponents_to_per()
        return result_tree

    def __truediv__(self, other: DsiUnit) -> DsiUnit:
        """Performing division operations by the '/' operator."""
        if self.non_dsi_unit or other.non_dsi_unit:
            raise RuntimeError("Can't do math with non-DSI units")
        if DsiParserInstance.create_per_by_division:
            return (self * (other**-1)).neg_exponents_to_per()
        return self * (other**-1)
