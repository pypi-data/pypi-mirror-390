'''
# Nets.hack Mocule

Modules - 
    gray - gray hacking.
    white - white hacking.

### !Attention! - The author is not responsible for the user's actions. Only for legal usage.
'''


from .gray import (ClassApi as GrayHackApi)
from .white import (ClassApi as WhiteHackApi)


class HackModuleApi:
    @property
    def white(): return WhiteHackApi()
    @property
    def gray(): return GrayHackApi()
