import  Coord
from pygame import Rect
import pygame
class Snake(Rect):
    def __init__(self, colour, width, x, y):
        Rect.__init__(self, x, y, width, width)
        self.colour = colour
        self.width = width
        self.updateHeadHitbox()
        self.tail = []
        self.x=x
        self.y=y
    def updateHeadHitbox(self):
        self.head_hitbox = Rect(self.x, self.y, self.width, self.width)
    
    def render(self,window):
        pygame.draw.rect(window, self.colour, self)
        for pos in self.tail:
            pygame.draw.rect(window, self.colour, pygame.Rect(pos.x, pos.y, self.width, self.width))
    def move (self, coord):
        self.tail.insert(0,coord)
    def pop(self):
        self.tail.pop()