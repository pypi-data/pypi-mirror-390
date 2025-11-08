"""Test cases related to proxy connections."""

from __future__ import annotations

import copy
import os
from typing import Optional

import pytest
import requests

from dsi_unit import DsiUnit

PROXY_CANDIDATES = [
    "http://webproxy.bs.ptb.de:8080",
    "http://proxy:3128",
    "http://proxy:8080",
    "http://fw:8080",
    "http://firewall:8080",
]
CONNECT_TIMEOUT = 20


def _get_safe_response(url: str, **kwargs) -> Optional[requests.Response]:
    """Wrapper for requests.get() that returns None on connection errors."""
    timeout = kwargs.pop("timeout", CONNECT_TIMEOUT)
    try:
        return requests.get(url, timeout=timeout, **kwargs)
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.SSLError):
        return None


def _can_proxy_connect(proxy_url: str) -> bool:
    proxies = {"http": proxy_url, "https": proxy_url}
    resp = _get_safe_response("http://example.com", proxies=proxies)
    if resp is None:
        return False
    return resp.status_code == 200


def _normalize_dsi_tree_to_tuples(unit: DsiUnit) -> list:
    """
    Normalize a DsiUnit instance into a list of (prefix, unit, exponent) tuples.
    The list will be flattened and _removePer will be applied to ensure compatibility.
    """
    unit_copy = copy.deepcopy(unit)
    unit_copy._remove_per()
    result = []
    for node in unit_copy.tree[0]:
        result.append((node.prefix or "", node.unit, int(node.exponent)))
    return result


@pytest.fixture(scope="module", autouse=True)
def configure_proxy_if_needed():
    """Configuring the proxy for the module before the tests run."""
    if "http_proxy" in os.environ or "HTTP_PROXY" in os.environ:
        print("✅ Proxy already configured in environment.")
        return

    for proxy_url in PROXY_CANDIDATES:
        if _can_proxy_connect(proxy_url):
            for var in ["http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY"]:
                os.environ[var] = proxy_url
            print(f"✅ Proxy set from working candidate: {proxy_url}")
            return

    print("⚠️ No working proxy configured or detected.")


@pytest.mark.parametrize(
    "invalid_unit", [r"\molli\meter", r"\kilogram\milli\metre\tothe{2}\nano\sec\tothe{-2}", r"\none", ""]
)
def test_bipm_pid_json_vs_dsi_unit_invalid_instances(invalid_unit: str):
    """Invalid unit expressions (syntactically wrong or non-existent)."""
    with pytest.warns(RuntimeWarning):
        unit = DsiUnit(invalid_unit)
    url = unit.to_sirp(pid=True)
    response = _get_safe_response(url)
    if response is None:
        pytest.skip(f"Skipping {url} due to connection error.")
    assert response.status_code == 400, (
        f"Expected 400 for invalid PID: {unit.dsi_string} → {url} but got {response.status_code}"
    )


@pytest.mark.parametrize(
    "unit_str",
    [
        r"\kilogram\milli\metre\tothe{2}\nano\second\tothe{-2}",
        r"\kilogram\milli\metre\tothe{2}\nano\second\tothe{-2}\astronomicalunit\tothe{-4}\degreecelsius\micro\henry",
        r"\volt\tothe{2}\per\ohm",
        r"\ampere\tothe{2}\ohm",
        r"\joule\per\second",
        r"\pascal\metre\tothe{3}\per\second",
        r"\weber\ampere\per\second",
        r"\degreecelsius",
        r"\nano\second",
        r"\micro\henry",
    ],
)
def test_bipm_pid_json_vs_dsi_unit_instances(unit_str: str):
    """Validate that the BIPM PID JSON response matches the internal DsiUnit representation."""
    unit = DsiUnit(unit_str)
    url = unit.to_sirp(pid=True)
    response = _get_safe_response(url)
    if response is None:
        pytest.skip(f"Skipping {url} due to connection error.")
    assert response.status_code == 200, f"Expected 200 {url}, got {response.status_code}"

    json_data = response.json()
    try:
        bipm_units = json_data["resultsCombinedUnitList"]
    except KeyError as err:
        if len(unit.tree) != 1:
            raise RuntimeError(
                "Expected that we stated with a tree with just one entry sinc we didn't get a combined unit back ..."
            ) from err
        # let's fake an ordinary response for the simple base unit ...
        bipm_units = [{"unitName": json_data["unitId"], "exponent": 1, "prefixName": ""}]

    parsed_bipm = []
    for item in bipm_units:
        prefix = item.get("prefixName", "").replace(" ", "").lower()
        unit_name = item["unitName"].replace(" ", "").lower()
        exponent = int(item["exponent"])
        parsed_bipm.append((prefix, unit_name, exponent))

    local_tree = _normalize_dsi_tree_to_tuples(unit)
    assert parsed_bipm == local_tree, f"\nExpression: {unit.dsi_string}\nExpected: {local_tree}\nGot: {parsed_bipm}"
