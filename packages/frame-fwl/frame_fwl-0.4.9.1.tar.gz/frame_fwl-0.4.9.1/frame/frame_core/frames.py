
import threading
import pickle
import json
from typing import Dict, Any
from .exceptions import *
from .funcs import exec_and_return, str_to_int
import ast, inspect


class _CodeGenerator:
    '''Basic system engine for code generation.'''
    def __init__(self):
        self._code = []
        self._cache = 0
    def _new_line(self, text: str): 
        self._code.append(text)
        self._cache += 1
        return self
    def _gen_temp_var(self, k: int = 0):
        var_name = f'__tmp_{self._cache - k}'
        self._cache += 1
        return var_name
    def _gen_id(self, k: int = 0):
        id = f'_id{len(self._code)+self._cache+k}{self._cache * (k+1)}{k}'
        self._cache += 1
        return id
    def _comentary(self, *args):
        self._new_line(f'"""{"\n".join(args)}"""')


class Framer(_CodeGenerator):
    '''
# Framer

Main context manager class: Framer.

For system.
    '''
    def __init__(self):
        super().__init__()
        self._vars = {}
        self._aliases = {}
        self._types = {}
        self._lock = threading.RLock()
        self._new_code_line = self._new_line
    
    def var(self, name:str, value):
        self._vars[name] = value
        return self

    def op(self, a, b, 
           operator: str = '+'):
        result_var = self._gen_temp_var()
        res = f'{a} {operator} {b}'
        code_line = f'{result_var} = {res}'
        self._code.append(code_line)
        return result_var
    
    def execute(self):
        try:
            final_code = "\n".join(self._code)
            local_scope = self._vars.copy()
            compiled = compile(final_code, '<string>', 'exec')
            exec(compiled, {}, local_scope)
            return_var = "__frame_return_value"
            return local_scope.get(return_var) 
        except Exception as e:
            raise FrameExecutionError(f"Error in frame execution: {e}\nCode:\n{final_code}")
    
    def get_thread_safe(self, name):
        with self._lock: return self._vars.get(self._aliases[name])

    def __enter__(self):
        System.last_framer = System.framer
        System.framer = self
        return self
    def __exit__(self, *args, **kwargs): pass




class SystemClass:
    '''
# System

System context class: System.

Has main [{framer}: Framer], [{last_framer}: Framer] and [{framers}: dict] self parameters.

For system.'''
    def __init__(self):
        self.framer = Framer()
        self.last_framer = self.framer
        self.framers = {'basic': Framer(), 'temp': Framer()}
    
    @classmethod
    def get_global(cls):
        if not hasattr(cls, '_global'):
            cls._global = cls()
        return cls._global

System = SystemClass().get_global()

class SystemOP:
    '''
    # System operations
    Basic simple api for [System] and [Framer].
    '''
    def match(condition: str, 
              true_block: str, 
              false_block: str = None, 
              framer: Framer | None = None):
        framer = System.framer if framer == None else framer
        framer._comentary('condition block', condition)
        cache = framer._gen_id(len(framer._aliases) + len(framer._code))
        Var(f'__condition_temp{cache}', condition, with_eval=True, framer=framer)
        framer._new_code_line(f'if __condition_temp{cache}:')
        new_true_block = ''
        for i in true_block.split('\n'):
            if i.strip() != '': new_true_block += '\n    ' + i
        framer._new_code_line(f'    {new_true_block}')
        if false_block:
            framer._new_code_line('else:')
            new_false_block = ''
            for i in false_block.split('\n'):
                if i.strip() != '': new_false_block += '\n    ' + i
            framer._new_code_line(f'    {new_false_block}')
    def to_last():
        s = System.framer
        System.framer = System.last_framer
        System.last_framer = s


