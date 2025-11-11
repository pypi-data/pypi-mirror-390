'''
# Simple Frames Core
Simplified module of frame concept for beginers.
'''


from .frame_core import (Frame, Framer, framing, framing_result, fExec, fGet, fVar, fSys)
from .frame_core.exceptions import *
from .frame_core.plugins import (MathPlugin)
from .frame_core.plugins_system import(PluginBase, PluginRegistry, register_plugin)