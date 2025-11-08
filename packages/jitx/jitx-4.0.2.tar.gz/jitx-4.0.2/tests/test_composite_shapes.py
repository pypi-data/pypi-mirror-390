import jitx
import math
from jitx.anchor import Anchor
from jitx.shapes.composites import (
    rectangle,
    rectangle_from_bounds,
    plus_symbol,
    capsule,
)

from jitx.shapes.shapely import ShapelyGeometry
import jitx.test


class RectangleTestCase(jitx.test.TestCase):
    def test_basic(self):
        R = rectangle(10.0, 5.0)
        p = R.to_shapely()
        self.assertAlmostEqual(p.area, 10.0 * 5.0, 4)

        pt = p.centroid
        self.assertAlmostEqual(pt.x, 0.0, 4)
        self.assertAlmostEqual(pt.y, 0.0, 4)

        start = p.bounds[:2]
        end = p.bounds[2:]
        self.assertAlmostEqual(start[0], -5.0, 4)
        self.assertAlmostEqual(start[1], -2.5, 4)

        self.assertAlmostEqual(end[0], 5.0, 4)
        self.assertAlmostEqual(end[1], 2.5, 4)

    def test_with_anchor(self):
        testvectors = [
            (Anchor.SW, [(5.0, 2.5), (0, 0), (10.0, 5.0)]),
            (Anchor.NW, [(5.0, -2.5), (0, -5.0), (10.0, 0.0)]),
            (Anchor.NE, [(-5.0, -2.5), (-10, -5), (0.0, 0.0)]),
            (Anchor.SE, [(-5.0, 2.5), (-10, 0), (0.0, 5.0)]),
        ]
        for testvector in testvectors:
            anch, exps = testvector

            R = rectangle(10.0, 5.0, anchor=anch)

            p = R.to_shapely()
            self.assertAlmostEqual(p.area, 10.0 * 5.0, 4)

            expCtr, expStart, expEnd = exps
            pt = p.centroid
            self.assertAlmostEqual(pt.x, expCtr[0], 4)
            self.assertAlmostEqual(pt.y, expCtr[1], 4)

            start = p.bounds[:2]
            end = p.bounds[2:]
            self.assertAlmostEqual(start[0], expStart[0], 4)
            self.assertAlmostEqual(start[1], expStart[1], 4)

            self.assertAlmostEqual(end[0], expEnd[0], 4)
            self.assertAlmostEqual(end[1], expEnd[1], 4)

    def test_from_bounds(self):
        # Typical output of the `bounds` property of a
        #   shapely shape.
        testvector = (0.2, 0.4, 4.3, 5.9)
        R = rectangle_from_bounds(testvector)

        p = R.to_shapely()
        self.assertAlmostEqual(p.area, 4.1 * 5.5, 4)

        pt = p.centroid
        self.assertAlmostEqual(pt.x, 2.25, 4)
        self.assertAlmostEqual(pt.y, 3.15, 4)

        start = p.bounds[:2]
        end = p.bounds[2:]
        self.assertAlmostEqual(start[0], 0.2, 4)
        self.assertAlmostEqual(start[1], 0.4, 4)

        self.assertAlmostEqual(end[0], 4.3, 4)
        self.assertAlmostEqual(end[1], 5.9, 4)


class PlusSymbolTestCase(jitx.test.TestCase):
    def test_basic(self):
        uut = plus_symbol(1.0, 0.1)
        P = uut.to_shapely()
        self.assertAlmostEqual(P.area, 0.2057, places=3)

        ctr = P.centroid
        self.assertAlmostEqual(ctr.x, 0.0, places=4)
        self.assertAlmostEqual(ctr.y, 0.0, places=4)

    def test_with_anchor(self):
        uut = plus_symbol(1.0, 0.1, anchor=Anchor.SW)
        P = uut.to_shapely()
        self.assertAlmostEqual(P.area, 0.2057, places=3)

        ctr = P.centroid
        self.assertAlmostEqual(ctr.x, 0.55, places=4)
        self.assertAlmostEqual(ctr.y, 0.55, places=4)


class CapsuleTestCase(jitx.test.TestCase):
    def test_horizontal(self):
        uut = capsule(2.0, 1.0)

        P = ShapelyGeometry.from_shape(uut, tolerance=1e-4)
        expArea = 1.0 + (0.5 * 0.5 * math.pi)
        self.assertAlmostEqual(P.area, expArea, places=2)

        ctr = P.centroid
        self.assertAlmostEqual(ctr.x, 0.0, places=4)
        self.assertAlmostEqual(ctr.y, 0.0, places=4)

        bds = P.bounds
        self.assertAlmostEqual(bds[0], -1.0, places=4)
        self.assertAlmostEqual(bds[1], -0.5, places=4)
        self.assertAlmostEqual(bds[2], 1.0, places=4)
        self.assertAlmostEqual(bds[3], 0.5, places=4)

    def test_vertical(self):
        uut = capsule(1.0, 2.0)

        P = ShapelyGeometry.from_shape(uut, tolerance=1e-4)
        expArea = 1.0 + (0.5 * 0.5 * math.pi)
        self.assertAlmostEqual(P.area, expArea, places=2)

        ctr = P.centroid
        self.assertAlmostEqual(ctr.x, 0.0, places=4)
        self.assertAlmostEqual(ctr.y, 0.0, places=4)

        bds = P.bounds
        self.assertAlmostEqual(bds[0], -0.5, places=4)
        self.assertAlmostEqual(bds[1], -1.0, places=4)
        self.assertAlmostEqual(bds[2], 0.5, places=4)
        self.assertAlmostEqual(bds[3], 1.0, places=4)

    def test_with_anchor(self):
        uut = capsule(2.0, 1.0, anchor=Anchor.SE)

        P = uut.to_shapely()

        ctr = P.centroid
        self.assertAlmostEqual(ctr.x, -1.0, places=4)
        self.assertAlmostEqual(ctr.y, 0.5, places=4)
