from jitx.container import inline

from jitx.circuit import Circuit
from jitx.sample import SampleDesign
from jitxlib.parts.query_api import CapacitorQuery, InductorQuery, ResistorQuery

from jitxexamples.components.mcus.nordic_NRF52840_QIAA_R import (
    Device as NRF52840_QIAA_RDevice,
)


class NRF52840_QIAA_RDesign(SampleDesign):
    _capacitor_defaults = CapacitorQuery(case=["0402", "0603"])
    _resistor_defaults = ResistorQuery(case=["0402"])
    _inductor_defaults = InductorQuery(case=["0402", "0603"])

    @inline
    class circuit(Circuit):
        mcu = NRF52840_QIAA_RDevice()

        def __init__(self):
            # The NRF52840 is a Bluetooth 5, Thread and Zigbee multiprotocol SoC
            # It includes power management, oscillators, and various interfaces
            pass
