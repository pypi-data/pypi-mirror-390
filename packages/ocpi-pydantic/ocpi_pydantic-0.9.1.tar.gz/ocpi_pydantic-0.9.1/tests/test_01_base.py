from decimal import Decimal

from bson import Decimal128
from ocpi_pydantic.v221.base import OcpiPrice



class TestBase:
    def test_ocpi_price(self):
        p1 = OcpiPrice(excl_vat=Decimal('10.1'), incl_vat=Decimal('11.1'))
        assert p1.excl_vat == Decimal('10.1')
        assert p1.incl_vat == Decimal('11.1')

        p2 = OcpiPrice(excl_vat=Decimal128('12.1'), incl_vat=Decimal('13.1'))
        assert p2.excl_vat == Decimal('12.1')
        assert p2.incl_vat == Decimal('13.1')