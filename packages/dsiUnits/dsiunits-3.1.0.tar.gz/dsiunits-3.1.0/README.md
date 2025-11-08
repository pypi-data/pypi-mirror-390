# D-SI Units

A Python library for parsing, validating, and performing mathematical operations on SI units using the [D-SI (Digital SI)](https://gitlab1.ptb.de/d-ptb/d-si/xsd-d-si) and [BIPM-RP (SI Reference Point)](https://si-digital-framework.org/SI/unitExpr?lang=en) syntax.

The library allows:

- **Unit Parsing & Validation**: Parse units from D-SI and BIPM-RP notation strings
- **Mathematical Operations**: Perform multiplication, division, and power operations on units while preserving dimensional consistency
- **Multiple Output Formats**: Convert units to LaTeX, UTF-8, and SIRP representations
- **Scale Factor Calculations**: Calculate conversion factors between compatible units
- **Base Unit Conversions**: Convert complex units to their base SI unit representation

> The **Javascript version** of this library has moved to <https://gitlab1.ptb.de/digitaldynamicmeasurement/dsiunits-js/>

## Installation

```bash
pip install dsiUnits
```

**Requirements**: Python 3.9+

## Quick Start

```python
from dsi_unit import DsiUnit

# Create units from D-SI notation
meter = DsiUnit(r"\metre")
second = DsiUnit(r"\second")
kilogram = DsiUnit(r"\kilogram")

# Or from BIPM-RP notation
velocity = DsiUnit("m.s-1")  # meters per second
```

## Usage Examples

### Basic Unit Operations

```python
from dsi_unit import DsiUnit

# Mathematical operations
velocity = DsiUnit(r"\metre") / DsiUnit(r"\second")
print(velocity)  # \metre\per\second

acceleration = velocity / DsiUnit(r"\second")
print(acceleration)  # \metre\per\second\tothe{2}

force = DsiUnit(r"\kilogram") * acceleration
print(force)  # \kilogram\metre\per\second\tothe{2}

# Power operations
area = DsiUnit(r"\metre") ** 2
print(area)  # \metre\tothe{2}
```

### Unit Conversions

```python
# Check if units are scalable (convertible)
joule = DsiUnit(r"\joule")
watt_second = DsiUnit(r"\watt") * DsiUnit(r"\second")
print(joule.is_scalable(watt_second))  # True

# Get scale factor between compatible units
km = DsiUnit(r"\kilo\metre")
m = DsiUnit(r"\metre")
scale = km.get_scale_factor(m)  # 0.001 (1 km = 1000 m, so 1 km * 0.001 = 1 m)

# Convert to base units
newton = DsiUnit(r"\newton")
base = newton.to_base_unit_tree()
print(base)  # \kilogram\metre\per\second\tothe{2}
```

### Output Formats

```python
unit = DsiUnit(r"\kilo\metre\tothe{2}\per\second")

# LaTeX representation
print(unit.to_latex())  # $$\frac{\mathrm{k}\mathrm{m}^{2}}{\mathrm{s}}$$

# UTF-8 representation
print(unit.to_utf8())  # km²/s

# SIRP (SI Reference Point) representation
print(unit.to_sirp())  # km2.s-1
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
