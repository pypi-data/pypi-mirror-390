'''
# Framing Concept Core
The Frames - multitool programming paradigm.


### Modules:
    - exceptions - exceptions of frames.
    - frames - main file of lib.
    - funcs - other functions file.
    - plugin_system - plugin base.
    - plugins - official plugins.


### Functions: 
    #### Framer functions -
        Frame (keyclass), FramesComposer, Framer, fExec, fGet, fVar, fSys, fOp, fReturn, fCode, @framing, 
        framing_result
    #### Plugin functions - 
        PluginBase (metaclass), PluginRegistry (keyclass), MathPlugin, register_plugin
    #### Other functions - 
        exec_and_return_safe (keyfunction), exec_and_return, str_to_int
    #### Errors - 
        FrameApiError, FramerError, FramingError, FrameExecutionError, PluginError, 
        PluginIsNotWorkingError

### Main terms - 
    - Frame - An isolated execution space with its own variables and code. Can interact with other contexts.
    - Framing - creating a local environment with superglobal variables.
    - Superglobal is the state of an object when it does not depend on the context. Roughly speaking, a global frame.
    - Framefile is a binary frame image that can be saved and loaded.
    - fcomp iso - Frames composition file

### Warning: 
Main clases of frame (like [Framer], for example) using eval/compile/exec. 

If you want to protect your porgram (full off exec), you can use {safemode} in Frame.

Not for web development.
'''

from .frames import (Framer, Frame, Exec as fExec, Get as fGet, Var as fVar, 
                System as fSys, SystemOP as fOp, Return as fReturn, Code as fCode)
from .composer import (FramesComposer)
from .funcs import (str_to_int, exec_and_return_safe, exec_and_return)
from .exceptions import (FrameApiError, FrameExecutionError, FramerError, FramingError, 
                        PluginError, PluginIsNotWorkingError)

_framecore_version_ = '0.4.12'

def framing(
    framer: str | Framer = 'new',
    name_of_result_variable: str = 'res',
    return_frame: bool = False
    ):
    '''
## Frame decorator
### Args: 
arg {framer}:  object[Frame] | str = 'new' -

- Frame to load {name_of_result_variable}. 
- If == 'new', will be created new frame.
    
arg {name_of_result_variable}:  str = 'res' -
- Variable that will be created in {framer}.
    
arg {return_frame}:  bool = False -
- Args for choise create 'frame' variable (Frame object named `frame`) in System.frames['temp'].
### Examples:
#### First code example: 
```
@framing(return_frame=True)
def test():
    print('test')
    return 10
# geting frame object from decorator
res_frame = fGet('frame', fSys.framers['temp']) 
print(test(), res_frame)
# geting result variable from decorator
print(fGet('res', res_frame))
# or just
# print(framing_result(res_frame, test))
```
Output:
```
test
10 <frame.op.Framer object at 0x10ddf3d10>
10
```
#### Second code example: 
```
ctx = Frame()
@framing(ctx(), return_frame=True)
def test():
    print('test')
    return 10
print(framing_result(ctx, test))
```
Output:
```
test
10
```
    '''
    if framer == 'new': framer_obj = Framer()
    else: framer_obj = framer
    def decorator(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            fVar(name_of_result_variable, res, framer=framer_obj)
            return res
        return wrapper
    if return_frame: fVar('frame', framer_obj, to_repr=False, framer=fSys.framers['temp'])
    return decorator


    
def framing_result(framer: Framer, func: object, name_of_result_variable: str = 'res', *func_args, **func_kwargs):
    '''
## Getting result from [@framing def ...] function
### Args:
- framer: object[Frame] -  framer to run.
- func: object - function for runing.
- name_of_result_variable: str - name_of_result_variable from decorator @framing.
- *args & **kwargs - arguments for [func] running.
### Example:
change 
```
# geting frame object from decorator
res_frame = fGet('frame', fSys.framers['temp'])
# runing 
print(test(), res_frame)
# geting result variable from decorator
print(fGet('res', res_frame))
```
to just
```
print(framing_result(fGet('frame', fSys.framers['temp']), test, 'res'))
```
    '''
    if isinstance(framer, Frame): framer = framer.framer
    resf = func(*func_args, **func_kwargs)
    resg = fGet(name_of_result_variable, framer)
    if resf != resg: raise FramingError(f'Variable [{name_of_result_variable}] is not found in Frame[{framer}].')
    return resg

def open_and_run(filename: str = 'ctx.json', 
                 format: str = 'json', 
                 name_of_result_var: str = 'res',
                 returning_format: str = 'result', 
                 exec_method: str = 'basic') -> any | Frame:
    '{returning_format} - result/frame \n\n{exec_method} - basic/safe'
    if returning_format == 'result':
        with Frame().load(filename, format) as f: 
            code = f.compile()
            res = exec_and_return(code, name_of_result_var) if exec_method == 'basic' else exec_and_return_safe(code, name_of_result_var)
    else: res = Frame().load(filename, format)
    return res

def save_code_to_bin(filename: str = 'ctx.json', 
                     output_file: str = 'bin.py',
                     format: str = 'json'):
    opened = open_and_run(filename, format, returning_format='frame')
    code = opened.compile()
    with open(output_file, 'w') as file: file.write(code)
    return code


from .plugins_system import (PluginBase, PluginRegistry, register_plugin)
from .plugins import (MathPlugin)