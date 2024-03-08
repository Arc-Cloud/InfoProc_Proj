from NetworkSharedBytes import networkSharedBytesInit, NetworkSharedBytes, addNetworkSharedBytes, setNetworkSharedBytes

import multiprocessing as mp
import ctypes
import time

def test():
    test_list = mp.Manager().list()
    return test_list

class Test():
    def __init__(self, val):
        self.val = val

def app(list_):
    tmp = NetworkSharedBytes(send = True)
    list_.append(tmp)

if __name__ == "__main__":

    # INSTRUCTIONS: CONNECT TO SERVER AS FOLLOWS:
    shared_vars, list_lock, max_clients = networkSharedBytesInit("127.0.0.1", 12345, False, 10, 5)

    # A CLIENT CAN HAVE A VARIABLE ONLY IT MODIFIES. CREATE AS FOLLOWS:
    addNetworkSharedBytes(shared_vars, list_lock, NetworkSharedBytes(send = True))

    while True:
        
        # MUST USE setNetworkSharedBytes, cannot do shared_vars[i].set(). Must set to bytes
        setNetworkSharedBytes(shared_vars, 0, list_lock, bytes((shared_vars[0].get()[0] + 1,)))

        time.sleep(0.5)
        
        # CAN USE shared_vars.get()
        print([(i.get(), i.id) for i in shared_vars])
