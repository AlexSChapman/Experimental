import numpy as np
import camera
import math

class world():
    def __init__(self, size):
        max = 4
        self.map = np.random.randint(max, size=(size, size))
        low_values_indices = self.map < max-1  # Where values are low
        self.map[low_values_indices] = 0  # All low values set to 0

        low_values_indices = self.map == max-1  # Where values are low
        self.map[low_values_indices] = 1  # All low values set to 0
        print(self.map)

        # positive angle increase is clockwise
        self.cam = camera.player([int(size / 2), int(size/2), 0], [math.pi/2, 0], math.pi/2)

if __name__ == "__main__":
    world = world(20)
