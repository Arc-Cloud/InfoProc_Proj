import pygame
class floor():
    def _init_(self,colour,sizex,sizey,screensizex,screensizey):
        self.screenx=screensizex
        self.screensizey=screensizey
        self.x=sizex
        self.y=sizey
        

    def render(self):
        self.fill(self.colour)
        