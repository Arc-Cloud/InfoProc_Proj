import socket
import time
import accelerometer_input as acc
import json
import os
import pygame, random
from pygame.locals import *

# initialize game
pygame.init()
pygame.font.init()

#the server name and port client wishes to access
server_name = '13.48.57.52'
server_port = 12000
#create a UDP client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# client_socket.bind(('localhost', 10000))

print("UDP client running...")
print("Connecting to server at IP: ", server_name, " PORT: ", server_port)

gamover_state= False

SCREEN_X= 720
"Width of the screen"
SCREEN_Y=480
"Height of the screen"

pygame.display.set_caption('Sophie Snake Slay')
window = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
"Target window for game"

clock = pygame.time.Clock()

SNAKE_COLOUR = (255, 0, 247)
FOOD_COLOUR = (0, 255, 166)
SCORE_COLOUR = (255, 0, 247)

FOOD_WIDTH = 20

SNAKE_WIDTH = 20
score = 0


sounds = { "omnom" : pygame.mixer.Sound("eat_sound.mp3"),
           "oopsydaisy" : pygame.mixer.Sound("collision_sound.mp3"),
           "womp_womp" : pygame.mixer.Sound("womp-womp.mp3")
         }

def gamover():
    
    my_font = pygame.font.SysFont('Times New Roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, (252,3,3) )
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (SCREEN_X/2, SCREEN_Y/4)
    window.fill((10,10,10))
    window.blit(game_over_surface, game_over_rect)
    show_score(0, (252,3,3), 'Times New Roman', 20)
    pygame.display.flip()
    
    sounds["womp_womp"].play()
    time.sleep(3)
    pygame.quit()

def show_score(choice, colour, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, colour)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (SCREEN_X/10, 15)
    else:
        score_rect.midtop = (SCREEN_X/2, SCREEN_Y/1.25)
    window.blit(score_surface, score_rect)

while True:
    msg = {
        'x' : acc.Input.getX(),
        'y' : acc.Input.getY()
    }

    msg_json = json.dumps(msg)
        
    #send the message to the udp server
    client_socket.sendto(msg_json.encode(),(server_name, server_port))

    #return values from the server
    msg_ret, sadd = client_socket.recvfrom(2048)

    #process gameData here
    gameData = json.loads(msg_ret)

    me = gameData['you']

    food_encoded = gameData['food']
    
    food = pygame.Rect(food_encoded[0], food_encoded[1], food_encoded[2], food_encoded[3])

    users = gameData['userlist']

    gameover_state = users[me]['gameover']

    score = users[me]['score']

    #rendering
    window.fill('black')
    for user in users:
        for pos in users[user]['body']:
            pygame.draw.rect(window, SNAKE_COLOUR, pygame.Rect(pos[0], pos[1], SNAKE_WIDTH, SNAKE_WIDTH))

    pygame.draw.rect(window, FOOD_COLOUR, food)

    #game over
    if gamover_state:
        sounds["oopsydaisy"].play()
        gamover()

    #refresh
    show_score(1, SCORE_COLOUR, 'Comic Sans', 20)
    pygame.display.update()

    # limits FPS to 60
    clock.tick(60)

    #show output and close client
    #os.system('cls')
    #print(json.loads(msg))
    #time.sleep(0.01)

