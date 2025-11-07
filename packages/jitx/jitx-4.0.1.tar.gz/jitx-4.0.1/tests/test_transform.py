from jitx.feature import Soldermask
from jitx.inspect import visit
from jitx.landpattern import Landpattern, Pad
from jitx.shapes import Shape
from jitx.shapes.primitive import Circle
import jitx.test
from jitx.transform import IDENTITY, Transform


def matmult(Am, Bm):
    return tuple(
        tuple(sum(Am[i][x] * Bm[x][j] for x in range(3)) for j in range(3))
        for i in range(3)
    )


class TransformTestCase(jitx.test.TestCase):
    def test_mat_mult(self):
        A = Transform((2, 3), 23, (2, 2))
        B = Transform((5, -9), -45, (1.5, 0.5))
        AB = A * B
        Am = A.matrix3x3(row_major=True)
        Bm = B.matrix3x3(row_major=True)
        ABm = AB.matrix3x3(row_major=True)
        AmBm = matmult(Am, Bm)
        for rABm, rAmBm in zip(ABm, AmBm, strict=True):
            for cABm, cAmBm in zip(rABm, rAmBm, strict=True):
                self.assertAlmostEqual(cABm, cAmBm)

    def test_visit_kinematic(self):
        class P(Pad):
            shape = Circle(diameter=0.5)
            soldermask = Soldermask(Circle(diameter=0.6))

        class LP(Landpattern):
            p1 = P().at(Transform((1, 0), 90))
            p2 = P().at(Transform((-1, 0), -90))

        lp = LP()
        for trace, _shape in visit(lp, Shape):
            assert trace.transform is not None
            if trace.path[0] == "p1":
                self.assertEqual(trace.transform._rotate, 90)
            elif trace.path[0] == "p2":
                self.assertEqual(trace.transform._rotate, -90)

    def test_inverse(self):
        a = Transform((1, 1), 90, (-1, 1))
        b = ~a
        self.assertEqual(a * b, IDENTITY)
