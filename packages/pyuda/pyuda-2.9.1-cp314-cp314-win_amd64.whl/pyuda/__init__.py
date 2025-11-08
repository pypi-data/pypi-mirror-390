from __future__ import (division, print_function, absolute_import)


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

from logging import DEBUG, WARNING, INFO, ERROR

import cpyuda

from ._client import Client
from ._signal import Signal
from ._video import Video
from ._dim import Dim
from ._structured import StructuredData
from ._json import SignalEncoder, SignalDecoder
from ._version import __version__, __version_info__


UDAException = cpyuda.UDAException
ProtocolException = cpyuda.ProtocolException
ServerException = cpyuda.ServerException
InvalidUseException = cpyuda.InvalidUseException
Properties = cpyuda.Properties


__all__ = ("UDAException", "ProtocolException", "ServerException", "InvalidUseException",
        "Client", "Signal", "Video", "Dim", "Properties", "DEBUG", "WARNING", "INFO", "ERROR")
