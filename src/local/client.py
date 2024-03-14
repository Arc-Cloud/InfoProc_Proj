import pygame
import json
import de10 as acc
from netcode.TCPConnection import TCPConnection
import time
import math
import game_pb2
import os
import sys
import random
import colorsys
from PIL import Image
import numpy as np
from collections import Counter


# Server IP address and port
HOST = '3.8.153.70'
PORT = 12000

# Screen dimensions
SCREEN_X = 720
SCREEN_Y = 480

# Snake and food dimensions
SCORE_COLOUR = (255, 0, 247)
FOOD_RAD = 10
SNAKE_RAD = 10
HEAD_RAD = 15
BASE_SPEED = 3

STATE_RUNNING = 0
STATE_GAME_OVER = 1
STATE_RESTART = 2
STATE_QUIT = 3

food_id_to_image = {}

pygame.init()
clock = pygame.time.Clock()

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_X, SCREEN_Y))
pygame.display.set_caption('Snake Game Client')

sounds = { "omnom" : pygame.mixer.Sound("media/sounds/sound_effects/eat_sound.mp3"),
           "oopsydaisy" : pygame.mixer.Sound("media/sounds/sound_effects/collision_sound.mp3"),
           "womp_womp" : pygame.mixer.Sound("media/sounds/sound_effects/womp-womp.mp3")
         }

# -----------------------------------------------Login Screen-----------------------------------------------------------#

def protobuf_to_dict(protobuf_message):
    result = {
        "players": [],
        "foods": [],
        "alive": protobuf_message.alive,
        "score": protobuf_message.score,
        "food_eaten": protobuf_message.food_eaten,
        "boundary_box": tuple(protobuf_message.boundary_box),
    }
    
    # Convert players
    for player in protobuf_message.players:
        player_data = {
            "player_id": player.player_id,
            "username": player.username,
            "x": player.position.x,
            "y": player.position.y,
            "score": player.score,
            "dirX": player.dirX,
            "dirY": player.dirY,
            "body": [(coord.x, coord.y) for coord in player.body],
            "head_image_path" : player.head_image_path,
            "body_color" : tuple(player.body_color)
        }
        result["players"].append(player_data)
    
    # Convert foods
    for food in protobuf_message.foods:
        food_data = {"x": food.position.x, "y": food.position.y, "id": food.id }
        result["foods"].append(food_data)
    
    return result

def load_frames(directory, screen):
    frames = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.jpg'):
            path = os.path.join(directory, filename)
            frame = pygame.image.load(path).convert()
            frame = pygame.transform.scale(frame, screen.get_size())  # Scale frame to fit screen
            frames.append(frame)
    return frames

def play_frames(frames, screen):
    clock = pygame.time.Clock()
    for frame in frames:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        clock.tick(30)  # Control frame rate
    return frames[-1]  # Return the last frame

def input_username(screen, last_frame=None):

    # Set up fonts
    font = pygame.font.SysFont(None, 32)

    username = ""

    box_width = 400
    box_height = 50
    x_position = (SCREEN_X - box_width) // 2
    y_position = (SCREEN_Y - box_height) // 1.5
    input_rect = pygame.Rect(x_position, y_position, box_width, box_height)
    active = False

    input_box_color = (255, 255, 255)  
    text_color = (255, 255, 255) 

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return username
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode

        if last_frame is not None:
            screen.blit(last_frame, (0, 0))
        else:
            screen.fill((0, 0, 0))
        
        # Draw input box
        pygame.draw.rect(screen, input_box_color, input_rect, 2)  # Change border color here
        
        # Render and draw username text
        text_surface = font.render(username, True, text_color)  # Adjust text color here
        text_width, text_height = font.size(username)
        text_x = input_rect.x + (input_rect.width - text_width) // 2
        text_y = input_rect.y + (input_rect.height - text_height) // 2

        screen.blit(text_surface, (text_x, text_y))
        
        pygame.display.flip()


