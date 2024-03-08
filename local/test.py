from netcode import networkSharedBytesInit, NetworkSharedBytes, addNetworkSharedBytes, setNetworkSharedBytes
from time import sleep

## SAMPLE CLIENT CODE

# Mandatory because of threads
if __name__ == "__main__":

    shared_vars, list_lock, max_clients = networkSharedBytesInit("127.0.0.1", 12345, False, 10, 1)

    # Client-controlled variable. Must be send = True
    addNetworkSharedBytes(shared_vars, list_lock, NetworkSharedBytes(send = True))

    while True:

        # Function handles lock. Must use function for setting
        setNetworkSharedBytes(shared_vars, 0, list_lock, bytes((shared_vars[0].get()[0] + 1, )))
        # Note: no overflow in python, this will crash at 255

        # Note: index within list varies across clients and host, but shared_vars[A].id will be synchronised.
        # Note: upon disconnect, or deletion of that variable, shared_vars[A].is_alive will be False.
        #       is_alive is true from creation, even before sync with server.

        # Use locks when reading. Release as soon as read is complete
        list_lock.acquire()
        print([(i.get(), i.id, i.is_alive) for i in shared_vars])
        list_lock.release()
        sleep(0.5)