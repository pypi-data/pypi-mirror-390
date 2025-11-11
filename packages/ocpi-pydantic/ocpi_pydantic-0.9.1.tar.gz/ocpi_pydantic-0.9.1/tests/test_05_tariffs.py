from datetime import datetime, timezone
from decimal import Decimal

from bson import Decimal128
from ocpi_pydantic.v221.enum import OcpiTariffDimensionTypeEnum
from ocpi_pydantic.v221.locations.location import OcpiEnergyMix
from ocpi_pydantic.v221.tariffs import OcpiPriceComponent, OcpiTariff, OcpiTariffElement



class TestTariffs:
    def test_price_component(self):
        p1 = OcpiPriceComponent(type=OcpiTariffDimensionTypeEnum.FLAT, price=Decimal('10.1'), step_size=1)
        assert p1.price == Decimal('10.1')

        p2 = OcpiPriceComponent(type=OcpiTariffDimensionTypeEnum.FLAT, price=Decimal128('11.1'), step_size=1)
        assert p2.price == Decimal('11.1')


    def test_tariff(self):
        t = OcpiTariff(
            country_code='TW',
            party_id='WIN',
            id='ID1',
            currency='NTD',
            elements=[OcpiTariffElement(
                price_components=[OcpiPriceComponent(type=OcpiTariffDimensionTypeEnum.FLAT, price=10, step_size=1)],
            )],
            energy_mix=OcpiEnergyMix(is_green_energy=False),
            last_updated=datetime.now(timezone.utc),
        )
        assert t