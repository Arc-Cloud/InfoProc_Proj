import random
from .Geometry import Rect

class Floor():
    "The floor that the snakes and foods exist on."

    def __init__(self, colour, w, h):
        self.colour = colour
        self.w = w
        self.h = h

    def getRandomCircle(self, r):
        "Gets a random circle with a given radius."
        # COMPLETE
        
    def getRandomRect(self, w, h):
        "Gets a random rectangle with a given height and width."
        return Rect(random.randint(0, self.w - w - 1),
                    random.randint(0, self.h - h - 1),
                    w, h)

    def render(self, screen):
        screen.fill(self.colour)