from jitx.anchor import Anchor
from jitx.component import Component
from jitx.feature import Courtyard, Custom, Paste, Silkscreen, Soldermask
from jitx.landpattern import Landpattern, Pad, PadMapping
from jitx.model3d import Model3D
from jitx.net import Port
from jitx.shapes.composites import rectangle
from jitx.shapes.primitive import Arc, ArcPolyline, Polyline, Text
from jitx.symbol import Direction, Pin, Symbol, SymbolMapping


class RectangleSmdPad(Pad):
    shape = rectangle(0.49, 1.157)
    soldermask = Soldermask(rectangle(0.592, 1.259))
    paste = Paste(rectangle(0.592, 1.259))


class RectangleSmdPad1(Pad):
    shape = rectangle(0.49, 1.175)
    soldermask = Soldermask(rectangle(0.592, 1.277))
    paste = Paste(rectangle(0.592, 1.277))


class LandpatternSOT_23_5_L3_0_W1_7_P0_95_LS2_8_BL(Landpattern):
    name = "SOT-23-5_L3.0-W1.7-P0.95-LS2.8-BL"
    p = {
        1: RectangleSmdPad().at((-0.95, -1.158)),
        2: RectangleSmdPad().at((0, -1.158)),
        3: RectangleSmdPad().at((0.95, -1.158)),
        4: RectangleSmdPad1().at((0.95, 1.149)),
        5: RectangleSmdPad1().at((-0.95, 1.149)),
    }
    reference_designator = Silkscreen(Text(">REF", 0.5, Anchor.W).at((-0.75, 3.4931)))
    value_label = Custom(Text(">VALUE", 0.5, Anchor.W).at((-0.75, 2.4931)), name="Fab")
    silkscreen = [
        Silkscreen(Polyline(0.152, [(-1.526, -0.856), (-1.526, 0.847)])),
        Silkscreen(Polyline(0.152, [(1.526, -0.856), (1.526, 0.847)])),
        Silkscreen(Polyline(0.152, [(0.476, 0.847), (-0.476, 0.847)])),
        Silkscreen(ArcPolyline(0.3, [Arc((-1.651, -1.148), 0.15, 0, -360)])),
    ]
    custom_layer = [
        Custom(ArcPolyline(0.2, [Arc((-0.95, -1.767), 0.1, 0, -360)]), name="Fab"),
        Custom(ArcPolyline(0.06, [Arc((-1.42, -1.375), 0.03, 0, -360)]), name="Fab"),
    ]
    courtyard = [Courtyard(rectangle(3.204, 3.575))]
    model3ds = [
        Model3D(
            "texas_instruments_TLV314IDBVR.stp",
            position=(0.0, 0.0, 0.0),
            scale=(1.0, 1.0, 1.0),
            rotation=(0.0, 0.0, 0.0),
        )
    ]


class SymbolTLV314IDBVR(Symbol):
    pin_name_size = 0.7874
    pad_name_size = 0.7874
    INn = Pin((-4, 2), 4, Direction.Left)
    INp = Pin((-4, -2), 4, Direction.Left)
    Vn = Pin((0, -4), 4, Direction.Down)
    OUT = Pin((4, 0), 4, Direction.Right)
    Vp = Pin((0, 4), 4, Direction.Up)
    reference_designator = Text(">REF", 0.55559, Anchor.C).at((0, 5.57481))
    value_label = Text(">VALUE", 0.55559, Anchor.C).at((0, 4.78741))
    shapes = [
        Polyline(
            0.254,
            [
                (-4, -4),
                (4, 0),
                (-4, 4),
                (-4, -4),
            ],
        ),
        Polyline(0.254, [(-3.2, 2), (-2, 2)]),
        Polyline(0.254, [(-3.2, -2), (-2, -2)]),
        Polyline(0.254, [(-2.6, -1.4), (-2.6, -2.6)]),
        Polyline(0.254, [(0, 4), (0, 2)]),
        Polyline(0.254, [(0, -2), (0, -4)]),
    ]


class TLV314IDBVR(Component):
    manufacturer = "Texas Instruments"
    mpn = "TLV314IDBVR"
    reference_designator_prefix = "U"
    datasheet = "https://www.lcsc.com/datasheet/lcsc_datasheet_1809251733_Texas-Instruments-TLV314IDBVR_C133032.pdf"
    INn = Port()
    INp = Port()
    Vn = Port()
    OUT = Port()
    Vp = Port()
    landpattern = LandpatternSOT_23_5_L3_0_W1_7_P0_95_LS2_8_BL()
    symbol = SymbolTLV314IDBVR()
    cmappings = [
        SymbolMapping(
            {
                INn: symbol.INn,
                INp: symbol.INp,
                Vn: symbol.Vn,
                OUT: symbol.OUT,
                Vp: symbol.Vp,
            }
        ),
        PadMapping(
            {
                INn: landpattern.p[4],
                INp: landpattern.p[3],
                Vn: landpattern.p[2],
                OUT: landpattern.p[1],
                Vp: landpattern.p[5],
            }
        ),
    ]


Device: type[TLV314IDBVR] = TLV314IDBVR
