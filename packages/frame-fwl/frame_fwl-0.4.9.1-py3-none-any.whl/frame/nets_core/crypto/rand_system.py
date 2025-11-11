import secrets as s, abc as a
from .bip39_worldlist import wordlist
rnd = s.SystemRandom()


def gencode_int(length: int = 10):
    result = []
    for _ in range(length): result.append(rnd.randrange(0, 9))
    res = []
    for _ in range(length): res.append(rnd.choice(result))
    result1 = ''
    for i in res: result1 += str(i)
    return result1

def gencode_int_sections(sections: int = 2, one_section_length: int = 4, separator: str = '-'):
    sections_tmp = []
    for i in range(sections): sections_tmp += [gencode_int(one_section_length)]
    result2 = ''
    for i in sections_tmp:
        for li in i: result2 += str(li)
        result2 += separator
    return result2[:-1]

def gencode_str(length: int = 10):
    alphabet = list('1234567890' +
                    'QwErTyUiOpAsDfGhJkLzXcVbNmqWeRtYuIoPaSdFgHjKlZxCvBnM')
    result = []
    for _ in range(length): result.append(rnd.choice(alphabet))
    return ''.join(result)

def gencode_str_sections(sections: int = 4, one_section_length: int = 5, separator: str = '-'):
    sections_tmp = []
    for i in range(sections): sections_tmp += [gencode_str(one_section_length)]
    return separator.join(sections_tmp)

def genpass(length: int = 20):
    if length < 8: raise ValueError(f"Can't generate password with length < 8. Current length: [{length}].")
    res = []
    for _ in range(round(length/2)): res += gencode_str(2)
    return ''.join(res)

def gen_mnemonic_phrase(word_count=12):
    return ' '.join(s.choice(wordlist) for _ in range(word_count))


class ClassApi(a.ABC):
    def __init__(self):
        super().__init__()
    
    @staticmethod
    def gen_type(type: str = 'int', length: int = 10):
        'type: int/str'
        if type == 'int': return gencode_int(length)
        else: return gencode_str(length)
    
    @staticmethod
    def gen_type_sections(type: str = 'int', 
                          sections: int = 4, 
                          one_section_length: int = 5, 
                          separator: str = '-'):
        'type: int/str'
        if type == 'int': return gencode_int_sections(sections, one_section_length, separator)
        else: return gencode_str_sections(sections, one_section_length, separator)
    
    @staticmethod
    def gen_password(length: int = 8): return genpass(length)

    @staticmethod
    def gen_mnemonic(length: int = 10): return gen_mnemonic_phrase(length)