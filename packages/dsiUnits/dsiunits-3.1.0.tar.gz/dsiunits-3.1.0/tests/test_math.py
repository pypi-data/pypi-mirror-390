"""Module for testing math operators."""

from __future__ import annotations

import random
import warnings
from fractions import Fraction
from sys import float_info
from typing import Union

import pytest

from dsi_unit import DsiUnit
from dsi_unit.unit_mapping import _BASE_DSI_UNIT_MAP, PREFIX_TO_SCALE_MAP  # noqa: PLC2701

# All digital prefixes end in 'bi'.
DIGITAL_PREFIXES_MAP = {p: s for p, s in PREFIX_TO_SCALE_MAP.items() if p.endswith("bi")}


@pytest.mark.parametrize(
    ("unit_a", "unit_b", "result_unit"),
    [
        (r"\metre", r"\second", r"\metre\second"),
        (r"\metre\per\second", r"\second", r"\metre"),
        (r"\metre\per\second", r"\metre", r"\metre\tothe{2}\second\tothe{-1}"),
        (r"\metre", r"\one", r"\metre"),
        (r"\kilo\metre", r"\milli\metre", r"\metre\tothe{2}"),
    ],
)
def test_unit_multiplication(unit_a: str, unit_b: str, result_unit: str):
    """Testing the __mul__ method at DsiUnit as 'unit_a * unit_b = result_unit'."""
    unit_a = DsiUnit(unit_a)
    unit_b = DsiUnit(unit_b)
    res = DsiUnit(result_unit)
    assert unit_a * unit_b == res


@pytest.mark.parametrize(
    ("unit_a", "unit_b", "result_unit"),
    [
        (r"\metre", r"\second", r"\metre\per\second"),
        (r"\metre", r"\one", r"\metre"),
        (r"\metre\per\second", r"\second", r"\metre\second\tothe{-2}"),
        (r"\metre\per\second", r"\one\per\metre", r"\metre\tothe{2}\second\tothe{-1}"),
    ],
)
def test_unit_division(unit_a: str, unit_b: str, result_unit: str):
    """Testing the __truediv__ method at DsiUnit."""
    unit_a = DsiUnit(unit_a)
    unit_b = DsiUnit(unit_b)
    res = DsiUnit(result_unit)
    assert unit_a / unit_b == res


def test_special_case_joules():
    """Test for unit Joules, which have some special conversions with base and deriver SI units."""
    unit_one = DsiUnit(r"\one")
    unit_joule = DsiUnit(r"\joule")
    base_unit_joule = DsiUnit(r"\kilogram\metre\tothe{2}\per\second\tothe{2}")
    unit_electronvolt = DsiUnit(r"\electronvolt")

    assert (unit_joule / base_unit_joule).is_scalable(unit_one)
    assert (unit_electronvolt / unit_joule).is_scalable(unit_one)

    ev_scale_factor = unit_one.get_scale_factor(unit_electronvolt / unit_joule)
    assert ev_scale_factor == pytest.approx(1.602176634e-19)


@pytest.mark.parametrize(
    ("base_unit", "exponent", "result_unit"),
    [
        (r"\metre", 2, r"\metre\tothe{2}"),
        (r"\metre\per\second", 3, r"\metre\tothe{3}\second\tothe{-3}"),
        (r"\volt", 0, r"\one"),
        (r"\metre", -2, r"\metre\tothe{-2}"),
        (r"\milli\metre", 2, r"\micro\metre\tothe{2}"),
        (r"\volt", 0.5, r"\volt\tothe{1_2}"),
        (r"\volt", Fraction(1, 3), r"\volt\tothe{1_3}"),
        (r"\metre\per\second\tothe{-1}", -2, r"\second\tothe{-2}\per\metre\tothe{2}"),
        (r"\metre\per\volt\second\tothe{-1}", -3, r"\second\tothe{-3}\volt\tothe{3}\per\metre\tothe{3}"),
    ],
)
def test_unit_power(base_unit: str, exponent: Union[int, float, Fraction], result_unit: str):
    """Testing the __pow__ method at DsiUnit."""
    # Note: There is an open ticket regarding the representation of fractions using '_'.
    # https://github.com/TheBIPM/SI_Digital_Framework/issues/2
    # The warnings for that specific case are being suppressed here.
    warnings.filterwarnings("ignore", category=UserWarning)

    base_unit = DsiUnit(base_unit)
    res = DsiUnit(result_unit)
    assert base_unit**exponent == res


@pytest.mark.parametrize(
    ("unit_name", "base_unit_name", "factor", "digital"),
    [
        (r"\milli\volt", r"\volt", 1e3, False),
        (r"\kilo\metre", r"\metre", 1e-3, False),
        (r"\metre\per\second", r"\kilo\metre\per\hour", 1 / 3.6, False),
        (r"\second", r"\minute", 60, False),
        (r"\joule", r"\electronvolt", 1.6e-19, False),
        (r"\joule", r"\kilogram\metre\tothe{2}\second\tothe{-2}", 1.0, False),
        (r"\joule", r"\gram\metre\tothe{2}\second\tothe{-2}", 0.001, False),
        (r"\one", r"\percent", 0.01, False),
        (r"\one", r"\ppm", 1e-6, False),
        (r"\bit", r"\byte", 8, True),
        (r"\mebi\bit", r"\kibi\byte", 1 / 128, True),
    ]
    + [(rf"\{pre}\bit", rf"\{pre}\byte", 8, True) for pre in DIGITAL_PREFIXES_MAP]
    + [
        (rf"\{u}", rf"\{pre}\{u}", 1024**idx, True)
        for idx, pre in enumerate(sorted(DIGITAL_PREFIXES_MAP, key=DIGITAL_PREFIXES_MAP.get), start=1)
        for u in ("bit", "byte")
    ],
)
def test_base_unit_conversion(unit_name: str, base_unit_name: str, factor: float, digital: bool):
    """Base checking for the scale factor."""
    unit = DsiUnit(unit_name)
    base_unit = DsiUnit(base_unit_name)

    if not digital and unit_name != r"\joule":
        assert unit.get_base_unit(base_unit) == unit
    scale_factor = unit.get_scale_factor(base_unit)
    assert abs(scale_factor - factor) < float_info.epsilon


@pytest.mark.parametrize(
    ("unit_name", "convert_unit"),
    [
        # Units that cannot be converted to any base unit:
        (r"\bel", random.choice(list(_BASE_DSI_UNIT_MAP))),
        (r"\decibel", random.choice(list(_BASE_DSI_UNIT_MAP))),
        (r"\neper", random.choice(list(_BASE_DSI_UNIT_MAP))),
        (r"\arcminute", random.choice(list(_BASE_DSI_UNIT_MAP))),
        # Incorrect conversions:
        (r"\percent", r"\metre"),
        (r"\barn", r"\kelvin"),
        (r"\day", r"\kilogram"),
        (r"\one", r"\gram"),
    ],
)
def test_invalid_conversion(unit_name: str, convert_unit: str):
    """Checking invalid conversions among units."""
    unit = DsiUnit(unit_name)
    base_unit = DsiUnit(convert_unit)
    # There is no common base unit:
    assert unit.get_base_unit(base_unit) is None
