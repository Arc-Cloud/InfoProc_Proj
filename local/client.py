import socket
import time
import accelerometer_input as acc
import json
import os

class client:
    #the server name and port client wishes to access
    server_name = '13.60.28.247'
    server_port = 12000
    #create a UDP client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # client_socket.bind(('localhost', 10000))

    print("UDP client running...")
    print("Connecting to server at IP: ", server_name, " PORT: ", server_port)


    while True:
        msg = {
            'x' : acc.Input.getX(),
            'y' : acc.Input.getY()
        }

        msg_json = json.dumps(msg)
        
        #send the message to the udp server
        client_socket.sendto(msg_json.encode(),(server_name, server_port))

        #return values from the server
        msg, sadd = client_socket.recvfrom(2048)
        #show output and close client
        os.system('cls')
        print(json.loads(msg))
        time.sleep(0.01)

