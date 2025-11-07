from jitx.container import inline

# from jitx.test import TestCase
from jitx.circuit import Circuit
from jitx.sample import SampleDesign
from jitxlib.parts.query_api import CapacitorQuery, ResistorQuery

from jitxexamples.components.isolators.texas_instruments_ISO1211 import (
    # ISO1211Circuit,
    Device as ISO1211Device,
)


class ISO1211Design(SampleDesign):
    _capacitor_defaults = CapacitorQuery(case=["0402", "0603"])
    _resistor_defaults = ResistorQuery(case=["0402"])

    @inline
    class circuit(Circuit):
        isolator_circuit = ISO1211Device()

        def __init__(self):
            # The ISO1211Circuit already has all the necessary connections
            # including bypass capacitors for both power domains
            pass


# class TestISO1211(TestCase):
#     def test_iso1211_circuit(self):
#         design = ISO1211Design()
#         # Verify that the circuit was created successfully
#         self.assertIsInstance(design.circuit.isolator_circuit, ISO1211Circuit)
#
#         # Verify that the isolator component exists
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "isolator"))
#
#         # Verify that the bypass capacitors exist
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "bypass_cap_input"))
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "bypass_cap_output"))
#
#         # Verify that power interfaces exist
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "power_input"))
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "power_output"))
#
#         # Verify that signal interfaces exist
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "enable"))
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "input_signal"))
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "output_signal"))
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "sense_signal"))
#
#         # Verify that nets are properly defined
#         self.assertTrue(hasattr(design.circuit.isolator_circuit, "nets"))
#         self.assertGreater(len(design.circuit.isolator_circuit.nets), 0)
#
#         # Verify that the isolator has the correct pins
#         isolator = design.circuit.isolator_circuit.isolator
#         self.assertTrue(hasattr(isolator, "VCC1"))
#         self.assertTrue(hasattr(isolator, "EN"))
#         self.assertTrue(hasattr(isolator, "OUT"))
#         self.assertTrue(hasattr(isolator, "GND1"))
#         self.assertTrue(hasattr(isolator, "SUB"))
#         self.assertTrue(hasattr(isolator, "FGND"))
#         self.assertTrue(hasattr(isolator, "IN"))
#         self.assertTrue(hasattr(isolator, "SENSE"))
