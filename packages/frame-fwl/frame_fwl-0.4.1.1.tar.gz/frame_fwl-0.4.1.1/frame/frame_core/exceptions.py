class FramerError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class FrameApiError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class FramingError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class PluginIsNotWorkingError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class PluginError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class FrameExecutionError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class FrameComposeError(Exception):
    def __init__(self, framer_name = '', exception = '', exception_text = ''):
        self.text = f'''\n
Error in [Framer{'_' + str(framer_name) if str(framer_name) else ''}]
=== {exception} ===
{exception_text}
{'=' * (len(exception) + 8)}
'''
        super().__init__(self.text)