# ---------------------------------------------------Music--------------------------------------------------------#
def intro_music(loop=True):
    intro_music_path = "media/sounds/intro_music/the-republic-zac-tiessen-main-version-21765-01-46.mp3"
    pygame.mixer.music.load(intro_music_path)
    if loop:
        pygame.mixer.music.play(-1)  # Play music in a loop
    else:
        pygame.mixer.music.play()

def load_playlist(directory):
    # Scan the directory for mp3 files and return the list
    songs = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.mp3')]
    random.shuffle(songs)  # Shuffle the playlist
    return songs

def setup_music_end_event():
    # Define a custom event for when a music track ends
    MUSIC_END = pygame.USEREVENT+1
    pygame.mixer.music.set_endevent(MUSIC_END)
    return MUSIC_END

def play_next_song(songs, current_song_index):
    # If there are no songs, just return
    if not songs:
        return
    # Load and play the current song, wrap around the list if needed
    pygame.mixer.music.load(songs[current_song_index % len(songs)])
    pygame.mixer.music.play()
# ----------------------------------------------------------------------------------------------------------------#

def blitRotate(surf, image, origin, pivot, angle):
    image_rect = image.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = pygame.math.Vector2(origin) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotozoom(image, 180 + angle, 0.05)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect)

def get_angle(x, y):
    
    # Calculate the angle using arctangent (in radians) and convert to degrees
    angle_rad = math.atan2(y, x)  # Note the negative sign for y
    angle_deg = math.degrees(angle_rad)

    return angle_deg-90


def show_score(choice, colour, font, size, score):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, colour)
    score_rect = score_surface.get_rect()
    score = str(score).zfill(6)
    acc.Input.set7Seg(0,(0,0,0,0,0,0,0))
    acc.Input.set7Seg(1,(0,0,0,0,0,0,0))
    acc.Input.set7Seg(2,(0,0,0,0,0,0,0))
    acc.Input.set7Seg(3,str(score)[-3])
    acc.Input.set7Seg(4,str(score)[-2])
    acc.Input.set7Seg(5,str(score)[-1])
    if choice == 1:
        score_rect.midtop = (SCREEN_X/10, 15)
    else:
        score_rect.midtop = (SCREEN_X/2, SCREEN_Y/1.25)
    screen.blit(score_surface, score_rect)

# ------------------------------------------------GameOverLog---------------------------------------------------------------#

