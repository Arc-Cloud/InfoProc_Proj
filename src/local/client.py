import pygame
import json
import de10 as acc
from netcode.TCPConnection import TCPConnection
import time

# Server IP address and port
HOST = '13.48.57.52'
PORT = 12000

# Screen dimensions
SCREEN_X = 720
SCREEN_Y = 480

# Snake and food dimensions
SCORE_COLOUR = (255, 0, 247)
FOOD_RAD = 10
SNAKE_RAD = 10
HEAD_RAD = 15
speed = 5

# Initialize pygame
pygame.init()
clock = pygame.time.Clock()

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
pygame.display.set_caption('Snake Game Client')

sounds = { "omnom" : pygame.mixer.Sound("eat_sound.mp3"),
           "oopsydaisy" : pygame.mixer.Sound("collision_sound.mp3"),
           "womp_womp" : pygame.mixer.Sound("womp-womp.mp3")
         }

def show_score(choice, colour, font, size, score):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, colour)
    score_rect = score_surface.get_rect()
    acc.Input.set7Seg(0,(0,0,0,0,0,0,0))
    acc.Input.set7Seg(1,(0,0,0,0,0,0,0))
    acc.Input.set7Seg(2,(0,0,0,0,0,0,0))
    acc.Input.set7Seg(3,(0,0,0,0,0,0,0))
    acc.Input.set7Seg(4,str(score//10))
    acc.Input.set7Seg(5,str(score%10))
    if choice == 1:
        score_rect.midtop = (SCREEN_X/10, 15)
    else:
        score_rect.midtop = (SCREEN_X/2, SCREEN_Y/1.25)
    screen.blit(score_surface, score_rect)

def gamover(score):
    sounds["oopsydaisy"].play()
    my_font = pygame.font.SysFont('Times New Roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, (252,3,3) )
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (SCREEN_X/2, SCREEN_Y/4)
    screen.fill((10,10,10))
    screen.blit(game_over_surface, game_over_rect)
    show_score(0, (252,3,3), 'Comic Sans', 20, score)
    pygame.display.flip()
    sounds["womp_womp"].play()
    time.sleep(5)
    pygame.quit()

# Function to render game state
def render_game_state(screen, game_state):
    # Clear the screen
    screen.fill((0, 0, 0))

    # Render players
    for player_data in game_state['players']:
        for segment in player_data['body']:
            pygame.draw.circle(screen, (255, 255, 255), (segment[0], segment[1]), SNAKE_RAD)

    # Render food
    food = game_state['food']
    if (game_state['food_eaten']):
        sounds['omnom'].play()
    pygame.draw.circle(screen, (255, 0, 0), (food['x'], food['y']), FOOD_RAD)
    show_score(1, SCORE_COLOUR, 'Comic Sans', 20, game_state['score'])

    # Update the display
    pygame.display.flip()

# Main function to run the client
def main():

    # Initialize the TCP connection
    connection = TCPConnection(HOST, PORT)

    # Main loop
    while True:
        msg = {
        'x' : acc.Input.getX(),
        'y' : acc.Input.getY(),
        'speed': speed+acc.Input.getButton(0)*3-acc.Input.getButton(1)*3}
        print(msg)

        msg_json = json.dumps(msg)
        
        #send the message to the udp server
        connection.send(msg_json.encode())

        # Receive game state from the server
        game_state_json = connection.recv(timeout=0.1)
        if game_state_json:
            game_state = json.loads(game_state_json)
            score = game_state['score']
            render_game_state(screen, game_state)
            if not game_state['alive']:
                connection.close()
                gamover(score)
                exit()

        # Tick the clock
        clock.tick(60)

if __name__ == "__main__":
    main()
