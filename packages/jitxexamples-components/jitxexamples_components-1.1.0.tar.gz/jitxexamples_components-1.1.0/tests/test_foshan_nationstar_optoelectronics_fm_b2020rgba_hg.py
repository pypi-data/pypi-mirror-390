from jitx.container import inline

from jitx.circuit import Circuit
from jitx.sample import SampleDesign
from jitxlib.parts.query_api import CapacitorQuery, ResistorQuery

from jitxexamples.components.leds.foshan_nationstar_optoelectronics_FM_B2020RGBA_HG import (
    Device as FM_B2020RGBA_HGDevice,
)


class FM_B2020RGBA_HGDesign(SampleDesign):
    _capacitor_defaults = CapacitorQuery(case=["0402", "0603"])
    _resistor_defaults = ResistorQuery(case=["0402"])

    @inline
    class circuit(Circuit):
        rgb_led = FM_B2020RGBA_HGDevice()

        def __init__(self):
            # The FM-B2020RGBA-HG is an RGB LED with common anode
            # It has separate cathodes for Red, Green, Blue and a common anode
            pass
