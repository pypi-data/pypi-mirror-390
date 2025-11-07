from jitx.container import inline

# from jitx.test import TestCase
from jitx.circuit import Circuit
from jitx.sample import SampleDesign
from jitxlib.parts.query_api import CapacitorQuery, ResistorQuery

from jitxexamples.components.transceivers.texas_instruments_SN65HVD1781DR import (
    # SN65HVD1781DRReferenceCircuit,
    Device as SN65HVD1781DRDevice,
)


class SN65HVD1781DRDesign(SampleDesign):
    _capacitor_defaults = CapacitorQuery(case=["0402", "0603"])
    _resistor_defaults = ResistorQuery(case=["0402"])

    @inline
    class circuit(Circuit):
        rs485_transceiver = SN65HVD1781DRDevice()

        def __init__(self):
            # The SN65HVD1781DRReferenceCircuit already has all the necessary connections
            # including bypass capacitors, pull-up resistors, and TVS protection
            pass


# requires active runtime
# class TestSN65HVD1781DR(TestCase):
#     def test_sn65hvd1781dr_circuit(self):
#         design = SN65HVD1781DRDesign()
#         # Verify that the circuit was created successfully
#         self.assertIsInstance(
#             design.circuit.rs485_transceiver, SN65HVD1781DRReferenceCircuit
#         )
#
#         # Verify that the transceiver component exists
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "transceiver"))
#
#         # Verify that the bypass capacitor exists
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "bypass_cap"))
#
#         # Verify that the pull-up resistors exist
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "re_pullup"))
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "de_pullup"))
#
#         # Verify that the series resistors exist
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "rs485a_series"))
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "rs485b_series"))
#
#         # Verify that TVS diodes exist
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "tvs_rs485a"))
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "tvs_rs485b"))
#
#         # Verify that power and signal interfaces exist
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "power"))
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "uart"))
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "dir_pin"))
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "rs485_a"))
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "rs485_b"))
#
#         # Verify UART interface has tx and rx
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver.uart, "tx"))
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver.uart, "rx"))
#
#         # Verify that nets are properly defined
#         self.assertTrue(hasattr(design.circuit.rs485_transceiver, "nets"))
#         self.assertGreater(len(design.circuit.rs485_transceiver.nets), 0)
#
#         # Verify that the transceiver has the correct pins
#         transceiver = design.circuit.rs485_transceiver.transceiver
#         self.assertTrue(hasattr(transceiver, "R"))
#         self.assertTrue(hasattr(transceiver, "RE_NOT"))
#         self.assertTrue(hasattr(transceiver, "DE"))
#         self.assertTrue(hasattr(transceiver, "D"))
#         self.assertTrue(hasattr(transceiver, "GND"))
#         self.assertTrue(hasattr(transceiver, "A"))
#         self.assertTrue(hasattr(transceiver, "B"))
#         self.assertTrue(hasattr(transceiver, "VCC"))
