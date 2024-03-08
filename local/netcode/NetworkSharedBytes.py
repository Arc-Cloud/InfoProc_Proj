from TCPConnection import TCPConnection
from UDPConnection import UDPConnection
import multiprocessing as mp
import ctypes
import time

class NetworkSharedBytes():
    """
    Bytes that are automatically synchronised with host/clients. Only access with the provided `get()` and `set()` methods.
    """
    def __init__(self, initial_val = None, send = False, id = None):
        if initial_val == None: initial_val = bytes([0])
        self.__val = initial_val
        self.send = send
        self.id = id

    def get(self, lock = None):
        #self.lock.acquire()
        val = self.__val
        #self.lock.release()
        return val

    def set(self, val, lock = None):
        #self.lock.acquire()
        self.__val = val
        #self.lock.release()

__globals = []

def __networkSharedBytesDaemon(ip, port, host, frequency, timeout, shared_vars, list_lock, max_clients):
    tcp_conn = TCPConnection(ip, port, host = host, timeout = timeout)
    udp_conn = UDPConnection(ip, port, host = host, timeout = 0.001)
    IDEAL_TIMEOUT = 1 / frequency
    cur_end_time = time.time()

    if host:
        clients = []
        pending_clients = []
        next_id = 1

    # Forward unique message
    if not host:
        tcp_recv = tcp_conn.recv()
        udp_conn.send(tcp_recv, mark_as_responded = False)

        loop = True
        while loop:
            tcp_recv = tcp_conn.recv()
            for tcp_recv_var in tcp_recv:
                if tcp_recv_var == 0:
                    loop = False
                    break
                __globals.append(NetworkSharedBytes(id = bytes((tcp_recv_var,))))
                shared_vars.append(__globals[-1])

    while tcp_conn.isAlive() and udp_conn.isAlive():
        cur_end_time += IDEAL_TIMEOUT

        list_lock.acquire()

        if host:
    
            # Send all variables which need sending
            for shared_var in shared_vars:
                for client in clients:
                    if shared_var.send != client[0]:
                        udp_conn.send(shared_var.id + shared_var.get(), response_targ_index = client[1], mark_as_responded = False)

            # Accept a new user
            tcp_conn.setMaxClients(max_clients.value[0])
            client_index = tcp_conn.acceptNewClient()
            if client_index != None:
                unique_message = bytes((0,)) + f"Unique message {client_index}".encode() # Can make more sophisticated
                tcp_conn.send(unique_message, client_index = client_index)
                pending_clients.append([client_index, unique_message, time.time()])

            # Prune pending_clients
            for i in range(len(pending_clients) - 1, -1, -1):
                if time.time() - pending_clients[i][2] > timeout:
                    tcp_conn.clients[pending_clients[i][0]].close()
                    pending_clients.pop(i)

            # Send variable over TCP if applicable and create new variables
            for client in clients:
                tcp_conn.clients[client[0]].settimeout(0.001)
                tcp_recv = tcp_conn.recv(client_index = client[0])
                tcp_conn.clients[client[0]].settimeout(timeout)
                if tcp_recv != b"":
                    for tcp_recv_var in tcp_recv:
                        if tcp_recv_var == 0:
                            __globals.append(NetworkSharedBytes(id = bytes((next_id,)), send = client[0]))
                            shared_vars.append(__globals[-1])
                            for client_ in clients:
                                tcp_conn.send(bytes((next_id,)), client_index = client_[0])
                            next_id += 1
                            continue
                        try:
                            shared_var_index = [i.id for i in shared_vars].index(bytes((tcp_recv_var,)))
                            tcp_conn.send(shared_vars[shared_var_index].get(), client_index = client[0])
                        except ValueError:
                            tcp_conn.send(bytes((0,)), client_index = client[0])
                
            # Attempt to add new variables
            for shared_var_index, shared_var in enumerate(shared_vars):
                if shared_var.id == None:
                    for client in clients:
                        tcp_conn.send(bytes((next_id,)), client_index = client[0])
                    tmp = shared_vars[shared_var_index]
                    tmp.id = bytes((next_id,))
                    shared_vars[shared_var_index] = tmp
                    next_id += 1
                
            # Receive remaining variables
            udp_recvs = []
            while True:
                udp_recv = udp_conn.recv()
                if udp_recv == None: break
                # Check for moving pending client to client. Should make more sophisticated.
                if udp_recv[0][0] == 0:
                    pending_client_index = [i[1] for i in pending_clients].index(udp_recv[0])
                    clients.append([pending_clients[pending_client_index][0], udp_recv[1]])
                    pending_clients.pop(pending_client_index)
                    for shared_var in shared_vars:
                        tcp_conn.send(shared_var.id, client_index = clients[-1][0])
                    tcp_conn.send(bytes((0,)), client_index = clients[-1][0])
                    continue
                # Disregard if not from client
                if not udp_conn.pending_responses[udp_recv[1]][0] in [udp_conn.pending_responses[i][0] for i in [j[1] for j in clients]]: continue
                # Insert most recent receives at start of list, storing only data
                udp_recvs.insert(0, udp_recv[0])
            # Clear pending responses in udp_conn, not used or needed
            for i in range(len(udp_conn.pending_responses)):
                if i in [j[1] for j in clients]: continue
                udp_conn.pending_responses[i][1] = False
            clients_to_pop = []
            shared_vars_to_pop = []
            for shared_var_index, shared_var in enumerate(shared_vars):
                for client_index, client in enumerate(clients):
                    if shared_var.send == client[0]:
                        found = False
                        for i, udp_recv in enumerate(udp_recvs):
                            if bytes((udp_recv[0],)) == shared_var.id:
                                tmp = shared_vars[shared_var_index]
                                tmp.set(udp_recv[1:])
                                shared_vars[shared_var_index] = tmp
                                found = True
                                break
                        if found: udp_recvs.pop(i)
                        else:
                            # Not received
                            if not tcp_conn.send(shared_var.id, client_index = client[0]):
                                tcp_conn.clients[client[0]].close()
                                tcp_conn.is_alive[1][client[0]] = False
                                clients_to_pop.append(client_index)
                                shared_vars_to_pop.append(shared_var_index)
                                continue
                            tcp_recv = tcp_conn.recv(client_index = client[0])
                            if tcp_recv == b"":
                                tcp_conn.clients[client[0]].close()
                                tcp_conn.is_alive[1][client[0]] = False
                                clients_to_pop.append(client_index)
                                shared_vars_to_pop.append(shared_var_index)
                                continue
                            tmp = shared_vars[shared_var_index]
                            tmp.set(tcp_recv)
                            shared_vars[shared_var_index] = tmp
            for i in clients_to_pop[::-1]:
                clients.pop(i)
            for i in shared_vars_to_pop[::-1]:
                shared_vars.pop(i)

        else:

            # Send all variables which need sending
            for shared_var in shared_vars:
                if shared_var.send and shared_var.id != None and shared_var.id != bytes((0,)):
                    udp_conn.send(shared_var.id + shared_var.get(), response_targ_index = 0, mark_as_responded = False)

            # Send variable over TCP if applicable and create new variables
            tcp_conn.socket.settimeout(0.001)
            tcp_recv = tcp_conn.recv()
            tcp_conn.socket.settimeout(timeout)
            if tcp_recv != b"":
                for tcp_recv_var in tcp_recv:
                    shared_var_index = -1
                    for i, shared_var in enumerate(shared_vars):
                        if shared_var.id == bytes((tcp_recv_var,)):
                            shared_var_index = i
                            break
                    if shared_var_index == -1:
                        __globals.append(NetworkSharedBytes(id = bytes((tcp_recv_var,))))
                        shared_vars.append(__globals[-1])
                        continue
                    tcp_conn.send(shared_vars[shared_var_index].get())

            # Attempt to add new variables
            for i in range(len(shared_vars)):
                if shared_vars[i].id == None:
                    if not tcp_conn.send(bytes((0,))): tcp_conn.close()
                    tcp_recv = tcp_conn.recv()
                    if tcp_recv == b"": tcp_conn.close()
                    elif len(tcp_recv) != 1: shared_vars[i].id = bytes((0,))
                    else:
                        val = shared_vars[i].get()
                        tmp = shared_vars[i]
                        tmp.id = tcp_recv
                        shared_vars[i] = tmp
            
            # Receive remaining variables
            udp_recvs = []
            while True:
                udp_recv = udp_conn.recv()
                if udp_recv == None: break
                # Disregard if not from host
                if udp_conn.pending_responses[udp_recv[1]][0] != udp_conn.pending_responses[0][0]: continue
                # Insert most recent receives at start of list, storing only data
                udp_recvs.insert(0, udp_recv[0])
            # Clear pending responses in udp_conn, not used or needed
            udp_conn.pending_responses = [udp_conn.pending_responses[0]]
            for shared_var_index, shared_var in enumerate(shared_vars):
                if (not shared_var.send) and shared_var.id != None and shared_var.id != bytes((0,)):
                    found = False
                    for i, udp_recv in enumerate(udp_recvs):
                        if udp_recv[0] == shared_var.id:
                            found = True
                            tmp = shared_vars[shared_var_index]
                            tmp.set(udp_recv[1:])
                            shared_vars[shared_var_index] = tmp
                            break
                    if found: udp_recvs.pop(i)
                    else:
                        # Not received
                        if not tcp_conn.send(shared_var.id): tcp_conn.close()
                        tcp_recv = tcp_conn.recv()
                        if tcp_recv == b"": tcp_conn.close()
                        tmp = shared_vars[shared_var_index]
                        tmp.set(tcp_recv)
                        shared_vars[shared_var_index] = tmp
        list_lock.release()

        remaining_time = cur_end_time - time.time()
        if remaining_time > 0:
            time.sleep(remaining_time)
        else:
            cur_end_time = time.time()

