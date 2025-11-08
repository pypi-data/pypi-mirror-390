from typing import Any
from .idmap import idmap
import jitxcore._proto.file_info_pb2 as fpb2
from jitx.fileinfo import FileInfo

from logging import getLogger

logger = getLogger(__name__)


def translate_file_info(into: fpb2.FileInfo, ob: Any):
    info = FileInfo.get(ob)
    if info:
        into.index = idmap.get_filename_index(info.filename)
        into.line = info.line
        into.column = 0


def translate_file_info_from_class(into: fpb2.FileInfo, ob: Any):
    try:
        import inspect

        if not isinstance(ob, type):
            ob = ob.__class__
        file = inspect.getsourcefile(ob)
        if not file:
            return
        _, line = inspect.getsourcelines(ob)
        into.index = idmap.get_filename_index(file)
        into.line = line
        into.column = 0
    except Exception:
        logger.debug("Could not get source info for %s", ob)
