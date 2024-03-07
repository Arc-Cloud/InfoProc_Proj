import pygame
import json
import de10 as acc
from netcode.TCPConnection import TCPConnection

# Server IP address and port
HOST = '13.48.57.52'
PORT = 12000

# Screen dimensions
SCREEN_X = 720
SCREEN_Y = 480

# Snake and food dimensions
SNAKE_WIDTH = 20
FOOD_WIDTH = 20

# Initialize pygame
pygame.init()
clock = pygame.time.Clock()

# Function to render game state
def render_game_state(screen, game_state):
    # Clear the screen
    screen.fill((0, 0, 0))

    # Render players
    for player_data in game_state['players']:
        for segment in player_data['body']:
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(segment[0], segment[1], SNAKE_WIDTH, SNAKE_WIDTH))

    # Render food
    food = game_state['food']
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(food['x'], food['y'], FOOD_WIDTH, FOOD_WIDTH))
    acc.Input.set7Seg(1,2)

    # Update the display
    pygame.display.flip()

# Main function to run the client
def main():
    # Initialize the screen
    screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
    pygame.display.set_caption('Snake Game Client')

    # Initialize the TCP connection
    connection = TCPConnection(HOST, PORT)

    # Main loop
    while True:
        msg = {
        'x' : acc.Input.getX(),
        'y' : acc.Input.getY()}

        msg_json = json.dumps(msg)
        
        #send the message to the udp server
        connection.send(msg_json.encode())

        # Receive game state from the server
        game_state_json = connection.recv(timeout=0.1)
        if game_state_json:
            game_state = json.loads(game_state_json)
            render_game_state(screen, game_state)

        # Tick the clock
        clock.tick(60)

if __name__ == "__main__":
    main()
