import threading
import random
import pygame
from netcode.TCPConnection import TCPConnection
import json

#select a server port
HOST = '172.31.47.170'
PORT = 12000

SCREEN_X= 720
SCREEN_Y=480
INIT_X = 100.0
INIT_Y = 50.0
FOOD_WIDTH = 20
SNAKE_WIDTH = 20

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

    def to_dict(self):
        return {
            "player_id": self.player_id,
            "x": self.x,
            "y": self.y,
            "body": self.body,
            "score": self.score
        }

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y
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
                self.players[player_id].x -= x_in * 10
                self.players[player_id].y += y_in * 10
                self.players[player_id].body.insert(0, (self.players[player_id].x, self.players[player_id].y))
                self.players[player_id].body_rect.insert(0, pygame.Rect(x_in, y_in, SNAKE_WIDTH, SNAKE_WIDTH))
    
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

    def check_collisions(self, player_id) -> bool:
        player = self.players[player_id]
        player_head_rect = pygame.Rect(player.x,player.y,SNAKE_WIDTH,SNAKE_WIDTH)
        food_rect = pygame.Rect(self.food.x, self.food.y, FOOD_WIDTH, FOOD_WIDTH)

        if player_head_rect.colliderect(food_rect):
            self.generate_food()
            player.score += 1
        else: 
            self.reduce_player_body(player_id)
        
        all_player_bodies = [rect for player in self.players.values() for rect in player.body_rect]
        if (player_head_rect.collidelist(all_player_bodies) != -1):
            return True
        if (player.x < 0 or player.x > SCREEN_X-SNAKE_WIDTH or player.y < 0 or player.y > SCREEN_Y-SNAKE_WIDTH):
            return True
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
        while self.connection.isAlive(self.player_id) and self.alive:
            print("alive!")
            client_input = self.connection.recv(self.player_id)
            if client_input:
                
                json_msg = client_input.decode()
                msg = json.loads(json_msg)
                x = msg["x"]
                y = msg["y"]
                self.game_data.move_player(self.player_id, x, y)
                collide = self.game_data.check_collisions(self.player_id)
                if collide:
                    print("collide??")
                    self.alive = False
                    self.game_data.remove_player(self.player_id)
                game_state = self.game_data.to_dict()
                print("before sending")
                print(game_state)
                game_state['alive'] = self.alive
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
