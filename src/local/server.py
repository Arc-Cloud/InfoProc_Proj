import threading
import random
import pygame
from netcode.TCPConnection import TCPConnection
import json
import time
import math
import sys
from database import update_high_score, register_player, get_top_three_scores, add_death, add_kill
import game_pb2
from PIL import Image
import os
from collections import Counter
import numpy as np
import uuid



#select a server port
HOST = '172.31.44.2'
PORT = 12000

ARENA_X = 1000
ARENA_Y = 1000
SCREEN_X= 720
SCREEN_Y=480
INIT_X = 500
INIT_Y = 500
FOOD_RAD = 10
SNAKE_RAD = 10
HEAD_RAD = 15

clock = pygame.time.Clock()

def dict_to_protobuf(data):
    game_data = game_pb2.GameData()
    
    # Convert players
    for player_data in data["players"]:
        player = game_data.players.add()
        player.player_id = player_data["player_id"]
        player.username = player_data["username"]
        player.position.x = player_data["x"]
        player.position.y = player_data["y"]
        player.score = player_data["score"]
        player.dirX = player_data["dirX"]
        player.dirY = player_data["dirY"]
        for body_part in player_data["body"]:
            body_coord = player.body.add()
            body_coord.x = body_part[0]
            body_coord.y = body_part[1]
        player.head_image_path = player_data["head_image_path"]
        player.body_color[:] = player_data["body_color"]
    
    # Convert foods
    for food_data in data["foods"]:
        food = game_data.foods.add()
        food.position.x = food_data["x"]
        food.position.y = food_data["y"]
        food.id = food_data["id"]
    
    # Set game state
    game_data.alive = data["alive"]
    game_data.score = data["score"]
    game_data.food_eaten = data["food_eaten"]
    game_data.boundary_box[:] = data["boundary_box"]
    
    return game_data

# -------------------------------------------------------Get Random Snake----------------------------------------------------------------#


def load_random_snake_head(heads_directory):
    files = [f for f in os.listdir(heads_directory) if f.endswith(('.jpg', '.png'))]
    selected_file = random.choice(files)
    file_path = os.path.join(heads_directory, selected_file)
    return file_path

# ---------------------------------------------------------------------------------------------------------------------------------#


def check_collision_circle(circle1, circle2):
    diffx = circle1[0] - circle2[0]
    diffy = circle1[1] - circle2[1]
    dist = math.sqrt(diffx**2 + diffy**2)
    if dist < circle1[2] + circle2[2]:
        return True
    else:
        return False
    
def check_collision_circle_list(circle, circle_list):
    for c in circle_list:
        if check_collision_circle(circle,c[:3]):
            return c[3]
    return ""

class Player:
    def __init__(self, player_id, username, x, y, head_image_path, body_color):
        self.username = username
        self.player_id = player_id
        self.x = x
        self.y = y
        self.body = [(x,y) for _ in range(0,10)]
        self.score = 0
        self.dirX = 0
        self.dirY = 0
        self.speed = 3
        self.head_image_path = head_image_path  # Path to the head image

    def to_dict(self):
        return {
            "username" : self.username,
            "player_id": self.player_id,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "body": [(round(x,2),round(y,2)) for (x,y) in self.body],
            "score": self.score,
            "dirX" : round(self.dirX, 2),
            "dirY" : round(self.dirY, 2),
            "head_image_path": self.head_image_path,
        }

class Food:
    def __init__(self, x, y, uuid_val=None):
        self.x = x
        self.y = y
        self.id = uuid_val if uuid_val is not None else uuid.uuid4()
        

    def to_dict(self):
        return {
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            'id': str(self.id)
        }

