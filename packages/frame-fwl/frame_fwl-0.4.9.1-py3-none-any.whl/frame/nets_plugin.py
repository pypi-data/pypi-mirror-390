from .nets_core import *
from .frame_core import *


@register_plugin('nets')
class NetsPlugin(PluginBase):
    _dependencies = ['frame']
    def __init__(self, frame = None):
        super().__init__(frame)
        self._state = {'included': False, 'safemode': self.frame._get_safemode()}
        self._version = 'v0.1.1'
        self._counter = 0
    def include(self):
        super().include()
        return self
    def work(self):
        return f'netsplugin <{self._version}>'