def gamover(score, connection):
    print("enter gameover")
    sounds["oopsydaisy"].play()
    my_font = pygame.font.SysFont('Times New Roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, (252,3,3) )
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (SCREEN_X/2, SCREEN_Y/4)
    screen.fill((10,10,10))
    screen.blit(game_over_surface, game_over_rect)
    show_score(0, (252,3,3), 'Comic Sans', 20, score)

    # Display leaderboard data
    font = pygame.font.SysFont('Times New Roman', 32)
    y_offset = SCREEN_Y/2

    leaderboard_data_json = {}
    not_valid = True
    while not_valid:
        try: 
            leaderboard_data = connection.recv(timeout=0.5)
            leaderboard_data_json = json.loads(leaderboard_data.decode())
            print(leaderboard_data_json[0]['HighScore'])
            not_valid = False
        except:
            continue

    for rank, score_dict in enumerate(leaderboard_data_json, start=1):
        rank_text = font.render(str(rank), True, (252,3,3))
        screen.blit(rank_text, (50, y_offset))
        username_text = font.render(score_dict['PlayerId'], True, (252,3,3))
        screen.blit(username_text, (100, y_offset))
        score_text = font.render(str(score_dict['HighScore']), True, (252,3,3))
        screen.blit(score_text, (300, y_offset))
        y_offset += 30    
    
    pygame.display.flip()
    sounds["womp_womp"].play()
    time.sleep(2)

    button_width = 200
    button_height = 50
    margin = 10  # Margin from the screen edges

    restart_button = pygame.Rect(SCREEN_X - button_width - margin, SCREEN_Y - button_height - margin, button_width, button_height)
    quit_button = pygame.Rect(margin, SCREEN_Y - button_height - margin, button_width, button_height)

    pygame.draw.rect(screen, (0, 255, 0), restart_button)  # Draw restart button green
    pygame.draw.rect(screen, (255, 0, 0), quit_button)  # Draw quit button red

    font = pygame.font.SysFont(None, 36)
    blit_text_center(screen, 'Restart', font, restart_button)
    blit_text_center(screen, 'Quit', font, quit_button)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if restart_button.collidepoint(mouse_pos):
                    return 'restart'
                elif quit_button.collidepoint(mouse_pos):
                    return 'quit'


    
    # pygame.quit()


# -----------------------------------------------Drawing -----------------------------------------------------------#

def blit_text_center(screen, text, font, rect):
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    
def draw_grid_background(screen, grid_color=(56, 56, 56), grid_spacing=20):
   
    screen_width, screen_height = screen.get_size()
    
    # Draw vertical lines
    for x in range(0, screen_width, grid_spacing):
        pygame.draw.line(screen, grid_color, (x, 0), (x, screen_height))
    
    # Draw horizontal lines
    for y in range(0, screen_height, grid_spacing):
        pygame.draw.line(screen, grid_color, (0, y), (screen_width, y))


def draw_scaled_segment(screen, color, complement_color, position, radius):
    # Draw the base circle
    pygame.draw.circle(screen, color, position, radius)
    
    num_scales = 8  # Adjust the number of scales 
    scale_radius = radius // num_scales * 2  # Radius of the scales
    
    # Adjusted the angle to make sure we cover the circle in a radial pattern
    for angle in range(0, 360, 360 // num_scales):
        angle_rad = math.radians(angle)  
        for r in range(scale_radius, radius, scale_radius):  # Start at scale_radius to avoid center and go to the edge
            scale_x = int(position[0] + r * math.cos(angle_rad))
            scale_y = int(position[1] + r * math.sin(angle_rad))
            
            # Draw the scale if it's within the circle's boundary
            dist_to_center = math.sqrt((scale_x - position[0]) ** 2 + (scale_y - position[1]) ** 2)
            if dist_to_center + scale_radius / 2 <= radius:
                pygame.draw.circle(screen, complement_color, (scale_x, scale_y), scale_radius // 2)


def get_complementary_color(rgb):
    r, g, b = [x / 255.0 for x in rgb]
    
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    h = (h + 0.5) % 1.0
    
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    
    return tuple(int(x * 255) for x in (r, g, b))


def get_most_common_color(image_path):
    image = Image.open(image_path)
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    pixels = np.array(image)

    # Filter out fully transparent pixels
    pixels = pixels.reshape(-1, 4)
    pixels = pixels[pixels[:, 3] > 0][:, :3]  # Drop the alpha channel information

    # Count colors
    colors = Counter(map(tuple, pixels))

    # Define a threshold for non-black colors
    non_black_threshold = 50

    # Filter out colors that are black or close to black
    colors = {color: count for color, count in colors.items() if all(value > non_black_threshold for value in color)}

    # Find the most common non-black color, defaulting to a placeholder if none are found
    most_common_non_black_color = max(colors, key=colors.get) if colors else (255, 255, 255)  # Default to white if no non-black color is found

    return tuple(map(int, most_common_non_black_color))

# -----------------------------------------------Load Images-----------------------------------------------------------#
image_cache = {}

def load_player_images(directory="media/AccelitherHeads"):
    for filename in os.listdir(directory):
        if filename.endswith('.png'):  # Assuming all images are PNGs
            path = os.path.join(directory, filename)
            try:
                image = pygame.image.load(path).convert_alpha()
                image_cache[path] = image  # Store the image with its path as the key
            except pygame.error as e:
                print(f"Error loading image: {path}. Error: {e}")

                
def load_player_image(image_path):
    if image_path in image_cache:
        return image_cache[image_path]
    try:
        image = pygame.image.load(image_path).convert_alpha()
        image_cache[image_path] = image  
        return image
    except pygame.error:
        print(f"Error loading image: {image_path}")
        # Return a default image if the desired one fails to load
        return pygame.Surface((HEAD_RAD*2, HEAD_RAD*2), pygame.SRCALPHA)
    

def load_and_resize_food_images(directory, size):
    food_images = []
    for filename in os.listdir(directory):
        if filename.endswith('.png'):  # Assuming the images are PNGs
            path = os.path.join(directory, filename)
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, size)
            food_images.append(image)
    return food_images

food_images_resized = load_and_resize_food_images('media/Food', (2 * FOOD_RAD, 2 * FOOD_RAD))

# -------------------------------------------------------Render Game----------------------------------------------------------------#


# Function to render game state
def render_game_state(screen, game_state):
    # Clear the screen
    screen.fill((0, 0, 0))
    draw_grid_background(screen)

    for player_data in game_state['players']:
        snake_head_path = player_data['head_image_path']
        snake_head = load_player_image(snake_head_path) 
        username = player_data['username']
        dirX = player_data['dirX']
        dirY = player_data['dirY']
        body_color = get_most_common_color(snake_head_path)
        complement_color = get_complementary_color(body_color)
        #print(body_color)
    
        for index, segment in enumerate(reversed(player_data['body'])):
            if index == len(player_data['body'])-1:  # Draw the head of the snake
                blitRotate(screen, snake_head, segment, (256,256), get_angle(dirX,dirY))
            else:
                segment_pos = (int(segment[0]), int(segment[1]))
                draw_scaled_segment(screen, body_color, complement_color, segment_pos, SNAKE_RAD)
                #pygame.draw.circle(screen, body_color, segment, SNAKE_RAD)

                
        font = pygame.font.SysFont(None, 24)
        text_surface = font.render(username, True, complement_color)
        headx = player_data['body'][0][0]
        heady = player_data['body'][0][1]
        text_rect = text_surface.get_rect(center=(headx, heady-30))
        screen.blit(text_surface,text_rect)
    
    pygame.draw.rect(screen, (255,255,255), pygame.Rect(game_state['boundary_box'][0], game_state['boundary_box'][1], 1000, 1000), 3)

    if (game_state['food_eaten']):
        sounds['omnom'].play()

    # Render food
    foods = game_state['foods']
    for food in foods:
        if food['id'] not in food_id_to_image:
            food_id_to_image[food['id']] = random.choice(food_images_resized)
        
        food_image = food_id_to_image[food['id']]
        screen.blit(food_image,(food['x'] - FOOD_RAD, food['y'] - FOOD_RAD))

    current_food_uuids = set(food['id'] for food in game_state["foods"])
    uuids_to_remove = [uuid for uuid in food_id_to_image if uuid not in current_food_uuids]
    for uuid in uuids_to_remove:
        del food_id_to_image[uuid]

    if(acc.Input.getSwitch(0)):
        acc.Input.setLED(0, True)
        show_score(1, SCORE_COLOUR, 'Comic Sans', 20, game_state['score'])
    elif(acc.Input.getSwitch(0) == False):
        acc.Input.setLED(0, False)
    
    # Update the display
    pygame.display.flip()


# -----------------------------------------------Reset Game-----------------------------------------------------------#
    

def reset_game(connection, username, songs, current_song_index):    #### Reset ####
    
    
    if connection is not None:
        connection.close()  
    
    current_song_index = [0]  
    # do we need to reset player related states?
    # e.g., player position, score, etc.
    pygame.mixer.music.stop()
    # Any other game state resets?

    if connection is not None:
        connection.close()  
        connection = None

    ### Start again ####

    intro_music()
    frames_directory = 'media/AccelitherLogin' 
    frames = load_frames(frames_directory, screen) # comment out to quickly login
    last_frame = play_frames(frames, screen) # comment out to quickly login
    load_player_images()
    username = input_username(screen, last_frame) # remove screen argument to quickly login 
    pygame.mixer.music.stop()
    
    # Initialize the TCP connection
    connection = TCPConnection(HOST, PORT)

    msg = {
        'username' : username,
        'x' : acc.Input.getX(),
        'y' : acc.Input.getY(),
        'speed': BASE_SPEED+acc.Input.getButton(0)*2-acc.Input.getButton(1)*2}
    
    msg_json = json.dumps(msg)

    connection.send(msg_json.encode())

    # Initialize music
    songs = load_playlist('media/sounds/ingame_music')
    current_song_index = [0]  
    MUSIC_END = setup_music_end_event()
    play_next_song(songs, current_song_index[0])
    

    time.sleep(1)

    return connection, username, songs, current_song_index

    





# -----------------------------------------------Main-----------------------------------------------------------#


# Main function to run the client
def main():
    
 ######## Initialisation ########
    
    intro_music()
    frames_directory = 'media/AccelitherLogin' 
    frames = load_frames(frames_directory, screen) # comment out to quickly login
    last_frame = play_frames(frames, screen) # comment out to quickly login
    load_player_images()
    username = input_username(screen, last_frame) # remove screen argument to quickly login 
    pygame.mixer.music.stop()
    
    # Initialize the TCP connection
    connection = TCPConnection(HOST, PORT)

    msg = {
        'username' : username,
        'x' : acc.Input.getX(),
        'y' : acc.Input.getY(),
        'speed': BASE_SPEED+acc.Input.getButton(0)*2-acc.Input.getButton(1)*2}
    
    msg_json = json.dumps(msg)

    connection.send(msg_json.encode())

    # Initialize music
    songs = load_playlist('media/sounds/ingame_music')
    current_song_index = [0]  # Using a list to allow modification in nested scope
    MUSIC_END = setup_music_end_event()
    play_next_song(songs, current_song_index[0])
    

    time.sleep(1)


    state = STATE_RUNNING

    # Main loop
    while True:
        if state == STATE_RUNNING:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    state = STATE_QUIT
                elif event.type == MUSIC_END:
                    # When one song ends, play the next
                    current_song_index[0] += 1 
                    play_next_song(songs, current_song_index[0])

            msg = {
            'username' : username,
            'x' : acc.Input.getX(),
            'y' : acc.Input.getY(),
            'speed': BASE_SPEED+acc.Input.getButton(0)*2-acc.Input.getButton(1)*2}

            msg_json = json.dumps(msg)
            
            #send the message to the udp server
            connection.send(msg_json.encode())

            # Receive game state from the server
            
            game_state_json = connection.recv(timeout=0.1)
            try:
                received_game_data = game_pb2.GameData()
                received_game_data.ParseFromString(game_state_json)
            except:
                continue
            '''
            curr = 0
            for ind,char in enumerate(game_state_json):
                if char == '{':
                    curr+=1
                elif char == '}':
                    curr-=1
                if curr == 0:
                    game_state_json = game_state_json[:ind+1]
            '''
            if received_game_data:
                try:
                    #game_state = json.loads(game_state_json)
                    game_state = protobuf_to_dict(received_game_data)
                    score = game_state['score']
                    render_game_state(screen, game_state)
                    if not game_state['alive']:
                        state = STATE_GAME_OVER
                        
                except:
                    print("Sussy baka")
                    continue
            
            
        elif state == STATE_GAME_OVER:
            player_choice = gamover(score, connection)  # Use your updated gamover function here
            connection.close()
            if player_choice == 'quit':
                state = STATE_QUIT
            elif player_choice == 'restart':
                state = STATE_RESTART

        elif state == STATE_RESTART:
            connection, username, songs, current_song_index = reset_game(connection, username, songs, current_song_index)
            state = STATE_RUNNING


        elif state == STATE_QUIT:
            pygame.quit()
            sys.exit()
        

        #pygame.display.flip()
        clock.tick(60)
        

if __name__ == "__main__":
    main()
    sys.exit()
