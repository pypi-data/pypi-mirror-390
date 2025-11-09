import hashlib, abc, functools, sys
#sys.set_int_max_str_digits(50000) 


def str_to_int(string: str, summing: bool = True) -> list | int:
    string = str(string)
    alphabet = list('1234567890 ' +
                    'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm' +
                    'ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЁЯЧСМИТЬБЮйцукенгшщзхъфывапролджэёячсмитьбю' +
                    '!@#$%^&*()_+¡™£¢∞§¶•ªº–≠[]{}\\|/?.,<>\'":;±§`~\n\t')
    res = []
    for i in list(string):
        if i in alphabet: res.append(alphabet.index(i)+1)
        else: 
            alphabet.append(i)
            res.append(alphabet.index(i)+1)
    return sum(res) if summing else res

def int_to_str(integrear: str, to_join: bool = True) -> list:
    integrear = str(integrear)
    alphabet = list('1234567890-' +
                    'QwErTyUiOpAsDfGhJkLzXcVbNmqWeRtYuIoPaSdFgHjKlZxCvBnM')
    res = []
    local_alphabet = alphabet.copy()
    kf = str_to_int(integrear)
    for i in list(integrear):
        try:
            i = int(i) % (kf) + int(i)
            res.append(local_alphabet[i])
            local_alphabet = local_alphabet[:i] + local_alphabet[i+1:]
            if len(local_alphabet) < 10: local_alphabet=alphabet.copy()
        except: 
            local_alphabet=alphabet.copy()
            i = int(i) % (kf) + int(i)
            res.append(local_alphabet[i])
            local_alphabet = local_alphabet[:i] + local_alphabet[i+1:]
            if len(local_alphabet) < 10: local_alphabet=alphabet.copy()
    return ''.join(res) if to_join else res


def sha512_sha256_hash(inp):
    inp = str(inp).encode()
    h1 = hashlib.sha3_512(inp)
    h2 = hashlib.sha3_256(h1.hexdigest().encode())
    return h2.hexdigest()


def our(inp):
    done_int = str_to_int(inp)
    first_digit = int(list(str(done_int))[0])
    last_digit = int(list(str(done_int))[-1])
    res = []
    for i in range(10+first_digit):
        done_int = int(''.join(reversed(list(str((done_int << 3 + i) >> 4))))) - i + last_digit * first_digit
        res += [int_to_str(done_int+i*last_digit)]
    return str_to_int(str(res))
    
def to_id(inp):
    integrear: int = str_to_int(inp)
    id_our = our(f'{inp}{integrear}')
    return f'{id_our}{integrear}{id(inp)}'



class ClassApi(abc.ABC):
    def __init__(self):
        super().__init__()
    
    @staticmethod
    def sha512_sha256_hash(inp): return sha512_sha256_hash(inp)

    @staticmethod
    def hash_pattern(inp): return our(inp)

    @staticmethod
    class system:
        def str_to_int(string: str, summing: bool = True): return str_to_int(string, summing)
        def int_to(integrear: int, join: bool = True): return str_to_int(integrear, join)

