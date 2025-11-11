# OCPI Pydantic

Pydantic models for the [Open Charge Point Interface (OCPI)](https://evroaming.org/ocpi/), currently supporting OCPI 2.2.1.

This library provides a set of Pydantic models to build OCPI applications in Python, ensuring data validation and type hints.

## Installation

You can install `ocpi-pydantic` using pip:

```bash
pip install ocpi-pydantic
```

## Usage

Here is a quick example of how to use the models to create an OCPI `Location` object.

```python
from ocpi_pydantic.v221.locations.location import OcpiLocation, OcpiGeoLocation


location = OcpiLocation(
    country_code='TW',
    party_id='WNC',
    id='LOC1',
    publish=True,
    time_zone='Asia/Taipei',
    coordinates=OcpiGeoLocation(latitude='21.234', longitude='124.567'),
    postal_code='325',
    country='TWN',
    city='桃園市',
    address='龍潭區百年路一號',
    evses=[],
    last_updated=datetime.datetime.now(datetime.UTC),
)
```
