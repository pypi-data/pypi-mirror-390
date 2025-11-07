import jitx
from jitx.anchor import Anchor

import jitx.test


class AnchorTestCase(jitx.test.TestCase):
    def test_basic(self):
        A = Anchor.NW
        B = Anchor.SW

        self.assertIsNot(A, B)

        C = Anchor.NW

        self.assertEqual(A, C)

        msg = str(A)
        self.assertEqual(msg, "Anchor.NW")

    def test_anchor_components(self):
        testvectors = [
            # UUT    , Horz    , Vert
            [Anchor.N, Anchor.C, Anchor.N],
            [Anchor.S, Anchor.C, Anchor.S],
            [Anchor.E, Anchor.E, Anchor.C],
            [Anchor.W, Anchor.W, Anchor.C],
            [Anchor.NW, Anchor.W, Anchor.N],
            [Anchor.NE, Anchor.E, Anchor.N],
            [Anchor.SW, Anchor.W, Anchor.S],
            [Anchor.SE, Anchor.E, Anchor.S],
            [Anchor.C, Anchor.C, Anchor.C],
        ]

        for testvector in testvectors:
            uut, expH, expV = testvector

            obsH = uut.horizontal()
            obsV = uut.vertical()

            self.assertEqual(obsH, expH)
            self.assertEqual(obsV, expV)