class Var:
    '''
# Variable

Abstraction api class for [Framer] and [System].

### Args:

- {name}: str - name of variable.
- {value}: Any - value of variable.
- {type}: str - type hint for debug in code.
- {to_repr}: bool - if true, value in variable will be repr(value).
- {with_eval}: bool - if true, value in variable will be ```f'eval({repr(value)})'```.
- {framer}: Framer | None - Framer object.
- {check_for_constant}: bool - check is variable constant if true


### Example: 
```
ctx = Framer() # creating context
Var('x', 10, framer = ctx) # setting variable
```
'''
    def __init__(self, 
                 name: str, 
                 value, 
                 type: str = 'int', 
                 to_repr: bool = True, 
                 with_eval: bool = False,
                 framer: Framer | None | str = 'System',
                 check_for_constant: bool = True):
        framer: Framer = Framer() if framer == None else System.framer if isinstance(framer, str) and framer.lower().strip() == 'system' else framer
        param_name = framer._gen_temp_var()
        self.name = param_name
        self.value = value
        to_repr = True if with_eval else to_repr
        val = repr(value) if to_repr else value
        val = f'eval({val})' if with_eval else val
        with framer._lock:
            if name in framer._types and check_for_constant:
                if framer._types[name] == 'const':
                    raise VariableTypeError(f'Variable already declared with type [{type}]. It cannot be overwritten.')
            framer.var(param_name, value)
            framer._types[name] = type
            type = type.replace("const", "int")
            framer._new_line(f'{name}: {type} = {val}')
            framer._aliases[name] = param_name
        self.framer = framer
def Get(name: str, 
        framer: Framer | None | str = 'System'):
    '''Get variable by {name} from {framer} method.'''
    framer: Framer = Framer() if framer == None else System.framer if isinstance(framer, str) and framer.lower().strip() == 'system' else framer
    return framer.get_thread_safe(name)

class Return:
    '''
# Return
 
Method to set variable to return with Exec() method.

### Args: 
- {value}: Var - Variable for return (object).
- {framer}: Framer | None - Framer object.

### Example: 
Code:
```
with Frame() as f: # creating context
    # setting variables
    x = Var('x', 10)
    y = Var('y', 50)
    res = Var('test', Get('x') * Get('y')) 
    Return(res) # setting variable to return
print('result:', Exec()) # executing code
```
Output:
```
result: 500
```'''
    def __init__(self, 
                 value: Var, 
                 framer: Framer | None | str = 'System'):
        framer: Framer = Framer() if framer == None else System.framer if isinstance(framer, str) and framer.lower().strip() == 'system' else framer
        return_var = "__frame_return_value"
        try: framer.var(return_var, f'{framer._vars.get(value.name)}')
        except AttributeError:
            raise FramerError(f'Exception in atribute parsing. \nObject [{value}, {type(value)}] has no atribute .name to create return. \nPlease, use [value] declaration like [`res = Var(...); Return(res, ...)`].')
        self.framer = framer
class Code:
    '''
# Code append

Method to append code in Framer.

### Args:
- {code}: str - code for paste to framer.
- {framer}: Framer | None - framer object.

### Example:
Code:
```
with Frame() as f:
    x = Var('x', 10)
    y = Var('y', 50)
    Code('result = x + y')
    Var('test', Get('x') * Get('y')) 
    Var('res', 'test + result', with_eval=True)
print('result:', exec_and_return(f.compile(), 'res'))
```
Output:
```
result: 560
```'''
    def __init__(self, 
                 code: str, 
                 framer: Framer | None | str = 'System'):
        framer: Framer = Framer() if framer == None else System.framer if isinstance(framer, str) and framer.lower().strip() == 'system' else framer
        framer._new_code_line(code)
        self._code = code
        self.framer = framer

def Exec(framer: Framer | None | str = 'System'):
    '''
Execution of [Frame] method.
    '''
    framer: Framer = Framer() if framer == None else System.framer if isinstance(framer, str) and framer.lower().strip() == 'system' else framer
    with framer._lock:
        return framer.execute()
    
