import multiprocessing.shared_memory as shm

class RawNS():
    __SHARED_MEMORY_NAME = "acc_inp"
    """
    Name of shared memory with raw accelerometer values.
    """

    __shared_mem = shm.SharedMemory(name = __SHARED_MEMORY_NAME)
    """
    Shared memory instance.
    """

    def __bytesToInt(self, byte1, byte2):
        """
        Converts 2 bytes of signed 16-bit number to int.
        """
        val = (byte1 << 8) + byte2
        if val > 0x8000: return val - 0x10000
        else: return val

    def getX(self):
        """
        Gets raw X reading from shared memory.
        """
        return self.__bytesToInt(self.__shared_mem.buf[0], self.__shared_mem.buf[1])
    
    def getY(self):
        """
        Gets raw Y reading from shared memory.
        """
        return self.__bytesToInt(self.__shared_mem.buf[2], self.__shared_mem.buf[3])
    
    def getZ(self):
        """
        Gets raw Z reading from shared memory.
        """
        return self.__bytesToInt(self.__shared_mem.buf[4], self.__shared_mem.buf[5])

Raw = RawNS()
"""
Namespace for static functions which read raw input from shared memory.
"""

if __name__ == "__main__":
    while True:
        print(Raw.getX(), Raw.getY(), Raw.getZ())
