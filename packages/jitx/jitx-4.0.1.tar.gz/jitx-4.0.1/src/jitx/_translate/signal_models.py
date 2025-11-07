from jitx.si import PinModel

import jitxcore._proto.signal_models_pb2 as spb2


def translate_pin_model(model: PinModel, into: spb2.PinModel):
    into.delay.typ = model.delay.typ
    if model.delay.plus is not None:
        into.delay.tol_plus = model.delay.plus
    if model.delay.minus is not None:
        into.delay.tol_minus = model.delay.minus
    into.loss.typ = model.loss.typ
    if model.loss.plus is not None:
        into.loss.tol_plus = model.loss.plus
    if model.loss.minus is not None:
        into.loss.tol_minus = model.loss.minus
