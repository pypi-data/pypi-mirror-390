from jitx.circuit import Circuit
from jitx.container import inline
from jitx.error import UserCodeException
from jitx.net import Port
from jitx.sample import SampleDesign
import jitx.test
import jitx._translate.design


class WrapperDesign(SampleDesign):
    def __init__(self, circuit: Circuit):
        self.circuit = circuit


class AliasedPortInCircuit(Circuit):
    port = Port()
    other = [port]


class AliasedPortInSubCircuit(Circuit):
    @inline
    class subcircuit(Circuit):
        port = Port()

    other = subcircuit.port


class TranslationTest(jitx.test.TestCase):
    def test_aliased_port_in_circuit(self):
        with self.assertRaises(UserCodeException):
            jitx._translate.design.package_design(WrapperDesign(AliasedPortInCircuit()))

    def test_aliased_port_in_subcircuit(self):
        with self.assertRaises(UserCodeException):
            jitx._translate.design.package_design(
                WrapperDesign(AliasedPortInSubCircuit())
            )