class Frame:
    '''
# Frame
Abstraction api for all [Framer] and [System] methods.

(framer in functions is Frame.framer)

You can use with to create context, and call [Frame] object like `ctx()` to get framer.

### Args of initialization:
- {framer}: str | Framer = 'new' - framer context object for frame.
- {safemode}: bool - if safemode true, Exec method will be is not available.
- {name}: str - framer name in [System.framers]
- {save_while_exit}: bool - if true, while will be called [__exit__], context will be automaticly saved.
- {save_args}: list - list of args [name, format] for method save.

### Example usage:
Code:
```
with Frame(safemode=False) as f:
    f.Var('x', 10)
    f.Var('y', 50)
    SystemOP.match('x > y', 'print("x bigger")', 'print("y bigger")')
    f.Var('test', Get('x') * Get('y')) 
code = f.compile()
print('result:', exec_and_return(code, 'test'))
```
Output:
```
y bigger
result: 500
```'''
    def __init__(self, 
                 framer: str | Framer = 'new', 
                 safemode: bool = True, 
                 name: str = 'f1',
                 save_while_exit: bool = False,
                 save_args: list = ['ctx', 'pickle']):
        self.__saving = [save_while_exit, save_args]
        self.framer: Framer = Framer() if framer == 'new' else framer
        self.__safemode = safemode
        self._name = name
        System.framers[name] = self.framer
    def Sys(self) -> SystemOP: 
        '''Return [System] class.'''
        return SystemOP
    def System(self) -> SystemClass: 
        '''Return [System] class.'''
        return System
    def set_System(self, new_sys: SystemClass = SystemClass()) -> SystemClass:
        global System
        System = new_sys
    def Var(self, 
            name: str, 
            value, 
            type: str = 'int', 
            to_repr: bool = True,
            with_eval: bool = False,
            check_for_constant: bool = False) -> Var:
        '''Creating variable.'''
        return Var(name = name, 
                   value = value, 
                   type = type, 
                   to_repr = to_repr, 
                   with_eval = with_eval, 
                   framer = self.framer, 
                   check_for_constant = check_for_constant)
    def Get(self, name: str) -> Any: 
        '''Get variable by name.'''
        return Get(name, self.framer)
    def Return(self, name: Var) -> Return: 
        '''Set of variable to return.'''
        return Return(name, self.framer)
    def Code(self, code: str, comentary: bool = True, *comentaries) -> Code:
        '''Append code to frame.'''
        if comentary:
            self.framer._comentary('code section', f'Framer: {self._name}', f'Safemode: {self.__safemode}', *comentaries)
        return Code(code, self.framer)
    def Exec(self) -> Any:
        '''Executing code of frame.'''
        if not self.__safemode: return Exec(self.framer)
        else: raise FrameApiError('Exec is not avialable in safemode.')
    def compile(self) -> str: 
        '''Get full code of frame.'''
        return '\n'.join(self.framer._code)
    def reset(self) -> Frame: 
        '''Recreate framer.'''
        self.framer = Framer()
        return self
    def register(self, name: str = None):
        def decorator(func):
            func_name = name or func.__name__
            try:
                source_code = inspect.getsource(func)
                lines = source_code.split('\n')[1:]
                tabbed = False
                can_edit_tabs = True
                tabs = 0
                cleaned_code = []
                for i in lines:
                    if i.startswith('   '): 
                        t = 0
                        for local_i in i: 
                            if local_i == ' ':
                                t += 1
                            if t % 4 == 0: 
                                if can_edit_tabs: tabs = t/4
                            tabbed = True
                        can_edit_tabs = False
                    if not i.startswith('   '): tabbed = False; can_edit_tabs = False
                    if tabbed: 
                        tabs_c = int(4 * tabs)
                        cleaned_code.append(i[tabs_c:])
                    else: 
                        cleaned_code.append(i)
                cleaned_code = '\n'.join(cleaned_code)
                type = cleaned_code.split(" ")[0]
                self.Code(f"\n# Registred construction: {type} {func_name}\n{cleaned_code}", True, f'Registring [{type} {func_name}] construcntion.')
            except Exception as e:
                print(f"Warning: Could not register source code for {func_name}: \n{e}")
                self.Var(func_name, func, to_repr=False)
            return func
        return decorator
    def save(self, filename: str, format: str = 'pickle') -> Frame:
        '''
        ## Saving frame to file.
        ### Args:
            {filename}: str - file name
            {format}: str - saving format ('pickle' or 'json')
        '''
        data = self.data
        try:
            if format == 'pickle':
                with open(filename, 'wb') as f: pickle.dump(data, f)
            elif format == 'json':
                json_data = self._serealize('json')
                with open(filename, 'w', encoding='utf-8') as f: 
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
            else: raise FrameApiError(f"Unsupported format: {format}")
            return self
        except Exception as e:
            raise FrameApiError(f"Save failed: {e}")

    def load(self, filename: str = 'ctx', format: str = 'pickle', local_safemode: bool = True) -> Frame:
        '''
        ## Loading frame from file.
        ### Args:
            {filename}: str - file name
            {format}: str - loading format ('pickle' or 'json')
        '''
        try:
            if format == 'pickle':
                with open(filename, 'rb') as f: data = pickle.load(f)
            elif format == 'json':
                with open(filename, 'r', encoding='utf-8') as f: data = json.load(f)
                restored_vars = {}
                for k, v in data['framer']['_vars'].items():
                    try: restored_vars[k] = ast.literal_eval(v)
                    except: 
                        try:
                            if not self.__safemode or not local_safemode: 
                                restored_vars[k] = eval(v)
                            else: restored_vars[k] = v
                        except Exception as e: 
                            raise FrameApiError(f'Error in parsing parameters: {e}')
                data['framer']['_vars'] = restored_vars
            else: raise FrameApiError(f"Unsupported format: {format}")
            self._load_data(data)
            return self
        except Exception as e:
            raise FrameApiError(f"Load failed: {e}")
    @property
    def data(self):
        return {
                'framer': {
                    '_code': self.framer._code,
                    '_vars': self.framer._vars,
                    '_aliases': self.framer._aliases,
                    '_types': self.framer._types
                },
                'saving': self.__saving,
                'safemode': self.__safemode,
                'name': self._name
                }

    def _serealize(self, form: str = 'pickle' ):
        data = self.data
        json_data = {
            'framer': {
                '_code': data['framer']['_code'],
                '_vars': {k: str(v) for k, v in data['framer']['_vars'].items()},  # Приводим к строке для JSON
                '_aliases': data['framer']['_aliases'],
                '_types': data['framer']['_types']
            },
            'safemode': data['safemode'],
            'saving': data['saving'],
            'name': data['name']
        }
        return data if form == 'pickle' else json_data
    def _load_data(self, data: dict):
        self.framer._code = data['framer']['_code']
        self.framer._vars = data['framer']['_vars'] 
        self.framer._aliases = data['framer']['_aliases']
        self.framer._types = data['framer']['_types']
        self.__safemode = data['safemode']
        self.__saving = data['saving']
        self._name = data['name']
        return self
    def _get_safemode(self): return self.__safemode
    def __enter__(self): 
        self.framer.__enter__()
        return self
    def __exit__(self, *args, **kwargs): 
        if self.__saving[0]: self.save(*self.__saving[1])
    def __call__(self, *args, **kwds):
        return self.framer
    def __getitem__(self, index):
        return self.Get(index)





