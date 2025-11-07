"""
Winbond W25Q128 Serial Flash Memory

Component definition for Winbond W25Q128JVSIQ 128Mbit Serial Flash Memory
"""

from jitx.anchor import Anchor
from jitx.feature import Courtyard, Custom, Paste, Silkscreen, Soldermask
from jitx.landpattern import Landpattern, Pad, PadMapping
from jitx.model3d import Model3D
from jitx.net import Port
from jitx.shapes.composites import rectangle
from jitx.shapes.primitive import Arc, ArcPolyline, Circle, Polyline, Text
from jitx.symbol import Direction, Pin, Symbol, SymbolMapping
from jitx.component import Component
from jitx.circuit import Circuit
from jitx.common import Power
from jitxlib.protocols.serial import WideSPI
from jitxlib.parts import Capacitor


class CapsuleSmdPad(Pad):
    """SMD pad for SOIC-8 package with capsule shape"""

    shape = rectangle(0.63, 2.25)
    solder_mask = [Soldermask(rectangle(0.732, 2.352))]
    paste = [Paste(rectangle(0.732, 2.352))]


class LandpatternSOIC_8_L5_3_W5_3_P1_27_LS8_0_BL(Landpattern):
    """SOIC-8 landpattern for W25Q128JVSIQ flash memory"""

    name = "SOIC-8_L5.3-W5.3-P1.27-LS8.0-BL"
    p = {
        1: CapsuleSmdPad().at((-1.905, -3.5305)),
        2: CapsuleSmdPad().at((-0.635, -3.5305)),
        3: CapsuleSmdPad().at((0.635, -3.5305)),
        4: CapsuleSmdPad().at((1.905, -3.5305)),
        5: CapsuleSmdPad().at((1.905, 3.5305)),
        6: CapsuleSmdPad().at((0.635, 3.5305)),
        7: CapsuleSmdPad().at((-0.635, 3.5305)),
        8: CapsuleSmdPad().at((-1.905, 3.5305)),
    }
    reference_designator = Silkscreen(Text(">REF", 0.5, Anchor.W).at((-0.75, 6.4121)))
    value_label = Custom(Text(">VALUE", 0.5, Anchor.W).at((-0.75, 5.4121)), name="Fab")
    silkscreen = [
        Silkscreen(
            Polyline(
                0.152,
                [
                    (-2.639, -2.1765),
                    (-2.639, 2.1765),
                    (2.639, 2.1765),
                    (2.639, -2.1765),
                    (-2.639, -2.1765),
                ],
            )
        ),
        Silkscreen(ArcPolyline(0.3, [Arc((-1.905, -1.4235), 0.15, 0, -360)])),
        Silkscreen(ArcPolyline(0.3, [Arc((-2.672, -3.5305), 0.15, 0, -360)])),
    ]
    custom_layer = [
        Custom(ArcPolyline(0.3, [Arc((-1.905, -4.3505), 0.15, 0, -360)]), name="Fab"),
        Custom(ArcPolyline(0.06, [Arc((-2.585, -3.9205), 0.03, 0, -360)]), name="Fab"),
    ]
    courtyard = Courtyard(rectangle(5.43, 9.413))
    model3d = Model3D(
        "winbond_W25Q128JVSIQ.stp",
        position=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
        rotation=(0.0, 0.0, 0.0),
    )


class SymbolW25Q128JVSIQTR(Symbol):
    """Schematic symbol for W25Q128JVSIQ flash memory"""

    pin_name_size = 0.7874
    pad_name_size = 0.7874
    CS_NOT = Pin((-8, 3), 2, Direction.Left)
    DO = Pin((-8, 1), 2, Direction.Left)
    IO2 = Pin((-8, -1), 2, Direction.Left)
    GND = Pin((-8, -3), 2, Direction.Left)
    DI = Pin((8, -3), 2, Direction.Right)
    CLK = Pin((8, -1), 2, Direction.Right)
    IO3 = Pin((8, 1), 2, Direction.Right)
    VCC = Pin((8, 3), 2, Direction.Right)
    reference_designator = Text(">REF", 0.55559, Anchor.C).at((0, 6.27481))
    value_label = Text(">VALUE", 0.55559, Anchor.C).at((0, 5.48741))
    shapes = [
        rectangle(16.00003, 10.80002),
        Circle(radius=0.3).at((-7.00001, 4.40001)),
        Circle(radius=0.3).at((-7.00001, 4.40001)),
    ]


