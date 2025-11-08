"""Tests over general functionalities used in (but not directly related to) DsiUnits."""

from __future__ import annotations

import random
import re

import pytest
import xmlschema

from dsi_unit import DsiParser, DsiUnit
from dsi_unit.dsi_parser import get_closest_str
from dsi_unit.regex_generator import generate_list_regex, generate_regex
from dsi_unit.unit_mapping import (
    INVALID_UNITS_PREFIXES_MAP,
    NO_PREFIX_N_EXPONENT_UNITS,
    NO_PREFIX_UNITS,
    PREFIX_TO_UTF_MAP,
)


@pytest.mark.parametrize(
    ("unit", "exp_match"),
    [(r"\kiilo", ["kilo"]), (r"\mettre", ["metre"]), (r"ttothe", ["tothe"]), (r"molli", ["milli", "mole"])],
)
def test_closest_unit_match(unit: str, exp_match: list[str]):
    """Whether the functionality for the closest unit match works correctly."""
    closest_match = get_closest_str(unit)
    assert exp_match == closest_match


def test_info():
    """Whether the parser prints the correct DSI information."""
    p = DsiParser()
    _, dsi_version, dsi_schema_url, dsi_repository_url = p.info()
    assert dsi_version == DsiParser().dsi_version
    assert dsi_schema_url == DsiParser().dsi_schema_url
    assert dsi_repository_url == DsiParser().dsi_repository_url


@pytest.mark.parametrize(
    ("incorrect_unit", "msg_match"), [(r"\\metre\\\per\second", r"Double backslash found in string")]
)
def test_warning_msg(incorrect_unit: str, msg_match: str):
    """Test for checking the correct messages are being warned."""
    with pytest.warns(RuntimeWarning, match=msg_match):
        _ = DsiUnit(incorrect_unit)


# Global variable containing the generated regex string.
# Tried using a fixture, but it didn't like to be used in @pytest.mark.parametrize
dsi_regex = generate_regex()
dsi_regex_list = generate_list_regex()


# Global variable containing the xml flavoured regex string.
# Tried using a fixture, but it didn't like to be used in @pytest.mark.parametrize
_xml_schema_template = """<?xml version="1.0" encoding="utf-8"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
            elementFormDefault="qualified"
            attributeFormDefault="unqualified">

    <!-- Define a simpleType with the regex -->
    <xs:simpleType name="CodeType">
        <xs:restriction base="xs:string">
        <xs:pattern value="{regex_string}"/>
        </xs:restriction>
    </xs:simpleType>

    <!-- Define the unit element -->
    <xs:element name="unit" type="CodeType"/>

    <!-- Define the outer element, containing inner -->
    <xs:element name="test">
        <xs:complexType>
        <xs:sequence>
            <xs:element ref="unit" maxOccurs="unbounded"/>
        </xs:sequence>
        </xs:complexType>
    </xs:element>

    </xs:schema>
    """
dsi_regex_xml_schema = xmlschema.XMLSchema(_xml_schema_template.format(regex_string=generate_regex(xsd_flavoured=True)))
dsi_regex_list_xml_schema = xmlschema.XMLSchema(
    _xml_schema_template.format(regex_string=generate_list_regex(xsd_flavoured=True))
)


@pytest.mark.parametrize(
    ("dsi_string", "should_match"),
    [
        # (Some) cases that should match:
        (r"\metre", True),
        (r"\milli\metre\tothe{2}", True),
        (r"\kilo\metre\per\second", True),
        (r"\metre\kilogram", True),
        (r"|ounce", True),
        (r"\one", True),
        (r"\metre\tothe{2_3}", True),
        # Should NOT match cases:
        (r"\metre\per\second\per\gram", False),
        (r"\ounce", False),
    ]
    + [  # R011, R012: 'decibel' and 'kilogram' cases.
        (rf"\{pref}\{unit}", False) for pref, unit in INVALID_UNITS_PREFIXES_MAP.items()
    ]
    + [  # R010: No prefixes allowed.
        (rf"\{pref}\{unit}", False)
        for pref in random.choices(list(PREFIX_TO_UTF_MAP), k=5)
        for unit in NO_PREFIX_UNITS | NO_PREFIX_N_EXPONENT_UNITS
    ]
    + [  # R014: No exponents allowed.
        (rf"\{unit}\tothe{{{exp}}}", False) for exp in range(-2, 2) for unit in NO_PREFIX_N_EXPONENT_UNITS
    ],
)
@pytest.mark.parametrize("dsi_fixture", [dsi_regex, dsi_regex_xml_schema])
def test_regex_generator(dsi_fixture: str | xmlschema.XMLSchema, dsi_string: str, should_match: bool):
    """Test generated regex against different valid and invalid dsi unit strings."""
    if isinstance(dsi_fixture, str):
        regex_matched = bool(re.match(dsi_fixture, dsi_string))
    elif isinstance(dsi_fixture, xmlschema.XMLSchema):
        xml_str = f"""<?xml version="1.0" encoding="utf-8"?>
            <test xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="regex-pattern.xsd">
                <unit>
                        {dsi_string}
                </unit>
            </test>"""
        regex_matched = dsi_fixture.is_valid(xml_str)
    else:
        raise TypeError("dsi_fixture needs to be a str or a XMLSChema. ")
    assert regex_matched is should_match


@pytest.mark.parametrize(
    ("dsi_string", "should_match"),
    [
        (r"\milli\metre\tothe{2}", True),
        (r"\milli\metre\tothe{2} \milli\metre\tothe{2}", True),
        (r"\kilo\metre\per\second", True),
        (r"\metre\kilogram", True),
        (r"\metre\per\second\per\gram", False),
        (r"\metre\per\second\per\gram1251\metre\per\second\per\gram", False),
        (r"\metre\per\second\per\gram \metre\per\second\per\gram", False),
        (r"|ounce", True),
        (r"|ounce \metre\kilogram", True),
        (r"\ounce", False),
        (r"\milli\kilogram", False),
        (r"\kilo\gram", False),
        (r"\deci\bel", False),
        (r"\metre  \gram", False),
    ],
)
@pytest.mark.parametrize("dsi_fixture", [dsi_regex_list, dsi_regex_list_xml_schema])
def test_list_regex_generator(dsi_fixture: str | xmlschema.XMLSchema, dsi_string: str, should_match: bool):
    """Test generated list regex against different valid and invalid space-separated lists of dsi unit strings."""
    if isinstance(dsi_fixture, str):
        regex_matched = bool(re.match(dsi_fixture, dsi_string))
    elif isinstance(dsi_fixture, xmlschema.XMLSchema):
        xml_str = f"""<?xml version="1.0" encoding="utf-8"?>
            <test xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:noNamespaceSchemaLocation="regex-pattern.xsd">
                <unit>
                        {dsi_string}
                </unit>
            </test>"""
        regex_matched = dsi_fixture.is_valid(xml_str)
    else:
        raise TypeError(f"dsi_fixture needs to be a str or an XMLSchema, but was a {type(dsi_fixture)}.")
    assert regex_matched is should_match
