import socket
import json
import pygame
import random

#select a server port
server_port = 12000

#create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#bind the server to the localhost at port server_port
server_socket.bind(('172.31.47.170',server_port))

print('UDP Server running on port ', server_port)

#Now the loop that listens from clients
#As UDP is not connection oriented,the same UDP socket serves all clients

userList = {}

# game initialization stuff here

pygame.init()

SCREEN_X= 720
"Width of the screen"
SCREEN_Y=480
"Height of the screen"

clock = pygame.time.Clock()

FOOD_WIDTH = 20

def generateFood():
    return pygame.Rect(random.randint(0, SCREEN_X - FOOD_WIDTH),
                       random.randint(0, SCREEN_Y - FOOD_WIDTH),
                       FOOD_WIDTH, FOOD_WIDTH)

SNAKE_WIDTH = 20

accurate_x = 100.0
accurate_y = 50.0

gameover = False

snake_pos = [accurate_x, accurate_y]
"Head of the snake"

snake_body = [(snake_pos[0], snake_pos[1])]
"'Units' of the snake body"

food = generateFood()

while True:

    #cadd below is the client process address
    json_msg, cadd = server_socket.recvfrom(2048)
    json_msg = json_msg.decode()
    msg = json.loads(json_msg)
    msg_x = msg["x"]
    msg_y = msg["y"]
    

    #If first time user, add initial position (spawn snake head)
    if cadd[0] not in userList:
        userList[cadd[0]] = {'position': snake_pos, 'body': snake_body, 'score' : 0}
        print("user joined")
        print(cadd)

    #Update snake head position
    userList[cadd[0]]['position'][0] -= msg_x * 10
    userList[cadd[0]]['position'][1] += msg_y * 10

    
    #update snake body
    userList[cadd[0]]['body'].insert(0, (snake_pos[0], snake_pos[1]))

    # snake be getting bigger
    for i in userList:
        pos = userList[i]['position']
        pos_rect = pygame.Rect(pos[0],pos[1],SNAKE_WIDTH,SNAKE_WIDTH)
        if pos_rect.colliderect(food):
            food = generateFood()
            userList[i]['score'] += 1
            break
        else: 
            userList[i]['body'].pop()
        
    
    if snake_pos[0] < 0 or snake_pos[0] > SCREEN_X-SNAKE_WIDTH or snake_pos[1] < 0 or snake_pos[1] > SCREEN_Y-SNAKE_WIDTH:
        gameover = True
        pygame.quit()
    


    food_decode = (food.left, food.top, food.width, food.height)

    gameState = {'userlist': userList, 'food': food_decode, 'gameover': gameover}

    msg = json.dumps(gameState)
    server_socket.sendto(msg.encode(),(cadd[0], cadd[1]))

    #send reply message to all other client process 
    # for i in userList:
    #     if (i != cadd):
    #         server_socket.sendto(msg.encode(),(cadd[0], cadd[1]))
    #         print("Message forwarded to client " + str(cadd))    
    clock.tick(60)

    

