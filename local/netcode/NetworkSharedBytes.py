from TCPConnection import TCPConnection
from UDPConnection import UDPConnection
import multiprocessing as mp
import time

"""def recv_thread(shared_bytes):
    cur_end_time = time.time()
    HEADROOM_TIME = shared_bytes.conn_timeout - shared_bytes.conn_ideal_timeout
    while shared_bytes.isAlive():
        # End time of UDP send/recv. Aims for ideal frequency over time.
        cur_end_time += shared_bytes.conn_ideal_timeout

        # Send current data. Should be instantaneous so no need for timeout update
        cur_val = shared_bytes.get()
        shared_bytes.udp_conn.send(cur_val, mark_as_responded = False)

        # Set the timeout for receive, accounting for headroom
        shared_bytes.udp_conn.socket.settimeout(cur_end_time + HEADROOM_TIME - time.time())
        inp = shared_bytes.udp_conn.recv(will_respond = False)

        # If no data is received (timeout/disconnect)
        if inp == b"":
            shared_bytes.tcp_conn.socket.settimeout(shared_bytes.timeout - shared_bytes.conn_timeout)
            if not tcp_conn.send()

        # Prevent redundant write, less wasted mutex lock time
        if inp != cur_val:
            shared_bytes.set(inp)"""

def host_listen(shared_bytes):
    tcp_index = shared_bytes.tcp_conn.acceptNewClient()
    if tcp_index == None:
        return
    
    while len(shared_bytes.tcp_index_to_udp_index) - 1 < tcp_index:
        shared_bytes.tcp_index_to_udp_index.append(-1)
    
    # Can (and should?) make more complicated
    unique_data = f"Unique data: {tcp_index}".encode()

    shared_bytes.tcp_conn.send(unique_data, client_index = tcp_index)
    timeout = time.time() + shared_bytes.timeout
    wrong_recv = []
    while time.time() < timeout:
        shared_bytes.udp_conn.socket.settimeout(timeout - time.time())
        val = shared_bytes.udp_conn.recv(will_respond = True)
        if val[0] != unique_data:
            wrong_recv.append(val)
        shared_bytes.tcp_index_to_udp_index[tcp_index] = val[1]
    return wrong_recv

def client_send_thread(shared_bytes):
    unique_data = shared_bytes.tcp_conn.recv()
    shared_bytes.udp_conn.send(unique_data)
    cur_end_time = time.time()
    TIMEOUT_OFFSET = shared_bytes.timeout - shared_bytes.conn_ideal_timeout
    while shared_bytes.isAlive():
        cur_end_time += shared_bytes.conn_ideal_timeout

        cur_val = shared_bytes.get()
        shared_bytes.udp_conn.send(cur_val, mark_as_responded = False)

        shared_bytes.tcp_conn.socket.settimeout(cur_end_time - time.time())
        recv = shared_bytes.tcp_conn.recv()
        
        # Skip the remaining if no TCP received
        if recv == b"":
            continue

        # Can use more recent value
        cur_val = shared_bytes.get()

        shared_bytes.tcp_conn.socket.settimeout(cur_end_time + TIMEOUT_OFFSET - time.time())
        if not shared_bytes.tcp_conn.send(cur_val):
            shared_bytes.tcp_conn.close()
            shared_bytes.udp_conn.is_alive = False

def host_recv_thread(shared_bytes):
    cur_end_time = time.time()
    recv_buffer = []
    while shared_bytes.isAlive():
        if shared_bytes.listening: recv_buffer = host_listen(shared_bytes)
        cur_end_time += shared_bytes.conn_ideal_timeout
        



def host_send_thread(shared_bytes):
    pass

def client_recv_thread(shared_bytes):
    pass



class NetworkSharedBytes():
    """
    Bytes that are automatically synchronised with host/clients.
    """

    __TIMEOUT_HEADROOM_MULT = 1.1

    def __init__(self, ip, port, host = False, frequency = 1, timeout = 5, host_write = True):
        self.conn_ideal_timeout = 1 / frequency
        self.conn_timeout = self.conn_ideal_timeout * self.__TIMEOUT_HEADROOM_MULT
        self.tcp_conn = TCPConnection(ip, port, host = host, timeout = self.conn_timeout)
        self.udp_conn = UDPConnection(ip, port, host = host, timeout = self.conn_timeout)
        self.val = b""
        self.last_data_time = 0
        self.timeout = timeout
        manager = mp.Manager()
        self.lock = manager.Lock()
        if host:
            self.listening = True
            tcp_index_to_udp_index = []

    def set(self, val, time_ = None):
        self.lock.acquire()
        self.val = val
        if time_ != None:
            self.last_data_time = time_
        self.lock.release()

    def get(self):
        self.lock.acquire()
        val = self.val
        self.lock.release()

        if self.last_data_time == 0:
            time_ = -1
        else:
            # No need for lock, only reading float, which is atomic
            time_ = time.time() - self.last_data_time

        return (val, time_)

    def isAlive(self):
        # No need for lock, only reading bool, which is atomic
        return self.tcp_conn.isAlive() and self.udp_conn.isAlive()

if __name__ == "__main__":
    a = NetworkSharedBytes("127.0.0.1", 12345, host = True, frequency = 5)
    b = NetworkSharedBytes("127.0.0.1", 12345, host = False, frequency = 5)

    #client_send_thread(b)