class GameData:
    def __init__(self, heads_directory):
        self.directory = heads_directory
        self.players = {}
        self.foods = [Food(random.randint(FOOD_RAD, ARENA_X - FOOD_RAD), random.randint(FOOD_RAD, ARENA_Y - FOOD_RAD)) for _ in range(0,20)]
        self.lock = threading.Lock()

    def add_player(self, player_id, username):
        print("added player")

        with self.lock:
            not_valid = True
            x,y = 0,0
            while not_valid:
                not_valid = False
                x = random.randint(100, ARENA_X-100)
                y = random.randint(100, ARENA_Y-100)
                for player in self.players.values():
                    dist = math.sqrt((player.x-x)**2 + (player.y-y)**2)
                    if dist < 200:
                        not_valid = True
                        break
            head_image_path = load_random_snake_head(self.directory)
            self.players[player_id] = Player(player_id, username, x, y, head_image_path)  
            

    def remove_player(self, player_id):
        with self.lock:
            if player_id in self.players:
                del self.players[player_id]

    def set_player_speed(self, player_id, speed):
        with self.lock:
            self.players[player_id].speed = speed

    def move_player(self, player_id, x_in, y_in):
        with self.lock:
            if player_id in self.players:
                player = self.players[player_id]
                # Calculate the magnitude of the vector
                magnitude = math.sqrt(x_in**2 + y_in**2)
    
                # Normalize the vector
                if magnitude != 0:
                    x_in /= magnitude
                    y_in /= magnitude
                    player.dirX = x_in
                    player.dirY = y_in
                    
                else: 
                    x_in = player.dirX
                    y_in = player.dirY

                player.x -= x_in * player.speed
                player.y += y_in * player.speed
                player.body.insert(0, (player.x, player.y))
    
    def reduce_player_body(self, player_id):
        with self.lock:
            if player_id in self.players:
                self.players[player_id].body.pop()

    def generate_food(self):
        with self.lock:
            x = random.randint(FOOD_RAD, ARENA_X - FOOD_RAD)
            y = random.randint(FOOD_RAD, ARENA_Y - FOOD_RAD)
            id = uuid.uuid4()
            self.foods.append(Food(x, y, id))

    def check_collision_player(self, player_id) -> bool:
        player = self.players[player_id]
        player_head_circle = (player.x, player.y,SNAKE_RAD)
        
        all_player_bodies = []
        for other_player in self.players.values():
            if other_player.player_id != player_id:
                for index, segment in enumerate(other_player.body):
                    if index == 0:
                        all_player_bodies.append((segment[0],segment[1],HEAD_RAD, other_player.username))
                    else:
                        all_player_bodies.append((segment[0],segment[1],SNAKE_RAD, other_player.username))
        Killer = check_collision_circle_list(player_head_circle, all_player_bodies)
        if Killer != "":
            for index, body in enumerate(player.body):
                if (len(self.foods) < 100 and index % 5==0):
                    self.foods.append(Food(body[0], body[1]))
            add_kill(Killer)
            print("player colision " + str(player_id))
            return True
        if (player.x < SNAKE_RAD or player.x > ARENA_X-SNAKE_RAD or player.y < SNAKE_RAD or player.y > ARENA_Y-SNAKE_RAD):
            for index, body in enumerate(player.body):
                if (len(self.foods) < 100 and index % 5==0):
                    self.foods.append(Food(body[0], body[1]))
            print("wall collision " + str(player_id))
            return True
        return False
    
    def render_to_player(self, player_id):
        centerx = self.players[player_id].x
        centery = self.players[player_id].y
        return_dict = self.to_dict()
        for player in return_dict['players']:
            player['x'] = round(player['x'] - centerx+SCREEN_X//2,1)
            player['y'] = round(player['y'] - centery+SCREEN_Y//2,1)
            player['body'] = [(round(x-centerx+SCREEN_X//2,1), round(y-centery+SCREEN_Y//2,1)) for x,y in player['body'] if x > centerx - SCREEN_X//2 - HEAD_RAD and x < centerx + SCREEN_X//2 + HEAD_RAD and y < centery + SCREEN_Y//2 + HEAD_RAD and y > centery - SCREEN_Y//2 - HEAD_RAD]
        tmp_array = []
        for player in return_dict['players']:
            if len(player['body']) != 0:
                tmp_array.append(player)
        return_dict['players'] = tmp_array

        tmp_array = []
        for food in return_dict['foods']:
            x = food['x']
            y = food['y']
            if x > centerx - SCREEN_X//2 - HEAD_RAD and x < centerx + SCREEN_X//2 + HEAD_RAD and y < centery + SCREEN_Y//2 + HEAD_RAD and y > centery - SCREEN_Y//2 - HEAD_RAD:
                food['x'] = round(food['x'] - centerx+SCREEN_X//2,1)
                food['y'] = round(food['y'] - centery+SCREEN_Y//2,1)
                tmp_array.append(food)
        return_dict['foods'] = tmp_array
        return return_dict, (round(SCREEN_X//2-centerx,1), round(SCREEN_Y//2-centery,1))

    
    def check_eat_food(self, player_id):
        player = self.players[player_id]
        player_head_circle = (player.x,player.y,SNAKE_RAD)
        food_circles = [(food.x, food.y, FOOD_RAD) for food in self.foods]
        for index, food_circle in enumerate(food_circles):
            if check_collision_circle(player_head_circle,food_circle):
                with self.lock:
                    self.foods.pop(index)
                    player.score += 1
                if (len(self.foods) < 50):
                    self.generate_food()
                return True
        self.reduce_player_body(player_id)
        return False


    def to_dict(self):
        return {
            "players": [player.to_dict() for player in self.players.values()],
            "foods": [food.to_dict() for food in self.foods]
        }

class ServerThread(threading.Thread):
    def __init__(self, connection: TCPConnection, player_id: int, game_data: GameData):
        super().__init__()
        self.connection = connection
        self.game_data = game_data
        self.player_id = player_id
        self.alive = True
        no_username = True
        while(no_username):
            client_input = self.connection.recv(self.player_id)
            if client_input:
                json_msg = client_input.decode()
                msg = json.loads(json_msg)
                username = msg["username"]
                if username == "":
                    username = "Guest"+str(self.player_id)
                no_username = False
                self.game_data.add_player(player_id, username)
                register_player(username)
                self.username = username
                # except:
                #     continue

    def run(self):
        while self.connection.isAlive(self.player_id):
            if not self.alive:
                update_high_score(self.username, self.game_data.players[self.player_id].score)
                add_death(self.username)
                leaderboard = get_top_three_scores()
                leaderboard_msg = json.dumps(leaderboard)
                print(leaderboard_msg)
                self.connection.send(leaderboard_msg.encode(), self.player_id)
                time.sleep(0.1)
                print("remove player")
                self.game_data.remove_player(self.player_id)
                self.connection.clients[self.player_id].close()
                self.connection.is_alive[1][self.player_id] = False
            try:
                client_input = self.connection.recv(self.player_id).decode()
                curr = 0
                for ind, char in enumerate(client_input):
                    if char == '{':
                        curr+=1
                    elif char == '}':
                        curr-=1
                    if curr == 0:
                        client_input = client_input[:ind+1]

                if client_input != "":
                    json_msg = client_input
                    try:
                        msg = json.loads(json_msg)
                        x = msg["x"]
                        y = msg["y"]
                        speed = msg["speed"]
                        self.game_data.set_player_speed(self.player_id, speed)
                        self.game_data.move_player(self.player_id, x, y)
                        eaten = self.game_data.check_eat_food(self.player_id)
                        collide = self.game_data.check_collision_player(self.player_id)
                        if collide:
                            self.alive = False
                        game_state, boundary_box = self.game_data.render_to_player(self.player_id)
                        game_state['alive'] = self.alive
                        game_state['score'] = self.game_data.players[self.player_id].score
                        game_state['food_eaten'] = eaten
                        game_state['boundary_box'] = boundary_box
                        #msg_out = json.dumps(game_state)
                        msg_out = dict_to_protobuf(game_state)
                        #print(msg_out.SerializeToString())
                        self.connection.send(msg_out.SerializeToString(), self.player_id)
                    except:
                        print("failed")
                        print(json_msg)
                else:
                    sys.exit()
            except:
                sys.exit()
        

def main():

    image_directory = "media/AccelitherHeads"
    game_data = GameData(heads_directory=image_directory)

    server = TCPConnection(HOST, PORT, host=True)
    server.setMaxClients(5)
    while server.isAlive():
        client_index = server.acceptNewClient()
        if client_index is not None:
            server_thread = ServerThread(server, client_index, game_data)
            server_thread.start()
        #print(game_data.to_dict())
        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")
