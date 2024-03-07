from .Raw import Raw
from time import sleep

class CalibrationNS():
    def begin(self):
        """
        Begins calibration. Clears the minimum and maximum values in the X, Y and Z directions,
        which are updated with calls to Calibration.tick().
        """
        self.min_x = 0
        self.max_x = 0
        self.min_y = 0
        self.max_y = 0
        self.min_z = 0
        self.max_z = 0

        self.__matching_vals = [[] for i in range(6)]
        self.__complete = [False for i in range(6)]
    
    __MATCHING_VALS_NEEDED = 10
    __MATCHING_VALS_TOLERANCE = 10

    def __recordValue(self, value, index):
        self.__matching_vals[index].append(value)
        while len(self.__matching_vals[index]) > self.__MATCHING_VALS_NEEDED: self.__matching_vals[index].pop(0)
        min_val = min(self.__matching_vals[index])
        max_val = max(self.__matching_vals[index])
        if abs(max_val - min_val) <= self.__MATCHING_VALS_TOLERANCE:
            self.__complete[index] = True
            return (max_val + min_val) // 2
        else: return 0

    def tick(self, min_threshold = 200, max_threshold = 300, delay = False):
        """
        Call while calibrating to get new minimum and maximum values for X, Y and Z.\n
        Adjust `max_threshold` to set cutoff (to ignore high magnitude noise observed when expecting 0).
        """
        x = Raw.getX()
        y = Raw.getY()
        z = Raw.getZ()

        if x < -max_threshold: x = 0
        elif x > max_threshold: x = 0
        if y < -max_threshold: y = 0
        elif y > max_threshold: y = 0
        if z < -max_threshold: z = 0
        elif z > max_threshold: z = 0

        if x < -min_threshold: x = self.__recordValue(x, 0)
        else: self.__matching_vals[0].clear()
        if x > min_threshold: x = self.__recordValue(x, 1)
        else: self.__matching_vals[1].clear()
        if y < -min_threshold: y = self.__recordValue(y, 2)
        else: self.__matching_vals[2].clear()
        if y > min_threshold: y = self.__recordValue(y, 3)
        else: self.__matching_vals[3].clear()
        if z < -min_threshold: z = self.__recordValue(z, 4)
        else: self.__matching_vals[4].clear()
        if z > min_threshold: z = self.__recordValue(z, 5)
        else: self.__matching_vals[5].clear()

        if x < self.min_x: self.min_x = x
        elif x > self.max_x: self.max_x = x
        if y < self.min_y: self.min_y = y
        elif y > self.max_y: self.max_y = y
        if z < self.min_z: self.min_z = z
        elif z > self.max_z: self.max_z = z

        if delay: sleep(0.001)

    def isComplete(self):
        """
        Call between 1Calibration.begin()` and `Calibration.end()`.\n
        Returns whether calibration is complete and `Calibration.end()` can be called.
        """
        return not False in self.__complete
    
    def getIncomplete(self):
        """
        Call between 1Calibration.begin()` and `Calibration.end()`.\n
        Returns which axes still aren't calibrated.
        """
        out = []
        for i, j in zip(self.__complete, ("MIN_X", "MAX_X", "MIN_Y", "MAX_Y", "MIN_Z", "MAX_Z")):
            if not i: out.append(j)
        return out

    def end(self):
        """
        Ends calibration. Is equivalent to `Calibration.copyValuesToFile()`, but is named
        to match Calibration.begin().
        """
        self.copyValuesToFile()

    def copyValuesToList(self):
        """
        Copies calibration values to list.
        """
        return [self.min_x, self.max_x, self.min_y, self.max_y, self.min_z, self.max_z]

    def loadValuesFromList(self, list_):
        """
        Loads calibration values from list.
        """
        self.min_x = list_[0]
        self.max_x = list_[1]
        self.min_y = list_[2]
        self.max_y = list_[3]
        self.min_z = list_[4]
        self.max_z = list_[5]

    __FILE_PATH = "accelerometer_input/calibration.txt"

    def copyValuesToFile(self):
        """
        Copies calibration values to file.
        """
        with open(self.__FILE_PATH, "w") as file:
            file.write(f"{self.min_x} {self.max_x} " +
                       f"{self.min_y} {self.max_y} " +
                       f"{self.min_z} {self.max_z}")

    def loadValuesFromFile(self):
        """
        Loads calibration values from file.
        """
        with open(self.__FILE_PATH, "r") as file:
            self.loadValuesFromList([int(i) for i in file.readline().split(" ")])

Calibration = CalibrationNS()
"""
Namespace with calibration functions.
"""

try:
    Calibration.loadValuesFromFile()
except:
    pass

if __name__ == "__main__":

    try:
        print(Calibration.copyValuesToList())
    except:
        pass

    if input("Enter 'Y' to begin calibration\n>   ").upper() != "Y": quit()

    Calibration.begin()
    while not Calibration.isComplete():
        Calibration.tick(delay = True)
        print(Calibration.getIncomplete())
    
    # Extra ticks to maximise last value
    for i in range(1000):
        Calibration.tick(delay = True)
    
    print(Calibration.copyValuesToList())

    Calibration.end()