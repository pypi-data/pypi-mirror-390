from unittest import TestCase

from jitx.shapes.primitive import Arc


class TestArc(TestCase):
    def test_three_point(self) -> None:
        a = Arc((0, 0), (5, 0), (0, 5))
        self.assertEqual(a.center, (2.5, 2.5))
