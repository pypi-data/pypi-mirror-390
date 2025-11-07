from jitx.inspect import decompose, extract
from jitx.stackup import Conductor, Dielectric, Material, Symmetric
from jitx.test import TestCase


class StackupTestCase(TestCase):
    def test_symmetric_stackup(self):
        class Stack(Symmetric):
            surface = Dielectric(thickness=0.1)
            top = Conductor(thickness=0.2)
            core = Dielectric(thickness=0.3)

        stack = Stack()
        layers = tuple(decompose(stack, Material))
        self.assertEqual(len(layers), 5)
        self.assertEqual(
            len([layer for layer in layers if isinstance(layer, Conductor)]), 2
        )
        self.assertIs(stack.top, layers[1])
        self.assertIs(stack.top, layers[3])

        self.assertEqual(len(stack.conductors), 2)
        # ensure the conductors property is not introspected.
        self.assertEqual(sum(1 for _ in extract(stack, Conductor)), 2)
