import socket as s

class UDPConnection():
    """
    Basic UDP host/client.
    """
    def __init__(self, ip, port, host = False, timeout = None):
        self.socket = s.socket(s.AF_INET, s.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.socket.setblocking(1)
        self.host = host
        if host:
            try:
                self.socket.bind((ip, port))
                self.is_alive = True
                self.pending_responses = []
            except OSError:
                self.is_alive = False
        else:
            self.pending_responses = [[(ip, port), True]]

    def send(self, bytes_, response_targ_index = 0, mark_as_responded = True):
        """
        Sends data to address with index `response_targ_index`. If `mark_as_responded = True`, marks the
        address as responded and invalid to send to (if multiple `response_targ_index`'s have the same
        address, the other ones are still valid if one is marked as responded).
        """
        self.socket.sendto(bytes_, self.pending_responses[response_targ_index][0])
        if mark_as_responded:
            self.pending_responses[response_targ_index][1] = False
        return True

    __BUFFER_SIZE = 4096
    def recv(self, will_respond = True):
        """
        Receives next value in buffer and returns it. If `will_respond = True`, adds the
        recipient address to list and returns a tuple (`output`, `index`).\n
        Note: returns `None` on timeout.
        """
        try:
            out, addr = self.socket.recvfrom(self.__BUFFER_SIZE)
        except TimeoutError:
            return None

        if will_respond:
            self.__cleanUpList()

            for i, pending_response in enumerate(self.pending_responses):
                if not pending_response[1]:
                    self.pending_responses[i] = [addr, True]
                    return (out, i)

            self.pending_responses.append([addr, True])
            return (out, len(self.pending_responses) - 1)
        else:
            return out

    def __cleanUpList(self):
        for i in range(len(self.pending_responses) - 1, -1, -1):
            if not self.pending_responses[i][1]:
                self.pending_responses.pop(i)
            else:
                return
    
    def isAlive(self):
        return self.is_alive