import jitx
from jitx.inspect import Trace
from jitx.net import Port, PortArray
from jitx._structural import Structural, Proxy
from jitx._translate.dispatch import dispatch
from jitx.memo import memoize
from jitx.error import InvalidElementException

from jitx.refpath import RefPath
import jitx.test


class SubCircuit(jitx.Circuit):
    array = PortArray(3)

    def __init__(self):
        self.z = jitx.Circuit()


class Main(jitx.Circuit):
    one = SubCircuit()


class InstantiationTestDesign(jitx.Design):
    circuit = Main()


class InstantiationTestCase(jitx.test.TestCase):
    def test_separate_instance_identities(self):
        q1 = Main()
        q2 = Main()

        self.assertIsNot(q1, q2)
        self.assertIsNot(q1.one, q2.one)
        self.assertIsNot(q1.one.z, q2.one.z)
        self.assertIsNot(q1.one.array[0], q2.one.array[1])
        self.assertEqual(len(q1.one.array), 3)

        self.assertIs(type(q1.one.array), type(q2.one.array))


class TraverseTestCase(jitx.test.TestCase):
    def test_traverse_design(self):
        design = InstantiationTestDesign()

        with dispatch(design) as d:

            @d.register
            def _(ob: Main, trace: Trace):
                self.assertEqual(trace.path, RefPath(("circuit",)))

            @d.register
            def _(ob: jitx.Board, trace: Trace):
                self.assertEqual(trace.path.steps, ("board",))

            @d.register
            def _(ob: jitx.Circuit, trace: Trace):
                self.assertTrue(False, "Should not be called")

        with dispatch(design.circuit) as d:

            @d.register
            def _(ob: SubCircuit, trace: Trace):
                self.assertEqual(trace.path.steps, ("one",))

            @d.register
            def _(ob: jitx.Circuit, trace: Trace):
                self.assertEqual(trace.path.steps, ("other",))

    def test_reject_bad_subelement(self):
        class BadElement(Structural):
            pass

        class BadContainer(Structural):
            bad = [BadElement()]

        bad = BadContainer()

        with self.assertRaises(InvalidElementException):
            with dispatch(bad):
                pass

    def test_bad_init_args(self):
        class Bundle(Port):
            x = Port()

        with self.assertRaises(TypeError):
            Bundle("abc")  # type: ignore

    def test_memoization(self):
        @memoize
        class Xyz(jitx.Circuit):
            a = Port()
            b = object()

        x = Xyz()
        y = Xyz()
        assert isinstance(x, Proxy)  # for pyright
        assert isinstance(y, Proxy)  # for pyright
        assert x.b is y.b and x.a is not y.a
        self.assertIsInstance(x, Proxy)
        self.assertIsInstance(x.a, Proxy)
        self.assertIsInstance(y, Proxy)
        self.assertIsInstance(y.a, Proxy)
        self.assertFalse(Proxy.is_tainted(x))
        self.assertFalse(Proxy.is_tainted(y))
        sentinel = object()
        x.z = sentinel
        self.assertTrue(Proxy.is_tainted(x))
        self.assertFalse(Proxy.is_tainted(y))
        self.assertIs(x.z, sentinel)
        with self.assertRaises(AttributeError):
            self.assertIsNot(y.z, sentinel)

    def test_memoize_port(self):
        import jitx.memo
        from jitx._structural import Proxy

        @jitx.memo.memoize
        class PortA(Port):
            a = Port()

        class PortAB(PortA):
            b = Port()

        @jitx.memo.memoize
        class PortArray(Port):
            def __init__(self, n):
                self.array = tuple(Port() for _ in range(n))

        self.assertIsInstance(PortAB(), Proxy)
        self.assertIs(Proxy.forkbase(PortArray(10)), Proxy.forkbase(PortArray(10)))
        self.assertIsNot(Proxy.forkbase(PortArray(11)), Proxy.forkbase(PortArray(12)))