def networkSharedBytesInit(ip, port, host, frequency, timeout):
    manager = mp.Manager()
    shared_vars = manager.list()
    list_lock = manager.Lock()
    max_clients = mp.Value(ctypes.c_char)
    proc = mp.Process(target = __networkSharedBytesDaemon,
                      args = (ip, port, host, frequency, timeout, shared_vars, list_lock, max_clients),
                      daemon = True)
    proc.start()
    return (shared_vars, list_lock, max_clients)

def addNetworkSharedBytes(shared_vars, list_lock, network_shared_bytes):
    __globals.append(network_shared_bytes)
    list_lock.acquire()
    shared_vars.append(__globals[-1])
    list_lock.release()

def setNetworkSharedBytes(shared_vars, index, list_lock, new_val):
    list_lock.acquire()
    tmp = shared_vars[index]
    tmp.set(new_val)
    shared_vars[index] = tmp
    list_lock.release()

if __name__ == "__main__":

    # INSTRUCTIONS: HAVE SERVER CALL AS FOLLOWS (feel free to increase frequency):
    shared_vars, list_lock, max_clients = networkSharedBytesInit("127.0.0.1", 12345, True, 10, 1)
    max_clients.value = bytes((5,))

    # THE SERVER CAN HAVE A VARIABLE ONLY IT MODIFIES. CREATE AS FOLLOWS:
    addNetworkSharedBytes(shared_vars, list_lock, NetworkSharedBytes(send = None))

    while True:
        
        # MUST USE setNetworkSharedBytes, cannot do shared_vars[i].set(). Must set to bytes
        setNetworkSharedBytes(shared_vars, 0, list_lock, bytes((shared_vars[0].get()[0] + 1,)))
        
        # CAN USE shared_vars.get()
        print([i.get() for i in shared_vars])
        time.sleep(0.5)