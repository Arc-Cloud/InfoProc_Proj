from .Geometry import Rect
import pygame

class Food(Rect):
    def __init__(self, colour, width, coord):
        Rect.__init__(self, coord.x, coord.y, width, width)
        self.colour = colour
        self.coord = coord

    def render(self, window):
         pygame.draw.ellipse(window, self.colour, self.asPygameRect())
    