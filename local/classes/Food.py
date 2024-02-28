import random
from pygame import Rect
import pygame

class Food(Rect):
    def __init__(self, colour, width, floor, coord = None):
        if coord == None: coord = floor.getRandomCoord()
        Rect.__init__(random.randint(0, floor.x - width),
                      random.randint(0, floor.y - width),
                      self.width, self.width)
        self.colour = colour
        self.coord = coord
        self.floor=floor
    def render(self,floor):
         pygame.draw.rect(floor, self.colour,self.coord)