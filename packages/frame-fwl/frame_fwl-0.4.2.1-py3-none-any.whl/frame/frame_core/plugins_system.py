from abc import ABC
from .frames import Frame, exec_and_return, PluginIsNotWorkingError, PluginError
import math, cmath, random, importlib





class PluginBase(ABC):
    def __init__(self, frame: Frame | None = None):
        self.frame = frame
        self._has_frame = isinstance(frame, Frame)
        super().__init__()
        self._dependencies = []
        self._state = {'included': False}
    def work(self):
        '''Main plugin method.'''
        raise PluginIsNotWorkingError
    def include(self):
        '''Include plugin to [Frame] method.'''
        self._check_dependencies()
        if not self._state['included']:
            self.frame: Frame = Frame() if not self._has_frame else self.frame
            self.frame.Code(f'import {", ".join(self._dependencies)}') if self._dependencies is not [] else None
            self._state['included'] = True
    def _set_dependencies(self, deps: list):
        self._dependencies = deps
    def _check_dependencies(self):
        for dep in self._dependencies:
            try: importlib.import_module(dep)
            except ImportError:
                PluginError(f'Dependencies error: {dep} is not installed.')
    def _check(self):
        if not self._state['included']: raise PluginError("Use include method before using operations. \nUse 'plugin.include()'' (example) for include lib.")
    def __call__(self, *args, **kwds):
        return self.frame



class PluginRegistry:
    _plugins = {}
    
    @classmethod
    def register(cls, name, plugin_class):
        cls._plugins[name] = plugin_class
    
    @classmethod
    def get_plugin(cls, name, frame) -> type[PluginRegistry]:
        return cls._plugins[name](frame)
    
    @classmethod
    def list_plugin(cls):
        return cls._plugins

def register_plugin(name):
    def decorator(cls):
        PluginRegistry.register(name, cls)
        return cls
    return decorator

