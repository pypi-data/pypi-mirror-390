from .frames import *
from .plugins import MathPlugin



class FramesComposer:
    '''
# FramesComposer
    '''
    def __init__(self, safemode: bool = False, arch: str = 'dict', superglobal_name: str = 'sgc'):
        'arch - dict/array (array is VERY experemental)'
        framer = 'new' 
        self.__safemode = safemode
        save_while_exit = False
        save_args = ['ctx', 'pickle']
        self._superglobal_name = superglobal_name
        self.sgc = Frame(framer, self.__safemode, superglobal_name, save_while_exit, save_args) # superglobal context
        self._frames: list[Frame] | dict[str, Frame] = {} if arch == 'dict' else []
        self._arch = arch
        self._deps = []
        self.__temp_names = []
    def load_frame(self, 
                   index: str | int, 
                   frame: Frame, 
                   add_to_deps: bool = True) -> FramesComposer:
        self.__temp_names.append(index)
        self._deps.append(index) if add_to_deps else None
        if self._arch == 'dict': self._frames[index] = frame
        else: 
            pre = self._frames[:index-1]
            after = self._frames[index:]
            _frames = pre + [frame] + after
            self._frames = _frames
        return self
    def check_deps(self):
        for i in self._deps: 
            if i not in self.__temp_names:
                raise FrameComposeError(i, 'FRAME NOT FOUND', f'Dependency is not found: [{i}].')
    def get_frame(self, index: str | int) -> Frame:
        try: return self._frames[int(index) if self._arch == 'array' else index]
        except (IndexError, KeyError) as e: raise FrameComposeError(index, 'GetFrameError', e)
    def sync(self, name_1: str, name_2: str) -> FramesComposer:
        if name_1 not in ('$', 'sgc'):
            f1 = self._frames[name_1]  
        else: f1 =  self.sgc
        if name_2 not in ('$', 'sgc'):
            f2 = self._frames[name_2]
        else: f2 = self.sgc
        new_dict1 = {}
        for i in f1.framer._aliases: 
            new_dict1[i] = f1.framer._aliases[i]
        for i in f2.framer._aliases: 
            new_dict1[i] = f2.framer._aliases[i]
        f1.framer._aliases = new_dict1
        f2.framer._aliases = new_dict1
        new_dict2 = {}
        for i in f1.framer._vars: 
            new_dict2[i] = f1.framer._vars[i]
        for i in f2.framer._vars: 
            new_dict2[i] = f2.framer._vars[i]
        f1.framer._vars = new_dict2
        f2.framer._vars = new_dict2
        if name_1 not in ('$', 'sgc'): self._frames[name_1] = f1
        else: self.sgc = f1
        if name_2 not in ('$', 'sgc'): self._frames[name_2] = f2
        else: self.sgc = f2
        return self
    def superglobal(self) -> Framer: return self.sgc
    def _data(self):
        data = {'_frames': {}}
        data['_superglobal_name'] = self._superglobal_name
        data['_arch'] = self._arch
        data['_deps'] = self._deps
        data['__safemode'] = self.__safemode
        data['sgc'] = self.sgc.data
        for i in self._frames.keys(): 
            data['_frames'][i] = self._frames[i].data
        return data
    def _load_data(self, data: dict):
        """Load data into existing FramesComposer instance"""
        self._superglobal_name = data['_superglobal_name']
        self._arch = data['_arch']
        self._deps = data['_deps']
        self.__safemode = data['__safemode']
        
        # Load superglobal context
        self.sgc._load_data(data['sgc'])
        
        # Clear current frames
        self._frames = {} if self._arch == 'dict' else []
        
        # Load all frames
        if isinstance(data['_frames'], dict): fr = data['_frames'].items()
        elif isinstance(data['_frames'], list): fr = data['_frames']
        else:
            raise FrameComposeError('', 'UNKNOWN TYPE TO LOAD', 'Unknown arch for load fcomp file.')
        for frame_name, frame_data in fr:
            frame = Frame()
            frame._load_data(frame_data)
            self.load_frame(frame_name, frame)
    def save(self, filename, format: str = 'json'):
        '''
        ## Saving FramesComposer to file.
        ### Args:
            {filename}: str - file name
            {format}: str - saving format ('pickle' or 'json')
        '''
        data = self._data()
        try:
            if format == 'pickle':
                with open(filename, 'wb') as f: 
                    pickle.dump(data, f)
            elif format == 'json':
                with open(filename, 'w', encoding='utf-8') as f: 
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else: 
                raise FrameApiError(f"Unsupported format: {format}")
            return self
        except Exception as e:
            raise FrameApiError(f"Save failed: {e}")
    def load(self, filename: str, format: str = 'json') -> 'FramesComposer':
        '''
        ## Loading FramesComposer from file.
        ### Args:
            {filename}: str - file name  
            {format}: str - loading format ('pickle' or 'json')
        ### Returns:
            FramesComposer: self for method chaining
        '''
        try:
            if format == 'pickle':
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
            elif format == 'json':
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                raise FrameApiError(f"Unsupported format: {format}")
            
            self._load_data(data)
            return self
            
        except FileNotFoundError:
            raise FrameApiError(f"File not found: {filename}")
        except Exception as e:
            raise FrameApiError(f"Load failed: {e}")
    @classmethod
    def from_file(cls, filename: str, format: str = 'json') -> 'FramesComposer':
        '''
        ## Create FramesComposer from file (class method)
        ### Args:
            {filename}: str - file name
            {format}: str - loading format ('pickle' or 'json')
        ### Returns:
            FramesComposer: new instance loaded from file
        '''
        composer = cls()
        composer.load(filename, format)
        return composer
    def test_exec(self) -> 'FramesComposer':
        self.check_deps()
        if self.__safemode:
            raise FrameComposeError(f'Superglobal Context [{self._superglobal_name}]', 'EXEC ERROR',
            'Execution is imposible in safemode.')
        self.sgc.Exec()
        return self
    def __enter__(self) -> FramesComposer: return self
    def __exit__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwds) -> Frame: return self.superglobal()
    def __add__(self, other: Frame) -> None: 
        if isinstance(other, Frame): self.load_frame(len(self._frames) if self._arch == 'array' else other._name, other)
        else: raise FrameComposeError('', 'NotSuuportableObject', f"Inncorect attemp to add {type(other)} object to frames.")
    def __getitem__(self, index) -> Frame:
        try: return self._frames[index]
        except (IndexError, KeyError) as e: raise FrameComposeError(index, 'GetFrameError', f'Unknown key: {e}')
        except Exception as e: raise FrameComposeError(index, 'GetItemError', e)
    def __setitem__(self, index, value):
        try: self.load_frame(index, value)
        except (IndexError, KeyError) as e: raise FrameComposeError(index, 'GetFrameError', f'Unknown key: {e}')
        except Exception as e: raise FrameComposeError(index, 'SetItemError', e)
    def __eq__(self, value) -> bool:
        if isinstance(value, FramesComposer): 
            cond1 = value.__safemode == self.__safemode and value._arch == self._arch
            cond2 = value.sgc._name == self.sgc._name  and value._superglobal_name == self._superglobal_name
            return cond1 and cond2
        else: return False
    def __format__(self, format_spec: str) -> str:
        if format_spec == '.all': return str(self._frames)
        elif format_spec.startswith('.get>'):
            index = format_spec[5:]
            list = {}
            counter = 0
            for i in self._frames: 
                list[str(counter)] = self._frames[i]
                counter += 1
            try: return str(list[str(index)])
            except (KeyError) as e: 
                raise FrameComposeError(f'index<{index}>', 'GetItemError', f'Unknown key: {e}')
            except Exception as e: raise FrameComposeError(index, 'fStringError', e)
        elif format_spec.startswith('.getname>'):
            index = format_spec[9:]
            list = {}
            counter = 0
            for i in self._frames: 
                list[str(counter)] = i
                counter += 1
            try: return list[str(index)]
            except (KeyError) as e: 
                raise FrameComposeError(f'index<{index}>', 'GetItemError', f'Unknown key: {e}')
            except Exception as e: raise FrameComposeError(index, 'fStringError', e)
        elif format_spec.startswith('.safemode'):
            return str(self.__safemode)
        elif format_spec.startswith('.hash'):
            return str(self.__hash__())
        elif format_spec.startswith(('.sgc', '.superglobal', '.sgcname')): 
            return self.sgc._name
        elif format_spec.startswith(('.arch', '.a')): 
            return self._arch
        raise ValueError('Unknown format option.')
    def __hash__(self) -> int:
        arch = str_to_int(self._arch)
        frames = str_to_int(self._frames)
        safemode = str_to_int(self.__safemode)
        superglobal = str_to_int(self._superglobal_name)
        return arch+frames+safemode+superglobal
    def __int__(self):
        return self.__hash__()



if __name__ == '__main__':
    filename = 'fc'
    format = 'json'
    filepath = f'{filename}.{format}'
    with FramesComposer(safemode=False) as fc:
        fc['test1'] = Frame(safemode=False)
        fc['test2'] = Frame(safemode=False)
        @fc['test2'].register()
        def test():
            return 'compleate'
        with fc['test2'] as f:
            f.Var('x', 10)
            f.Var('y', 50)
            SystemOP.match('x > y', 'print("x bigger")', 'print("y bigger")')
            f.Var('test', Get('x') * Get('y')) 
            @f.register()
            def test(): 
                print('testing')
            @f.register()
            class Test():
                hello = 'World'
                pass
        @fc['test1'].register()
        def test():
            return 'compleate'
        mfc = MathPlugin(fc['test1']).include()
        mfc.discriminant(10, 20, 30)
        mfc.discriminant(20, 20, 80)
        fc.sync('test1', '$')
        fc.sync('test2', '$')
        fc.save(filepath, format)
    with FramesComposer.from_file(filepath, format) as fc:
        fc.test_exec()