from jitx.anchor import Anchor
from jitx.component import Component
from jitx.container import inline
from jitx.feature import Courtyard, Custom, Silkscreen, Soldermask, Paste
from jitx.landpattern import Landpattern, Pad, PadMapping
from jitx.net import Port
from jitx.shapes.composites import rectangle
from jitx.shapes.primitive import Arc, ArcPolyline, Polygon, Polyline, Text
from jitx.symbol import Direction, Pin, Symbol, SymbolMapping


class RectangleSMDPad(Pad):
    shape = rectangle(1.25, 0.7)
    soldermask = Soldermask(rectangle(1.352, 0.802))
    paste = Paste(rectangle(1.352, 0.802))


class BSS138(Component):
    """
    BSS138 N-Channel MOSFET

    50V 220mA 3.5Ω@10V,220mA 360mW N Channel SOT-23 MOSFET
    Manufacturer: Changjiang Electronics Tech (CJ)
    """

    name = "C78284"
    description = "50V 220mA 3.5Ω@10V,220mA 360mW N Channel SOT-23  MOSFETs ROHS"
    manufacturer = "Changjiang Electronics Tech (CJ)"
    mpn = "BSS138"
    datasheet = "https://datasheet.lcsc.com/lcsc/1809291614_Jiangsu-Changjing-Electronics-Technology-Co---Ltd--BSS138_C78284.pdf"
    reference_designator_prefix = "Q"

    # MOSFET pins
    D = Port()  # Drain
    G = Port()  # Gate
    S = Port()  # Source

    @inline
    class landpattern(Landpattern):
        # Pads
        p = {
            1: RectangleSMDPad().at(1, -0.949),
            2: RectangleSMDPad().at(1, 0.95),
            3: RectangleSMDPad().at(-1, 0),
        }

        # Labels
        labels = [
            Silkscreen(Text(">REF", 0.5, Anchor.W).at(-0.75, 3.308)),
            Custom(Text(">VALUE", 0.5, Anchor.W).at(-0.75, 2.308), name="Fab"),
        ]

        # Silkscreen
        silkscreen = [
            Silkscreen(
                Polyline(
                    0.152,
                    [(0.726, 1.527), (-0.726, 1.527), (-0.726, 0.495)],
                )
            ),
            Silkscreen(
                Polyline(
                    0.152,
                    [(0.726, -1.526), (-0.726, -1.526), (-0.726, -0.494)],
                )
            ),
            Silkscreen(Polyline(0.152, [(0.726, 0.456), (0.726, -0.455)])),
        ]

        # Fab drawing
        fab_drawing = [
            Custom(ArcPolyline(0.06, [Arc((1.2, -1.45), 0.03, 0, -360)]), name="Fab"),
            Custom(ArcPolyline(0.2, [Arc((1.46, -1.1), 0.1, 0, -360)]), name="Fab"),
        ]

        # Courtyard
        courtyard = Courtyard(rectangle(3.352, 3.205))

    @inline
    class symbol(Symbol):
        pin_name_size = 0.7
        pad_name_size = 0.7

        # Pin definitions
        D = Pin((2, 2), 2, Direction.Up)
        G = Pin((-2, 0), 2, Direction.Left)
        S = Pin((2, -2), 2, Direction.Down)

        # Text elements
        value = Text(">VALUE", 0.7056, Anchor.C).at(0, 2.79)
        reference = Text(">REF", 0.7056, Anchor.C).at(0, 3.57)

        # Symbol artwork - N-Channel MOSFET symbol
        art = [
            # Channel connections
            Polyline(0.2, [(0, 1.4), (2, 1.4), (2, 2), (4, 2), (4, 0.4)]),
            Polyline(0.2, [(0, 0), (2, 0), (2, -2), (4, -2), (4, -0.6)]),
            Polyline(0.2, [(2, -1.4), (0, -1.4)]),
            # Gate structure
            Polyline(0.2, [(-0.4, 1.8), (-0.4, -1.8)]),
            Polyline(0.2, [(0, 1.8), (0, 1)]),
            Polyline(0.2, [(0, -0.4), (0, 0.4)]),
            Polyline(0.2, [(0, -1.8), (0, -1)]),
            # Gate connection
            Polyline(0.2, [(-2, 0), (-0.4, 0)]),
            # Arrows/triangles
            Polygon([(0, 0), (1.2, -0.4), (1.2, 0.4)]),
            Polygon([(4, 0.4), (3.4, -0.6), (4.6, -0.6)]),
        ]

    # Pin mapping
    padmapping = PadMapping(
        {
            G: landpattern.p[1],  # Gate
            S: landpattern.p[2],  # Source
            D: landpattern.p[3],  # Drain
        }
    )

    # Symbol mapping
    symbolmapping = SymbolMapping(
        {
            D: symbol.D,
            G: symbol.G,
            S: symbol.S,
        }
    )


Device: type[BSS138] = BSS138
