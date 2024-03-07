from .Calibration import Calibration
from .Raw import Raw
from math import acos, atan, sqrt, pi

def clamp(a, b):
    if b > 0: return min(a, b)
    else: return max(a, b)

def linMap(val, min, max):
    cent = (max + min) / 2
    off = val - cent
    return clamp(clamp(off / (max - cent), -1), 1)

class InputNS():
    __ZERO_DEADZONE = 0.1 # Bounds within which to assume 0
    __EDGE_DEADZONE = 0.9 # Bounds out of which to assume 1
    __MAX_THRESHOLD = 300 # Bounds out of which to assume 1 (with raw reading)

    def getX(self):
        """
        Gets normalised X reading.
        """
        val = Raw.getX()
        if val >= self.__MAX_THRESHOLD: return 0
        if val <= -self.__MAX_THRESHOLD: return 0

        val = linMap(val, Calibration.min_x, Calibration.max_x)
        if val >= -self.__ZERO_DEADZONE and val <= self.__ZERO_DEADZONE: return 0
        if val >= self.__EDGE_DEADZONE: return 1
        if val <= -self.__EDGE_DEADZONE: return -1
        
        return val

    def getY(self):
        """
        Gets normalised Y reading.
        """
        val = Raw.getY()
        if val >= self.__MAX_THRESHOLD: return 0
        if val <= -self.__MAX_THRESHOLD: return 0

        val = linMap(val, Calibration.min_y, Calibration.max_y)
        if val >= -self.__ZERO_DEADZONE and val <= self.__ZERO_DEADZONE: return 0
        if val >= self.__EDGE_DEADZONE: return 1
        if val <= -self.__EDGE_DEADZONE: return -1
        
        return val
    
    def getZ(self):
        """
        Gets normalised Z reading.
        """
        val = Raw.getZ()
        if val >= self.__MAX_THRESHOLD: return 0
        if val <= -self.__MAX_THRESHOLD: return 0

        val = linMap(val, Calibration.min_z, Calibration.max_z)
        if val >= -self.__ZERO_DEADZONE and val <= self.__ZERO_DEADZONE: return 0
        if val >= self.__EDGE_DEADZONE: return 1
        if val <= -self.__EDGE_DEADZONE: return -1
        
        return val
    
    def getJoystickRaw(self, on_zero_gravity = 99999):
        """
        Gets joystick input. Returns a tuple, (`g`, `mag`, `ang`), where:\n
        `g` = The observed total gravity (should be 1),\n
        `mag` = The observed magnitude,\n
        `ang` = The observed angle.\n
        Note on the angle: If facing the board such that the 'DE10-Lite' text faces you, an angle of
        0 is tilting it forward, and +-pi is tilting it towards you, where
        positive angles are on the right and negative on the left, i.e. it rotates clockwise.
        """

        x = self.getX()
        y = self.getY()
        z = self.getZ()

        g = sqrt((x * x) + (y * y) + (z * z))

        if g == 0:
            mag = on_zero_gravity
        else:
            mag = acos(z / g)
        if y == 0:
            if x > 0: ang = -pi / 2
            else: ang = pi / 2
        else:
            ang = atan(x/y)
        if y > 0:
            if x > 0: ang -= pi
            else: ang += pi

        return (g, mag, ang)

    __last_mag = 0
    __last_ang = 0

    __GRAVITY_THRESHOLD = 0.15

    def getJoystick(self, max_angle, origin = "-y", dir = "cw"):
        """
        Gets joystick input. Returns a tuple, (`new`, `mag`, `ang`), where:\n
        `new` = `True` if values are new, `False` if current readings are invalid and old
        values are being used.\n
        `mag` = The observed magnitude,\n
        `ang` = The observed angle.\n
        Note on the magnitude: Returns 1 at an angle greater than or equal to `max_angle`.\n
        Note on the angle: `origin` selects which direction gives 0. Can be `"+y"`, `"-y"`,
        `"+x"`, `"-x"`. `dir` selects the direction of rotation and can be `"cw"` or `"acw"`.
        Output will always be in the range -pi to +pi.
        """
        out = self.getJoystickRaw()

        if out[0] < 1 - self.__GRAVITY_THRESHOLD or out[0] > 1 + self.__GRAVITY_THRESHOLD or out[1] < 0:
            return (False, self.__last_mag, self.__last_ang)

        mag = clamp(out[1] / max_angle, 1)
        if origin == "-y": ang = out[2]
        elif origin == "-x": ang = out[2] + (3 * pi / 2)
        elif origin == "+y": ang = out[2] + pi
        else: ang = out[2] + (pi / 2)

        if ang > pi: ang -= 2 * pi

        if dir == "acw": dir *= -1

        return (True, mag, ang)

Input = InputNS()

if __name__ == "__main__":
    if input("Enter 'Y' to perform X, Y, Z print\n>   ").upper() == "Y":
        while True:
            print(Input.getX(), Input.getY(), Input.getZ())

    elif input("Enter 'Y' to perform X, Y test\n>   ").upper() == "Y":
        import tkinter as tk

        win = tk.Tk()
        win.geometry("500x500")
        canv = tk.Canvas(win)
        canv.place(anchor="nw", x=0, y=0, w=500, h=500)
        rect = canv.create_rectangle(245, 245, 255, 255)
        old_x = 250
        old_y = 250

        while True:
            x = Input.getX()
            y = Input.getY()
            
            new_x = int(250 - (x * 245))
            new_y = int(250 + (y * 245))

            off_x = new_x - old_x
            off_y = new_y - old_y
            
            canv.move(rect, off_x, off_y)
            
            old_x = new_x
            old_y = new_y

            win.update()
    
    elif input("Enter 'Y' to perform raw joystick test\n>   ").upper() == "Y":
        while True:
            print(Input.getJoystickRaw())
            
    elif input("Enter 'Y' to perform joystick test\n>   ").upper() == "Y":
        while True:
            print(Input.getJoystick(pi / 4))