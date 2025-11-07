# This file is generated based on the parts database query below:
#    from jitx_parts.query_api import create_part
#    class Example(Circuit) :
#        part = create_part(mpn = "SN74HC14PWR", manufacturer = "Texas Instruments")()

# File Location: components/Texas_Instruments/ComponentSN74HC14PWR.py
# To import this component:
#     from components.Texas_Instruments.ComponentSN74HC14PWR import ComponentSN74HC14PWR
from jitx import Circuit, Polygon
from jitx.common import Power
from jitx.landpattern import Landpattern, Pad
from jitx.model3d import Model3D
from jitx.symbol import Symbol, Pin, Direction
from jitx.component import Component
from jitx.net import Port
from jitx.landpattern import PadMapping
from jitx.symbol import SymbolMapping
from jitx.feature import Silkscreen, Custom, Paste, Soldermask, Courtyard
from jitx.anchor import Anchor
from jitx.shapes.primitive import Polyline, Circle, Arc, ArcPolyline, Text
from jitx.shapes.composites import rectangle
from jitxlib.parts import Capacitor


class RectangleSmdPad(Pad):
    shape = rectangle(0.4, 1.7)
    paste = Paste(rectangle(0.502, 1.802))
    soldermask = Soldermask(rectangle(0.502, 1.802))


class LandpatternTSSOP_14_L5_0_W4_4_P0_65_LS6_4_BL(Landpattern):
    p = {
        1: RectangleSmdPad().at((-1.9425, -2.8)),
        2: RectangleSmdPad().at((-1.2925, -2.8)),
        3: RectangleSmdPad().at((-0.6425, -2.8)),
        4: RectangleSmdPad().at((0.0075, -2.8)),
        5: RectangleSmdPad().at((0.6575, -2.8)),
        6: RectangleSmdPad().at((1.3075, -2.8)),
        7: RectangleSmdPad().at((1.9575, -2.8)),
        8: RectangleSmdPad().at((1.9575, 2.8)),
        9: RectangleSmdPad().at((1.3075, 2.8)),
        10: RectangleSmdPad().at((0.6575, 2.8)),
        11: RectangleSmdPad().at((0.0075, 2.8)),
        12: RectangleSmdPad().at((-0.6425, 2.8)),
        13: RectangleSmdPad().at((-1.2925, 2.8)),
        14: RectangleSmdPad().at((-1.9425, 2.8)),
    }

    customlayer = [
        Custom(Text(">VALUE", 0.5, Anchor.W).at((-0.75, 4.4066)), name="Fab"),
        Custom(ArcPolyline(0.06, [Arc((-2.4925, -3.2), 0.03, 0, -360)]), name="Fab"),
        Custom(ArcPolyline(0.3, [Arc((-1.9565, -3.662), 0.15, 0, -360)]), name="Fab"),
    ]
    silkscreen = [
        Silkscreen(Text(">REF", 0.5, Anchor.W).at((-0.75, 5.4066))),
        Silkscreen(Polyline(0.254, [(-2.5075, -1.601), (-2.5075, -0.686)])),
        Silkscreen(Polyline(0.254, [(-2.5075, 0.685), (-2.5075, 1.6)])),
        Silkscreen(Polyline(0.254, [(-2.4925, 2.25), (-2.3775, 2.25)])),
        Silkscreen(
            Polyline(
                0.254,
                [(2.3915, 2.25), (2.5075, 2.25), (2.5075, -2.25), (2.3915, -2.25)],
            )
        ),
        Silkscreen(Polyline(0.254, [(-2.3775, -2.25), (-2.4925, -2.25)])),
        Silkscreen(Polyline(0.254, [(-2.5075, 1.6), (-2.5075, 2.25)])),
        Silkscreen(Polyline(0.254, [(-2.5075, -1.601), (-2.5075, -2.25)])),
        Silkscreen(ArcPolyline(0.254, [Arc((-2.5075, 0), 0.686, 90, -180)])),
        Silkscreen(ArcPolyline(0.4, [Arc((-2.7425, -3), 0.2, 0, -360)])),
    ]

    courtyard = Courtyard(rectangle(5.269, 7.402))
    model = Model3D(
        "texas_instruments_SN74HC14PWR.stp",
        position=(0, 0, 0),
        scale=(1, 1, 1),
        rotation=(0, 0, -90.0),
    )


