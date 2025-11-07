import unittest
import jitx
from jitx.toleranced import Toleranced

import jitx.test


min_typ_max = Toleranced.min_typ_max
min_max = Toleranced.min_max


class TolerancedTestCase(jitx.test.TestCase):
    def test_basic(self):
        A = Toleranced(1.0, 0.1, 0.1)

        self.assertAlmostEqual(A.max_value, 1.1, places=3)
        self.assertAlmostEqual(A.min_value, 0.9, places=3)
        self.assertAlmostEqual(A.typ, 1.0, places=3)

        B = min_typ_max(4.5, 5.0, 5.5)

        self.assertAlmostEqual(B.max_value, 5.5, places=3)
        self.assertAlmostEqual(B.min_value, 4.5, places=3)
        self.assertAlmostEqual(B.typ, 5.0, places=3)

        B = min_max(-2.3, -0.5)
        self.assertAlmostEqual(B.max_value, -0.5, places=3)
        self.assertAlmostEqual(B.min_value, -2.3, places=3)
        self.assertAlmostEqual(B.typ, -1.4, places=3)

        C = Toleranced(-7.2, 0.4)

        self.assertAlmostEqual(C.max_value, -6.8, places=3)
        self.assertAlmostEqual(C.min_value, -7.6, places=3)
        self.assertAlmostEqual(C.typ, -7.2, places=3)

    def test_check_asserts(self):
        with self.assertRaises(AssertionError):
            Toleranced(1.0, 0.1, -0.1)

        with self.assertRaises(AssertionError):
            Toleranced(1.0, -0.1, 0.1)

        with self.assertRaises(ValueError):
            min_typ_max(1.0, 0.5, 2.0)

        with self.assertRaises(ValueError):
            min_typ_max(0.5, 1.0, 0.8)

        with self.assertRaises(AssertionError):
            Toleranced(0.0, -0.1)

    def test_span(self):
        uut = min_typ_max(1.0, 1.5, 2.5)
        self.assertAlmostEqual(uut.range(), 1.5, places=5)

        uut = min_typ_max(-5.0, -3.0, -1.5)
        self.assertAlmostEqual(uut.range(), 3.5, places=5)

        uut = min_typ_max(-4.0, 0.2, 3.2)
        self.assertAlmostEqual(uut.range(), 7.2, places=5)


if __name__ == "__main__":
    unittest.main()