class W25Q128JVSIQ(Component):
    """Winbond W25Q128JVSIQ 128Mbit Serial Flash Memory"""

    manufacturer = "Winbond"
    mpn = "W25Q128JVSIQ"
    reference_designator_prefix = "U"
    datasheet = "https://www.lcsc.com/datasheet/lcsc_datasheet_1811142111_Winbond-Elec-W25Q128JVSIQ_C97521.pdf"
    CS_NOT = Port()
    """Chip Select (active low)"""
    DO = Port()
    """Data Output (MISO)"""
    IO2 = Port()
    """I/O2 pin for quad SPI operation"""
    GND = Port()
    """Ground connection"""
    DI = Port()
    """Data Input (MOSI)"""
    CLK = Port()
    """Serial Clock"""
    IO3 = Port()
    """I/O3 pin for quad SPI operation"""
    VCC = Port()
    """Power supply (2.7V to 3.6V)"""
    landpattern = LandpatternSOIC_8_L5_3_W5_3_P1_27_LS8_0_BL()
    symbol = SymbolW25Q128JVSIQTR()
    cmappings = [
        SymbolMapping(
            {
                CS_NOT: symbol.CS_NOT,
                DO: symbol.DO,
                IO2: symbol.IO2,
                GND: symbol.GND,
                DI: symbol.DI,
                CLK: symbol.CLK,
                IO3: symbol.IO3,
                VCC: symbol.VCC,
            }
        ),
        PadMapping(
            {
                CS_NOT: landpattern.p[1],
                DO: landpattern.p[2],
                IO2: landpattern.p[3],
                GND: landpattern.p[4],
                DI: landpattern.p[5],
                CLK: landpattern.p[6],
                IO3: landpattern.p[7],
                VCC: landpattern.p[8],
            }
        ),
    ]


class W25Q128(Circuit):
    """
    W25Q128 128Mbit Serial Flash Memory Reference Circuit

    Features:
    - W25Q128JVSIQ flash memory IC (128Mbit/16MB capacity)
    - 4.7µF bypass capacitor for power supply decoupling
    - SPI interface for communication
    - Proper power and ground connections

    Pin Configuration:
    - CS_NOT: Chip Select (active low)
    - DI: Data Input (MOSI)
    - DO: Data Output (MISO)
    - CLK: Serial Clock
    - IO2: I/O2 (for quad SPI)
    - IO3: I/O3 (for quad SPI)
    - VCC: Power supply (2.7V to 3.6V)
    - GND: Ground

    Datasheet: https://www.lcsc.com/datasheet/lcsc_datasheet_1811142111_Winbond-Elec-W25Q128JVSIQ_C97521.pdf
    """

    # Power supply interface
    power = Power()

    # Quad SPI interface for full 4-wire operation
    qspi = WideSPI.quad(cs=True)

    def __init__(self):
        # Instantiate the W25Q128 flash memory
        self.flash = W25Q128JVSIQ()

        # 4.7µF bypass capacitor for power supply decoupling
        # Using X7R dielectric for good temperature stability
        self.bypass_cap = Capacitor(capacitance=4.7e-6).insert(
            self.flash.VCC, self.flash.GND, short_trace=True
        )

        # Net connections
        nets_list = [
            # Power connections
            self.power.Vp + self.flash.VCC,
            self.power.Vn + self.flash.GND,
            # Quad SPI interface connections
            # Connect all 4 data lines for full quad SPI operation
            self.qspi.data[0] + self.flash.DI,  # Data line 0 (MOSI in standard SPI)
            self.qspi.data[1] + self.flash.DO,  # Data line 1 (MISO in standard SPI)
            self.qspi.data[2] + self.flash.IO2,  # Data line 2 (for quad SPI)
            self.qspi.data[3] + self.flash.IO3,  # Data line 3 (for quad SPI)
            self.qspi.sck + self.flash.CLK,  # Serial Clock
        ]

        # Add chip select connection if available
        if self.qspi.cs is not None:
            nets_list.append(self.qspi.cs + self.flash.CS_NOT)

        self.nets = nets_list


# Device alias for easy import following JITX patterns
Device: type[W25Q128] = W25Q128
