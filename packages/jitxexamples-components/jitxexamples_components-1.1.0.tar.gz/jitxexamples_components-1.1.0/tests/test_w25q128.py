from jitx.container import inline

# from jitx.test import TestCase
from jitx.circuit import Circuit
from jitx.sample import SampleDesign
from jitxlib.parts.query_api import CapacitorQuery, ResistorQuery

from jitxexamples.components.flash.winbond_W25Q128JVSIQ import (
    # W25Q128Circuit,
    Device as W25Q128Device,
)


class W25Q128Design(SampleDesign):
    _capacitor_defaults = CapacitorQuery(case=["0402", "0603"])
    _resistor_defaults = ResistorQuery(case=["0402"])

    @inline
    class circuit(Circuit):
        flash_circuit = W25Q128Device()

        def __init__(self):
            # The W25Q128Circuit already has all the necessary connections
            # including the 4.7µF bypass capacitor and WideSPI quad interface
            pass


# can't run as test case, requires an active runtime
# class TestW25Q128(TestCase):
#     def test_w25q128_circuit(self):
#         design = W25Q128Design()
#         # Verify that the circuit was created successfully
#         self.assertIsInstance(design.circuit.flash_circuit, W25Q128Circuit)
#
#         # Verify that the flash component exists
#         self.assertTrue(hasattr(design.circuit.flash_circuit, "flash"))
#
#         # Verify that the bypass capacitor exists
#         self.assertTrue(hasattr(design.circuit.flash_circuit, "bypass_cap"))
#
#         # Verify that the WideSPI interface exists
#         self.assertTrue(hasattr(design.circuit.flash_circuit, "qspi"))
#
#         # Verify that nets are properly defined
#         self.assertTrue(hasattr(design.circuit.flash_circuit, "nets"))
#         self.assertGreater(len(design.circuit.flash_circuit.nets), 0)
