import socket as s

class TCPConnection():
    """
    Basic TCP host/client.
    """

    __CONNECT_TIMEOUT = 1
    __ACCEPT_TIMEOUT = 0.01

    def __init__(self, ip, port, host = False, timeout = None):
        self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.host = host
        if host:
            try:
                self.socket.settimeout(self.__ACCEPT_TIMEOUT)
                self.socket.bind((ip, port))
                self.timeout = timeout # For assigning to client connections
                self.clients = []
                self.is_alive = [True, []] # [LISTENING_SOCKET_IS_ALIVE, [CLIENT_SOCKETS_ARE_ALIVE...]]
                self.socket.listen(1)
            except OSError:
                self.is_alive = [False]
        else:
            try:
                self.socket.settimeout(self.__CONNECT_TIMEOUT)
                self.socket.connect((ip, port))
                self.socket.settimeout(timeout)
                self.is_alive = True
            except TimeoutError:
                self.is_alive = False


    def setMaxClients(self, max_clients = None):
        """
        For `host = True`:\n
        Sets the maximum number of clients.
        """
        self.max_clients = max_clients
    
    def acceptNewClient(self, dead_conn_policy = None, clean_up = True):
        """
        For `host = True`:\n
        Accepts a new client. Returns client index, or `None` on timeout.\n
        Note: `dead_conn_policy` has the following possible values:\n
        `override` (default) overrides any dead connection, and creates a new one if none exist.\n
        `ignore` ensures all dead connections remain untouched and always creates new.\n
        Note: `clean_up` removes redundant list elements if `True` (a redundant list element is one
        which is no longer alive and has a higher index than the highest alive index).
        """
        if dead_conn_policy == None: dead_conn_policy = "override"
        try:
            conn = self.socket.accept()[0]
        except TimeoutError:
            return None
        conn.settimeout(self.timeout)

        self.socket.listen(1)

        if self.is_alive[1].count(True) >= self.max_clients:
            conn.close()
            return None
        
        if clean_up: self.__cleanUpList()

        if dead_conn_policy == "override":
            for i in range(len(self.clients)):
                if self.is_alive[1][i] == False:
                    self.clients[i] = conn
                    self.is_alive[1][i] = True
                    return i

        self.clients.append(conn)
        self.is_alive[1].append(True)
        return len(self.clients) - 1
    
    def send(self, bytes_, client_index = 0):
        """
        For `host = True`:\n
        Send data to a client with `client_index`. Returns whether send was successful.\n
        For `host = False`:\n
        Send data to host. Returns whether send was successful.\n
        """
        if self.host:
            try:
                self.clients[client_index].sendall(bytes_)
                return True
            except ConnectionResetError:
                self.is_alive[1][client_index] = False
                return False
        else:
            try:
                self.socket.sendall(bytes_)
                return True
            except ConnectionResetError:
                self.is_alive = False
                return False
    
    __BUFFER_SIZE = 4096
    def recv(self, client_index = 0, timeout = False):
        """
        For `host = True`:\n
        Receive data from a client with `client_index`.\n
        For `host = False`:\n
        Receive data from host.\n
        Note: on timeout, the function returns empty byte array but `TCPConnection.isAlive()` will still return `True`.
        """
        if self.host:
            if timeout != False: self.clients[client_index].settimeout(timeout)
            try:
                out = self.clients[client_index].recv(self.__BUFFER_SIZE)
                if len(out) == 0:
                    self.is_alive[1][client_index] = False
                return out
            except TimeoutError:
                self.is_alive[1][client_index] = False
                return b""
            except ConnectionResetError:
                self.is_alive[1][client_index] = False
                return b""
            
        else:
            if timeout != False: self.socket.settimeout(timeout)
            try:
                out = self.socket.recv(self.__BUFFER_SIZE)
                if len(out) == 0:
                    self.is_alive = False
                return out
            except TimeoutError:
                self.is_alive = False
                return b""
            except ConnectionResetError:
                self.is_alive = False
                return b""
    
    def isAlive(self, client_index = None):
        """
        For `host = True`:\n
        Says whether the connection with client of index `client_index` is alive.\n
        For `host = False`:\n
        Says whether the connection with host is alive.
        """
        if self.host:
            if client_index == None:
                return self.is_alive[0]
            else:
                return self.is_alive[1][client_index]
        else:
            return self.is_alive
        
    def close(self):
        """
        For `host = True`:\n
        Closes listening socket and all client connections.\n
        For `host = False`:\n
        Closes connection to host.
        """
        if self.host:
            self.socket.close()
            for i, client in enumerate(self.clients):
                if self.is_alive[1][i]:
                    client.close()
                    self.is_alive[1][i] = False
        else:
            self.socket.close()
            self.is_alive = False

    def __cleanUpList(self):
        for i in range(len(self.clients) - 1, -1, -1):
            if not self.is_alive[1][i]:
                self.is_alive[1].pop(i)
                self.clients.pop(i)
            else:
                return