from jitx.container import inline

from jitx.circuit import Circuit
from jitx.sample import SampleDesign
from jitxlib.parts.query_api import CapacitorQuery, ResistorQuery

from jitxexamples.components.connectors.hirose_electric_co_ltd_U_FL_R_SMT_10 import (
    Device as U_FL_R_SMT_10Device,
)


class U_FL_R_SMT_10Design(SampleDesign):
    _capacitor_defaults = CapacitorQuery(case=["0402", "0603"])
    _resistor_defaults = ResistorQuery(case=["0402"])

    @inline
    class circuit(Circuit):
        rf_connector = U_FL_R_SMT_10Device()

        def __init__(self):
            # The U.FL-R-SMT(10) is an RF connector with signal and ground connections
            # It includes internal matching components (capacitor and inductor)
            pass
