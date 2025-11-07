# pyright: reportUnnecessaryTypeIgnoreComment=error
# ^ this triggers if an ignore is unnecessary, which indicates that a type
# error _wouldn't_ have been produced on that line; this is to make sure that
# we notice if an expected type-error case goes away.
from jitx import current
from jitx.circuit import Circuit
from jitx.component import Component
from jitx.container import inline
from jitx.copper import Pour
from jitx.landpattern import Landpattern, Pad
from jitx.net import Net, Port, PortArray
from jitx.sample import SampleDesign
from jitx.shapes.composites import rectangle
from jitx.symbol import Symbol, Pin
import jitx.test


# DO NOT REMOVE "type: ignore" IN THIS FILE THEY ARE TESTING TYPE INFERENCE


class NetsTestCase(jitx.test.TestCase):
    def test_net_two_ports(self):
        self.assertIsInstance(Port() + Port(), Net)

    def test_net_two_portarrays(self):
        self.assertIsInstance(PortArray(Port(), 5) + PortArray(Port(), 5), Net)

    def test_net_two_nonidentical_ports(self):
        class PortA(Port):
            a = Port()
            b = Port()

        class PortB(Port):
            a = Port()
            b = Port()

        with self.assertRaises(ValueError):
            # pyright correctly calls out this as an error
            self.assertNotIsInstance(PortA() + PortB(), Net)  # type: ignore

    def test_net_two_incompatible_ports(self):
        class PortA(Port):
            a = Port()
            b = Port()

        class PortB(Port):
            a = Port()
            c = Port()

        class PortC(Port):
            a = Port()

        # pyright correctly calls out these as errors
        with self.assertRaises(ValueError):
            self.assertNotIsInstance(PortA() + PortB(), Net)  # type: ignore
        with self.assertRaises(ValueError):
            self.assertNotIsInstance(PortA() + PortC(), Net)  # type: ignore
        with self.assertRaises(ValueError):
            self.assertNotIsInstance(PortA() + Port(), Net)  # type: ignore

    def test_net_two_incompatible_portarrays(self):
        with self.assertRaises(ValueError):
            # pyright does not recognize these as incompatible, as PortArray is
            # the same type.
            net = PortArray(Port(), 5) + PortArray(Port(), 4)
            self.assertNotIsInstance(net, Net)

    def test_net_append_compatible_port(self):
        net = Net(name="net 1")
        net += Port()
        net += Port()
        self.assertIsInstance(net, Net)
        self.assertEqual(len(net.connected), 2)
        self.assertEqual(net.name, "net 1")

        net = Net([Port()], name="net 2")
        net += Port()
        self.assertIsInstance(net, Net)
        self.assertEqual(len(net.connected), 2)

    def test_net_append_nonidentical_port(self):
        class PortA(Port):
            a = Port()

        class PortB(Port):
            a = Port()

        net = Net(name="net 1")
        net += PortA()
        self.assertIsInstance(net, Net)
        with self.assertRaises(ValueError):
            # pyright does not recognize this, because Net is initialized without a type
            net += PortB()

        net = Net(name="net 1", ports=[PortA()])
        self.assertIsInstance(net, Net)
        with self.assertRaises(ValueError):
            # pyright does recognize this, because Net is initialized with a type
            net += PortB()  # type: ignore

    def test_net_append_incompatible_port(self):
        class PortA(Port):
            a = Port()

        class PortB(Port):
            b = Port()

        net = Net(name="net 1")
        net += PortA()
        self.assertIsInstance(net, Net)
        with self.assertRaises(ValueError):
            net += PortB()


class MyPad(Pad):
    shape = rectangle(1, 1)


class PourTestDesign(SampleDesign):
    @inline
    class circuit(Circuit):
        @inline
        class ComponentA(Component):
            p = Port()

            @inline
            class lp(Landpattern):
                p = MyPad().at(0, 0)

            @inline
            class sym(Symbol):
                p = Pin((0, 0))

        def __init__(self):
            self.net = Net(name="GND")
            self.net += self.ComponentA.p
            self.net += Pour(layer=0, shape=current.design.board.shape, isolate=0.25)
