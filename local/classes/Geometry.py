import pygame

class Coord():
    "X and Y coordinates."
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, x_off, y_off):
        self.x += x_off
        self.y += y_off

class Rect(Coord):
    "X and Y coordinates (top-left) and width and height."
    def __init__(self, x, y, w, h):
        Coord.__init__(self, x, y)
        self.w = w
        self.h = h

    def asPygameRect(self):
        "Returns equivalent `pygame.Rect`."
        return pygame.Rect(self.x, self.y, self.w, self.h)

class Circle(Coord):
    "X and Y coordinates (center) and radius."
    def __init__(self, x, y, r):
        Coord.__init__(self, x, y)
        self.x = x
        self.y = y
    
        
