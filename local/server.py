import socket
import json

#select a server port
server_port = 12000

#create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#bind the server to the localhost at port server_port
server_socket.bind(('172.31.32.91',server_port))

print('UDP Server running on port ', server_port)

#Now the loop that listens from clients
#As UDP is not connection oriented,the same UDP socket serves all clients

userList = {}

while True:

    #cadd below is the client process address
    json_msg, cadd = server_socket.recvfrom(2048)
    json_msg = json_msg.decode()
    msg = json.loads(json_msg)
    msg_x = msg["x"]
    msg_y = msg["y"]

    #If first time user, add initial position (spawn snake head)
    if cadd[0] not in userList:
        userList[cadd[0]] = {'x': 0, 'y': 0}
        
    #Update snake head position
    userList[cadd[0]]['x'] -= msg_x * 10
    userList[cadd[0]]['y'] += msg_y * 10
    msg = json.dumps(userList)
    server_socket.sendto(msg.encode(),(cadd[0], cadd[1]))
    #send reply message to all other client process 
    # for i in userList:
    #     if (i != cadd):
    #         server_socket.sendto(msg.encode(),(cadd[0], cadd[1]))
    #         print("Message forwarded to client " + str(cadd))    
               

    