Var('name', 'frame', framer=System.framers['basic'])

if __name__ == '__main__':
    with Frame() as f:
        x = Var('x', 10)
        y = Var('y', 50)
        SystemOP.match('x > y', 'print("x bigger")', 'print("y bigger")')
        res = Var('test', Get('x') * Get('y')) 
        Return(res)  
    print(Exec())  # → 500
    with Frame() as f:
        x = Var('x', 10)
        y = Var('y', 50)
        res = Var('res', 'x + y', with_eval=True)
        Return(res)
    print(Exec())
    code = f.compile()
    print(exec_and_return(code, 'res')) # 60
    with Frame() as f:
        x = Var('x', 10)
        y = Var('y', 50)
        Code('result = x + y')
        Var('test', Get('x') * Get('y')) 
        Var('res', 'test + result', with_eval=True)
    print(exec_and_return(f.compile(), 'res')) # 560
    with Frame(save_while_exit=True, save_args=['ctx.json', 'json']) as f:
        f.Var('x', 10)
        f.Var('y', 50)
        SystemOP.match('x > y', 'print("x bigger")', 'print("y bigger")')
        f.Var('test', Get('x') * Get('y')) 
        print(f['test'], '========')
        @f.register()
        def test(): 
            print('testing')
        @f.register()
        class Test():
            hello = 'World'
            pass
    with Frame().load('ctx.json', format='json') as f:
        code = f.compile()
        print('result:', exec_and_return(code, 'test'))
    print('\n\n======= CODE =======')
    print(code)
    '''
y bigger
500
x + y
60
560
500 ========
y bigger
result: <function test at 0x10622da60>
test1
f1
<__main__.Frame object at 0x1061fc380>, test, sgc, 6585, False
6585


======= CODE =======
x: int = 10
y: int = 50
"""condition block
x > y"""
__condition_temp_id13305: int = eval('x > y')
if __condition_temp_id13305:
    
    print("x bigger")
else:
    
    print("y bigger")
test: int = 500
"""code section
Framer: f1
Safemode: True
Registring [def test] construcntion."""

# Registred construction: def test
def test(): 
    print('testing')

"""code section
Framer: f1
Safemode: True
Registring [class Test] construcntion."""

# Registred construction: class Test
class Test():
    hello = 'World'
    pass
'''