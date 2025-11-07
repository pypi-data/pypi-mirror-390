from jitx.container import inline

from jitx.circuit import Circuit
from jitx.sample import SampleDesign
from jitxlib.parts.query_api import CapacitorQuery, ResistorQuery

from jitxexamples.components.microphones.allpower_AP3722AT import (
    Device as AP3722ATDevice,
)


class AP3722ATDesign(SampleDesign):
    _capacitor_defaults = CapacitorQuery(case=["0402", "0603"])
    _resistor_defaults = ResistorQuery(case=["0402"])

    @inline
    class circuit(Circuit):
        microphone = AP3722ATDevice()

        def __init__(self):
            # The AP3722AT is a digital microphone with I2S output
            # It includes a bypass capacitor and has power and output interfaces
            pass