class SymbolSchmittInverter(Symbol):
    A = Pin((-2, 0), 2, Direction.Left)
    Y = Pin((1, 0), 2, Direction.Right)
    reference_designator = Text(">REF", 0.55559, Anchor.C).at((0, -2.0))
    shapes = [
        # Inverter triangle
        Polygon([(-2, 1.5), (-2, -1.5), (1, 0)]),
        # Inversion bubble at output
        Circle(radius=0.2).at((1.2, 0)),
        # Refined hysteresis symbol - more recognizable square wave
        Polyline(0.1, [(-1.4, -0.3), (-0.8, -0.3), (-0.8, 0.3)]),
        Polyline(0.1, [(-0.6, 0.3), (-1.2, 0.3), (-1.2, -0.3)]),
    ]


class SymbolSN74HC14PWR(Symbol):
    pin_name_size = 0.7874
    pad_name_size = 0.7874
    GND = Pin((-2, -1), 2, Direction.Left)
    VCC = Pin((2, 1), 2, Direction.Right)
    reference_designator = Text(">REF", 0.55559, Anchor.W).at((-2, 2.8))
    value_label = Text(">VALUE", 0.55559, Anchor.W).at((-2, 2.0))
    box = rectangle(4.0, 3.0)


class SN74HC14PWR(Component):
    name = "C6821"
    description = "Schmitt Trigger 6 21ns@6V,50pF 2uA 2V~6V TSSOP-14  Inverters ROHS"
    manufacturer = "Texas Instruments"
    mpn = "SN74HC14PWR"
    datasheet = "https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Texas-Instruments-SN74HC14PWR_C6821.pdf"
    reference_designator_prefix = "U"
    landpattern = LandpatternTSSOP_14_L5_0_W4_4_P0_65_LS6_4_BL()

    P_1A = Port()
    P_1Y = Port()
    P_2A = Port()
    P_2Y = Port()
    P_3A = Port()
    P_3Y = Port()
    GND = Port()

    P_4Y = Port()
    P_4A = Port()
    P_5Y = Port()
    P_5A = Port()
    P_6Y = Port()
    P_6A = Port()
    VCC = Port()

    symbol = SymbolSN74HC14PWR()
    schmitts = [SymbolSchmittInverter() for _ in range(6)]
    mappings = [
        SymbolMapping(
            {
                P_1A: schmitts[0].A,
                P_1Y: schmitts[0].Y,
                P_2A: schmitts[1].A,
                P_2Y: schmitts[1].Y,
                P_3A: schmitts[2].A,
                P_3Y: schmitts[2].Y,
                GND: symbol.GND,
                P_4Y: schmitts[3].Y,
                P_4A: schmitts[3].A,
                P_5Y: schmitts[4].Y,
                P_5A: schmitts[4].A,
                P_6Y: schmitts[5].Y,
                P_6A: schmitts[5].A,
                VCC: symbol.VCC,
            }
        ),
        PadMapping(
            {
                P_1A: landpattern.p[1],
                P_1Y: landpattern.p[2],
                P_2A: landpattern.p[3],
                P_2Y: landpattern.p[4],
                P_3A: landpattern.p[5],
                P_3Y: landpattern.p[6],
                GND: landpattern.p[7],
                P_4Y: landpattern.p[8],
                P_4A: landpattern.p[9],
                P_5Y: landpattern.p[10],
                P_5A: landpattern.p[11],
                P_6Y: landpattern.p[12],
                P_6A: landpattern.p[13],
                VCC: landpattern.p[14],
            }
        ),
    ]


class SN74HC14PWRCircuit(Circuit):
    power = Power()
    inv = SN74HC14PWR()

    def __init__(self):
        self.nets = [self.inv.GND + self.power.Vn, self.inv.VCC + self.power.Vp]

    byp = Capacitor(capacitance=4.7e-6).insert(inv.VCC, inv.GND, short_trace=True)


Device: type[SN74HC14PWR] = SN74HC14PWR
