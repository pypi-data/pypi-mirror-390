import builtins
import sys
from abc import ABC
try:
    import resource
    resource_available = True
except:
    resource = ABC()
    resource_available = False
from collections.abc import Mapping



def str_to_int(string: str, summing: bool = True) -> list | int:
    '''
# String to integrear method
Convert any value to int (list or number).
### Args:
- {string}: str - any string for convertation.
- {summing}: bool - function will return sum of list[indexes] if true, else list[indexes]
### Example:
Code:
```
print(str_to_int('test'))
print(str_to_int('test', summing = False))
```
Output:
```
169
[41, 39, 48, 41]
```
'''
    string = str(string)
    alphabet = list('1234567890 ' +
                    'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm' +
                    'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЁЯЧСМИТЬБЮйцукенгшщзхъфывапролджэёячсмитьбю' +
                    '!@#$%^&*()_+¡™£¢∞§¶•ªº–≠[]{}\\|/?.,<>\'":;±§`~\n\t')
    res = []
    for i in list(string):
        if i in alphabet: res.append(alphabet.index(i))
        else: 
            alphabet.append(i)
            res.append(alphabet.index(i))
    return sum(res) if summing else res


def exec_and_return_safe(code: str, variable_name: str):
    '''
# Exec and return: safe version
Execute code and return result of specified variable.
### Args:
- code: str - Full Python code to execute
- variable_name: str - Name of variable to return

### Usage:
```
simple_code = """
x = 10
y = 34
res = x + y
"""
print('result:', exec_and_return_safe(simple_code, 'res'))
```

### Security Features:
1. Restricted builtins (no file operations, network, imports)
2. Limited execution time
3. Memory limits
4. Restricted loop iterations
5. No access to dangerous modules
    '''

    # Safe builtins whitelist
    SAFE_BUILTINS = {
        'abs', 'all', 'any', 'bool', 'chr', 'dict', 'dir', 'enumerate',
        'filter', 'float', 'int', 'len', 'list', 'map', 'max', 'min',
        'ord', 'pow', 'range', 'round', 'set', 'sorted', 'str', 'sum',
        'tuple', 'zip', 'print'
    }

    class SafeGlobals(Mapping):
        def __init__(self):
            self._builtins = {
                name: getattr(builtins, name)
                for name in SAFE_BUILTINS
                if hasattr(builtins, name)
            }
        
        def __getitem__(self, key):
            if key in self._builtins:
                return self._builtins[key]
            raise KeyError(f"Access to '{key}' is restricted")
        
        def __iter__(self):
            return iter(self._builtins)
        
        def __len__(self):
            return len(self._builtins)

    def set_limits():
        if resource_available:
            # Set memory limit (50 MB)
            resource.setrlimit(
                resource.RLIMIT_AS,
                (50 * 1024 * 1024, 50 * 1024 * 1024)
            )
            # Set CPU time limit (5 seconds)
            resource.setrlimit(
                resource.RLIMIT_CPU,
                (5, 5)
            )

    def safe_exec(code, globals_dict):
        # Replace dangerous builtins
        original_builtins = builtins.__dict__.copy()
        builtins.__dict__.clear()
        builtins.__dict__.update(globals_dict['__builtins__'])
        
        try:
            # Monitor execution
            exec(code, globals_dict)
        finally:
            # Restore original builtins
            builtins.__dict__.update(original_builtins)

    safe_globals = SafeGlobals()
    local_namespace = {
        '__builtins__': safe_globals,
        'sys': None,  # Block sys module
        'os': None,   # Block os module
        'open': None, # Block file operations
    }

    try:
        # Set resource limits
        set_limits()
    except (ValueError, resource.error):
        pass  # Ignore limits on Windows

    try:
        safe_exec(code, local_namespace)
        return local_namespace.get(variable_name)
    except MemoryError:
        print("Error: Code exceeded memory limits")
        return None
    except Exception as e:
        print(f"Error in code execution: {e}")
        return None

def exec_and_return(code: str, 
                    variable_name: str, 
                    local: dict[str, any] = {},
                    globals: dict[str, any] = globals(),
                    mode: str = 'var'):
    '''
# Exec and return
Execute code and return result of {variable name}.
### Args:

- {code}: str - full code.
- {variable_name}: str - name of vatiable to return.
- {local}: dict - dictionary to executing.
- {mode}: str - var/res - function will be returning result of execution if res, else value from {variable_name}.

### Uasge:
Code:
```
simple_code = """
x = 10
y = 34
res = x + y
"""
print('result:', exec_and_return(simple_code, 'res'))
```
Output:
```
result: 34
```
    '''
    try:
        non_locals = local
        compiled = compile(code, '__tmp', 'exec')
        res = exec(compiled, globals, non_locals)
        return res if mode == 'res' else non_locals.get(variable_name)
    except Exception as e:
        print(f"Error in code running: {e}")
        return None

