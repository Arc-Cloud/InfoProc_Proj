import  Coord
from pygame import Rect
import pygame
class Snake(Coord):
    def __init__(self, colour, width, x, y):
        Coord.__init__(self, x, y)
        self.colour = colour
        self.width = width
        self.updateHeadHitbox()
        self.tail = []
    
    def updateHeadHitbox(self):
        self.head_hitbox = Rect(self.x, self.y, self.width, self.width)
    def render(self,floor):
        for pos in self.tail:
            pygame.draw.rect(floor, self.colour, pygame.Rect(pos.x, pos.y, self.width, self.width))