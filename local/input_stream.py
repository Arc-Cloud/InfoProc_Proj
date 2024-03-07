"C:/intelFPGA_lite/18.1/nios2eds/Nios II Command Shell.bat"

import multiprocessing.shared_memory as shm

INPUT_BYTE_COUNT = 6
SHARED_MEMORY_NAME = "acc_inp"

try:
    shared_mem = shm.SharedMemory(name = SHARED_MEMORY_NAME, size = 6, create = True)
except:
    shared_mem = shm.SharedMemory(name = SHARED_MEMORY_NAME, size = 6)

while True:
    inp = input()
    for i in range(INPUT_BYTE_COUNT):
        try:
            shared_mem.buf[i] = int(inp[2*i]+inp[2*i+1], 16)
        except:
            pass # Non-int received e.g. upon connecting. Want to ignore
    