from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib
import base64, abc
import os
import time
import threading as th
import secrets




class WarningType:
    def __init__(self, data):
        self.raw = data
        self.data = f'WARNING <[{data}]>'
    def __new__(self, data, to_object:bool=False):
        self.raw = data
        self.data = f'WARNING <[{data}]>'
        return self if to_object else self.data
    def __repr__(self):
        return f"'{self.data}'"
    def __eq__(self, value): return self.raw == value
    def __str__(self): return self.data
    def get(self): return self.data




class SafeData:
    """
    Data class for important constants in your program.
    Cryptography defender for data out of the box.
    Isn't works with custom classes and dtypes.
    Args:
        data: Any                    - data without encrypt
        key: Any                     - key for encrypting
        salt_for_key: bytes          - salt for encrypting
        time_to_live: int | 'inf'    - if you input int - ttl=time_to_live
                                       if you input 'inf' - ttl=None
    User methods:
        'of'     - full encrypt for data
        'get'    - get data with decrypt
    """
    def __init__(self, data, key, 
                 salt_for_key: bytes=os.urandom(32), 
                 time_to_live :int|str='inf', 
                 threadlock_for_wait :bool=True):
        self._rnd_delay()
        key = self._hash(key).encode()
        kfd = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt_for_key,
    iterations=100000)
        self.time = time_to_live
        self.threadlock = threadlock_for_wait
        self.t = th.Thread(target=self._wait)
        self.t.start()
        self.working = True
        self.key = base64.urlsafe_b64encode(kfd.derive(key))
        self.encrypted_data = self._encrypt(data, self.key)
        self.decrypted = False
        self.raw = self._hash(data)
        self.counter = 0
        self.logs = []
    
    def _rnd_delay(self):
        random = secrets.SystemRandom()
        delay = (random.randrange(100, 900) * 0.00003) + (random.randrange(100, 800) * 0.00001)
        time.sleep(delay)
    
    def _wait(self):
        try:
            if isinstance(self.time, (int, float)) and self.time > 0:
                time.sleep(self.time)
            elif self.time != 'inf':
                raise ValueError(f"Invalid TTL: {self.time}")
            if self.threadlock:
                with th.Lock():
                    self.working = False
            else:
                self.working = False
        except:
            if self.threadlock:
                with th.Lock():self.working = True
            else:self.working = True

    def _log(self, log):
        time_str = str(time.time())
        tm = time_str + ' ' * (20 - len(time_str))
        lg = str(log) + ' ' * (35 - len(str(log)))
        self.logs.append(f'LOG <[ {tm} : {lg} ]>')
    
    def _encrypt(self, data, key):
        cipher = Fernet(key)
        enscrypted_data = cipher.encrypt(str(data).encode())
        del data
        return enscrypted_data
    
    def _dec(self):
        self._log('=== DECRYPTING ===')
        if not self.working:
            self._undec_enc('phrase'.encode())
            self._log('Decryption failed - is not working')
            return WarningType('NOT_FOUND').encode()
        else: 
            kfd = self.key
            cipher = Fernet(kfd)
            decrypted_data = cipher.decrypt(self.encrypted_data)
            self.decrypted = True
            self._log('Decryption done')
            return decrypted_data

    def _enc(self, data):
        self._log('=== ENCRYPTING ===')
        cipher = Fernet(self.key)
        enscrypted_data = cipher.encrypt(str(data).encode())
        self.decrypted = False
        return enscrypted_data
    
    def _undec_enc(self, a):
        self._log('Full encrypting')
        random = secrets.SystemRandom()
        kfd = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=os.urandom(32),
            iterations=100000)
        self.working = False
        self.encrypted_data = self._encrypt(a, base64.urlsafe_b64encode(kfd.derive(str(random.randint(10000, 90000)).encode())))
        del kfd
    
    def _check(self) -> tuple[bool, str]:
        des = self._dec(); self._enc(des)
        h = self.raw == self._hash(des.decode())
        d = self.decrypted == False
        if not h:
            self._log('Hash Error')
        if not d:
            self._log('Decryption Error')
        if not self.working:
            self._log("Isn't working Error")
        res =  d and h and self.working
        return (res, des)
    
    def _hash(self, data):
        return hashlib.sha256(str(data).encode()).hexdigest()

    def __enter__(self):
        self._log('New context manager')
        return self

    def __exit__(self, *args):
        self.time = 0.00001
        self._wait()
        self._undec_enc('warning'.encode())
        del self
        del args
        return 0
    
    def __call__(self, *args, **kwds):
        return self.get(args[0] if args else True)
    
    def get(self, check: bool=True, eval: bool=True):
        self.counter += 1
        ch = self._check() if check else [True, self._dec()]
        self._log(f'=== GET ===')
        try:
            self._rnd_delay()
            if ch[0]: 
                self._log('Get working')
                try:
                    import ast
                    self._rnd_delay()
                    return ast.literal_eval(ch[1].decode()) if eval else ch[1].decode()
                except:
                    self._rnd_delay()
                    return ch[1].decode()
            else: 
                self._log('Get failed')
                if self.working:
                    self._rnd_delay()
                    return WarningType(ch[1].decode())
                else:
                    self._rnd_delay()
                    self._undec_enc(ch[1])
                    return WarningType('NOT_FOUND')
        except Exception as e:
            self._rnd_delay()
            print(f'Error in <MDData.get>: {e}')
            return self

    def off(self):
        self._log('FULL DATA ENCRYPT')
        self.working = False
        self._dec()
        return self
    
    def count(self):
        return self.counter
    
    def get_logs(self, to_string: bool=True, to_join: str='\n'):
        res = to_join.join(self.logs) if to_string else self.logs
        return res




class ClassApi(abc.ABC):
    def __init__(self):
        super().__init__()
    
    @staticmethod
    def SafeDataClass(): return SafeData



if __name__ == '__main__':
    with SafeData('test', 'test') as data:
        print(data.get())
        print(data.off())
        print(data.get())