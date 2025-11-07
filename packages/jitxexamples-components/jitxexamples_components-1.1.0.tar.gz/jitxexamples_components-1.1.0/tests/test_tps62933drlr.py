from jitx.container import inline

# from jitx.test import TestCase
from jitx.circuit import Circuit
from jitx.sample import SampleDesign

from jitxexamples.components.power_switchmode import texas_instruments_TPS62933DRLR
from jitxlib.parts import CapacitorQuery, ResistorQuery


class TPS62933DRLRDesign(SampleDesign):
    _capacitor_defaults = CapacitorQuery()
    _resistor_defaults = ResistorQuery(case="0402")

    @inline
    class circuit(Circuit):
        comp = texas_instruments_TPS62933DRLR.Device()


# Can't be run as a test case, as it requires an active runtime for queries
# class TestTPS62933DRLR(TestCase):
#     def test_lsf_smt(self):
#         design = LSF_SMTDesign()
#         # type ignore here because the type checker requires a type-narrowing check
#         self.assertIsInstance(design.circuit.comp, texas_instruments_TPS62933DRLR.Device)  # type: ignore
