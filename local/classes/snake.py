from .Geometry import Coord, Rect
import pygame

class Snake(Rect):
    def __init__(self, colour, width, x, y, length):
        Rect.__init__(self, x, y, width, width)
        self.colour = colour
        self.length = length
        self.tail = []
        "Snake's tail, stored as `pygame.Rect`s. Element 0 is closest to body."
    
    def move(self, x, y):
        if not (x==0 and y==0):
            self.tail.insert(0, self.asPygameRect())
            while len(self.tail) > self.length: self.shrink()
            Rect.move(self, x, y)
        else:
            while len(self.tail) > self.length: self.shrink()
            
    def shrink(self):
        "Removes last segment of tail."
        self.tail.pop()
        
    def render(self, window):
        pygame.draw.ellipse(window, self.colour, self.asPygameRect())
        for segment in self.tail:
            pygame.draw.rect(window, self.colour, segment)