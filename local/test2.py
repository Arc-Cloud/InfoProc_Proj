from netcode import networkSharedBytesInit, NetworkSharedBytes, addNetworkSharedBytes, setNetworkSharedBytes
from time import sleep

## SAMPLE HOST CODE

# Mandatory because of threads
if __name__ == "__main__":

    shared_vars, list_lock, max_clients = networkSharedBytesInit("127.0.0.1", 12345, True, 10, 1)
    max_clients.value = 5

    # Server-controlled variable. Must be send = None
    addNetworkSharedBytes(shared_vars, list_lock, NetworkSharedBytes(send = None))

    while True:

        # Function handles lock. Must use function for setting
        setNetworkSharedBytes(shared_vars, 0, list_lock, bytes((shared_vars[0].get()[0] + 1, )))
        # Note: no overflow in python, this will crash at 255

        # Note: shared_vars[A].is_alive is redundant in server code. Server always pops, not sets flag

        # Use locks when reading. Release as soon as read is complete
        list_lock.acquire()
        print([(i.get(), i.id) for i in shared_vars])
        list_lock.release()
        sleep(0.5)