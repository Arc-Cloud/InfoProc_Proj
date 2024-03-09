import threading
import random
import pygame
from netcode.TCPConnection import TCPConnection
import json
import time
import math

#select a server port
HOST = '172.31.47.170'
PORT = 12000

SCREEN_X= 720
SCREEN_Y=480
INIT_X = 100.0
INIT_Y = 50.0
FOOD_WIDTH = 15
SNAKE_WIDTH = 20
SPEED = 5

pygame.init()
clock = pygame.time.Clock()

class Player:
    def __init__(self, player_id, x, y):
        self.player_id = player_id
        self.x = x
        self.y = y
        self.body = [(x,y)]
        self.body_rect = [pygame.Rect(x,y,SNAKE_WIDTH,SNAKE_WIDTH)]
        self.score = 0
        self.dirX = 0
        self.dirY = 0

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "body": [(round(x,2),round(y,2)) for (x,y) in self.body],
            "score": self.score
        }

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_dict(self):
        return {
            "x": round(self.x, 2),
            "y": round(self.y, 2)
        }

class GameData:
    def __init__(self):
        self.players = {}
        self.food = Food(random.randint(0, SCREEN_X - FOOD_WIDTH), random.randint(0, SCREEN_Y - FOOD_WIDTH))
        self.lock = threading.Lock()

    def add_player(self, player_id, x, y):
        with self.lock:
            self.players[player_id] = Player(player_id, x, y)

    def remove_player(self, player_id):
        with self.lock:
            if player_id in self.players:
                del self.players[player_id]

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

                player.x -= x_in * SPEED
                player.y += y_in * SPEED
                player.body.insert(0, (player.x, player.y))
                player.body_rect.insert(0, pygame.Rect(player.x, player.y, SNAKE_WIDTH, SNAKE_WIDTH))
    
    def reduce_player_body(self, player_id):
        with self.lock:
            if player_id in self.players:
                self.players[player_id].body.pop()
                self.players[player_id].body_rect.pop()

    def generate_food(self):
        with self.lock:
            x = random.randint(0, SCREEN_X - FOOD_WIDTH)
            y = random.randint(0, SCREEN_Y - FOOD_WIDTH)
            self.food = Food(x, y)

    def check_collision_player(self, player_id) -> bool:
        player = self.players[player_id]
        player_head_rect = pygame.Rect(player.x,player.y,SNAKE_WIDTH,SNAKE_WIDTH)
        
        all_player_bodies = [rect for player in self.players.values() if player.player_id != player_id for rect in player.body_rect]
        if (player_head_rect.collidelistall(all_player_bodies) != []):
            return True
        if (player.x < 0 or player.x > SCREEN_X-SNAKE_WIDTH or player.y < 0 or player.y > SCREEN_Y-SNAKE_WIDTH):
            return True
        return False
    
    def check_eat_food(self, player_id):
        player = self.players[player_id]
        player_head_rect = pygame.Rect(player.x,player.y,SNAKE_WIDTH,SNAKE_WIDTH)
        food_rect = pygame.Rect(self.food.x, self.food.y, FOOD_WIDTH, FOOD_WIDTH)
        if player_head_rect.colliderect(food_rect):
            self.generate_food()
            with self.lock:
                player.score += 1
            return True
        else: 
            self.reduce_player_body(player_id)
            return False


    def to_dict(self):
        return {
            "players": [player.to_dict() for player in self.players.values()],
            "food": self.food.to_dict()
        }

class ServerThread(threading.Thread):
    def __init__(self, connection: TCPConnection, player_id: int, game_data: GameData):
        super().__init__()
        self.connection = connection
        self.game_data = game_data
        self.player_id = player_id
        self.alive = True
        self.game_data.add_player(player_id, INIT_X, INIT_Y)

    def run(self):
        while self.connection.isAlive(self.player_id):
            if not self.alive:
                time.sleep(0.1)
                print("removed player")
                self.game_data.remove_player(self.player_id)
            print("alive!")
            client_input = self.connection.recv(self.player_id)
            # this kills player via TCPConnection
            if client_input:
                json_msg = client_input.decode()
                msg = json.loads(json_msg)
                x = msg["x"]
                y = msg["y"]
                self.game_data.move_player(self.player_id, x, y)
                eaten = self.game_data.check_eat_food(self.player_id)
                collide = self.game_data.check_collision_player(self.player_id)
                if collide:
                    print("collide??")
                    self.alive = False
                game_state = self.game_data.to_dict()
                game_state['alive'] = self.alive
                game_state['score'] = self.game_data.players[self.player_id].score
                game_state['food_eaten'] = eaten
                msg = json.dumps(game_state)
                self.connection.send(msg.encode(), self.player_id)
        

def main():

    game_data = GameData()

    server = TCPConnection(HOST, PORT, host=True)
    server.setMaxClients(3)

    while server.isAlive():
        client_index = server.acceptNewClient()
        if client_index is not None:
            server_thread = ServerThread(server, client_index, game_data)
            server_thread.start()
        print(game_data.to_dict())
        clock.tick(60)

if __name__ == "__main__":
    main()
