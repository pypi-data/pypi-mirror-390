from .plugins_system import *

@register_plugin('math')
class MathPlugin(PluginBase):
    '''
    # Math Plugin
    Oficial math plugin for Frame's. 
    
    You have to run `include` method before using Plugin.
    
    Argument {framer}: Framer | None - frame context to using lib (only without safemode)'''
    def __init__(self, frame = None):
        super().__init__(frame)
        self._set_dependencies(['math', 'cmath'])
        self._state = {'included': False, 'safemode': self.frame._get_safemode()}
        self._version = 'v0.1.1'
        self._counter = 0
    
    def work(self):
        return f'mathplugin <{self._version}>'
    
    def include(self):
        if not self._state['included']:
            super().include()
            std = '''
classic_sum = sum
def sum(n):
    try: return classic_sum(n)
    except Exception as e:
        if 'debug' in locals().keys() or 'debug' in globals().keys() and debug == True: 
            print(f'Summing error: {e}')
        return n
'''
            self.frame.Code(std)
            self.frame.Code(f'\n_math_plugin_ver = {repr(self._version)}')
        return self
    
    def parabola(self, x: int | float, 
                 name_of_result_variable: str = 'res', 
                 returning: str = 'frame'): 
        '{returning} - frame / Code'
        return self._operand(x, name_of_result_variable, returning, op='$ ** 2', name='parabola')
    
    def sigmoid(self, x: int | float, 
                 name_of_result_variable: str = 'res', 
                 returning: str = 'frame'): 
        '{returning} - frame / Code'
        return self._operand(x, name_of_result_variable, returning, 
                             op='1 / (1 + math.exp(-$)) if isinstance($, (int, float)) else [1 / (1 + math.exp(-i)) for i in $]',
                             name='sigmoid')

    def softmax(self, x: int | float, 
                 name_of_result_variable: str = 'res', 
                 returning: str = 'frame'): 
        '{returning} - frame / Code'
        self.frame.Code(f'"""\nsoftmax\nReturning: {returning}\nName of result var: {name_of_result_variable}\nInputs: {x}"""')
        self._check()
        cache = self._cache()
        name = f'__temp_inp_math{cache}'
        self.frame.Var(name, str(x), with_eval=True)
        code = f'''
__condition{cache} = isinstance({name}, (int, float))
if __condition{cache}:
    {name_of_result_variable} = 1.0
else:
    __temp_exp_values{cache} = [math.exp(i - max({name})) for i in {name}]
    __temp_exp_sum{cache} = sum(__temp_exp_values{cache})
    {name_of_result_variable} = [i / __temp_exp_sum{cache} for i in __temp_exp_values{cache}]
'''
        code = self.frame.Code(code)
        return code if returning.lower().strip() == 'code' else self
    
    def sqrt(self, x: int | float, 
             name_of_result_variable: str = 'res', 
             returning: str = 'frame'): 
        '{returning} - frame / Code'
        return self._operand(x, name_of_result_variable, returning, op='math.sqrt($)', name='sqrt')
    
    def relu(self, x: int | float, 
             name_of_result_variable: str = 'res', 
             returning: str = 'frame'):
        '{returning} - frame / Code'
        return self._operand(x, name_of_result_variable, returning, op='1 if abs($) != $ else $', name='relu')
    
    def discriminant(self, a: int | float, b: int | float, c: int | float, 
                     name_of_result_variable: str = 'res', 
                     returning: str = 'frame') -> 'Frame.Code' | MathPlugin:
        '{returning} - frame / Code. \n\nValue of {name_of_result_variable} in code will be list[x1, x2, discriminant].'
        self.frame.Code(f'"""\ndiscriminant\nReturning: {returning}\nName of result var: {name_of_result_variable}\nInputs: {[a, b, c]}"""')
        self._check()
        cache = self._cache()
        self.frame.Var(f'__temp_a_math{cache}', str(a), with_eval=True)
        self.frame.Var(f'__temp_b_math{cache}', str(b), with_eval=True)
        self.frame.Var(f'__temp_c_math{cache}', str(c), with_eval=True)
        code = f'''
if __temp_a_math{cache} == 0: __temp_a_math{cache} += 1
__temp_D_math{cache} = (__temp_b_math{cache} ** 2) - (4 * __temp_a_math{cache} * __temp_c_math{cache})
if __temp_D_math{cache} >= 0: __temp_sqrt_D_math{cache} = math.sqrt(__temp_D_math{cache})
else: __temp_sqrt_D_math{cache} = cmath.sqrt(__temp_D_math{cache})
__temp_x1_math{cache} = (-__temp_b_math{cache} + __temp_sqrt_D_math{cache}) / (2 * __temp_a_math{cache})
__temp_x2_math{cache} = (-__temp_b_math{cache} - __temp_sqrt_D_math{cache}) / (2 * __temp_a_math{cache})
{name_of_result_variable} = [__temp_x1_math{cache}, __temp_x2_math{cache}, __temp_D_math{cache}]
'''
        code = self.frame.Code(code)
        if returning == 'code': return code
        return self
    
    def log(self, x, base=math.e, name_of_result_variable='res', returning='frame'):
        return self._operand(x, name_of_result_variable, returning, op=f'math.log($, {base})', name='log')

    def exp(self, x, name_of_result_variable='res', returning='frame'):
        return self._operand(x, name_of_result_variable, returning, op='math.exp($)', name='exp')

    def power(self, x, exponent, name_of_result_variable='res', returning='frame'):
        cache = self._cache()
        self.frame.Var(f'__exp_temp{cache}', exponent)
        return self._operand(x, name_of_result_variable, returning, op=f'$ ** __exp_temp{cache}', name='power')
    
    def mean(self, values, name_of_result_variable='res', returning='frame'):
        return self._operand(values, name_of_result_variable, returning, op='sum($) / len($)', name='mean')

    def std(self, values, name_of_result_variable='res', returning='frame'):
        self.frame.Code(f'"""\nstd\nReturning: {returning}\nName of result var: {name_of_result_variable}\nInputs: {values}"""')
        cache = self._cache()
        code = f'''
_mean_{cache} = sum({values}) / len({values})
{name_of_result_variable} = math.sqrt(sum((x - _mean_{cache}) ** 2 for x in {values}) / len({values}))'''
        code = self.frame.Code(code)
        return code if returning == 'code' else self

    def normalize(self, values, name_of_result_variable='res', returning='frame'):
        cache = self._cache()
        self.frame.Code(f'"""\nnormalize\nReturning: {returning}\nName of result var: {name_of_result_variable}\nInputs: {values}"""')
        code = f'''
_min_{cache} = min({values})
_max_{cache} = max({values})
{name_of_result_variable} = [(x - _min_{cache}) / (_max_{cache} - _min_{cache}) for x in {values}]'''
        code = self.frame.Code(code)
        return code if returning == 'code' else self

    def linear_regression(self, x_data, y_data, name_of_result_variable='res', returning='frame'):
        """Linear regression (returning [slope, intercept])"""
        self.frame.Code(f'"""\nlinear_regression\nReturning: {returning}\nName of result var: {name_of_result_variable}\nInputs: {[x_data, y_data]}"""')
        cache = self._cache()
        code = f'''
n_{cache} = len({x_data})
sum_x_{cache} = sum({x_data})
sum_y_{cache} = sum({y_data})
sum_xy_{cache} = sum(x * y for x, y in zip({x_data}, {y_data}))
sum_xx_{cache} = sum(x * x for x in {x_data})
    
slope_{cache} = (n_{cache} * sum_xy_{cache} - sum_x_{cache} * sum_y_{cache}) / (n_{cache} * sum_xx_{cache} - sum_x_{cache} ** 2)
intercept_{cache} = (sum_y_{cache} - slope_{cache} * sum_x_{cache}) / n_{cache}
{name_of_result_variable} = [slope_{cache}, intercept_{cache}]'''
        code = self.frame.Code(code)
        return code if returning == 'code' else self

    def cosine_similarity(self, vec1, vec2, name_of_result_variable='res', returning='frame'):
        cache = self._cache()
        self.frame.Code(f'"""\ncosine_similarity\nReturning: {returning}\nName of result var: {name_of_result_variable}\nVectors: {[vec1, vec2]}"""')
        code = f'''
dot_{cache} = sum(a * b for a, b in zip({vec1}, {vec2}))
mag1_{cache} = math.sqrt(sum(x * x for x in {vec1}))
mag2_{cache} = math.sqrt(sum(x * x for x in {vec2}))
{name_of_result_variable} = dot_{cache} / (mag1_{cache} * mag2_{cache}) if mag1_{cache} * mag2_{cache} != 0 else 0'''
        code = self.frame.Code(code)
        return code if returning == 'code' else self

    def _check(self):
        super()._check()
        if self._state['safemode']: raise PluginError('Your frame in safemode. \nMath operations works only without safemode: code execution must be available.')
    
    def _cache(self): self._counter += 1; return str(self._counter) + self.frame.framer._gen_id(self._counter)

    def _operand(self, x: int | float, 
                 name_of_result_variable: str = 'res', 
                 returning: str = 'frame', 
                 op: str = '$',
                 name: str = 'math_operation') -> 'Frame.Code' | MathPlugin:
        self._check()
        cache = self._cache()
        self.frame.Code(f'"""\n{name}\nReturning: {returning}\nName of result var: {name_of_result_variable}\n"""')
        temp_name = f'__x_temp_{name_of_result_variable}_math{cache}' 
        self.frame.Var(temp_name, f'{x}', with_eval=True)
        code = self.frame.Code(f'{name_of_result_variable} = {op.replace("$", f"({temp_name})")}')
        if returning.lower() == 'code':
            return code
        return self
    