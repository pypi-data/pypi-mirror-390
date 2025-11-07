from jitx.container import inline

from jitx.circuit import Circuit
from jitx.sample import SampleDesign
from jitxlib.parts.query_api import CapacitorQuery, ResistorQuery

from jitxexamples.components.connectors.myoung_MY_1632_03 import (
    Device as MY_1632_03Device,
)


class MY_1632_03Design(SampleDesign):
    _capacitor_defaults = CapacitorQuery(case=["0402", "0603"])
    _resistor_defaults = ResistorQuery(case=["0402"])

    @inline
    class circuit(Circuit):
        battery_connector = MY_1632_03Device()

        def __init__(self):
            # The MY_1632_03 is a battery connector that provides power
            # It has a single power output that can be used by other components
            pass
