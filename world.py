import numpy as np
import camera
import math


class world():
    def __init__(self, size):
        max = 4
        self.map = np.random.randint(max, size=(size, size))
        low_values_indices = self.map < max-1  # Where values are low
        self.map[low_values_indices] = 0  # All low values set to 0

        low_values_indices = self.map > max-3  # Where values are low
        self.map[low_values_indices] = 1  # All low values set to 0
        # print(self.map)
        start_box_size = 3
        for i in range(start_box_size):
            for o in range(start_box_size):
                self.map[int(size/2 - start_box_size/2 + i)][int(size/2 - start_box_size/2 + o)] = 0

        for i in range(size):
            self.map[0][i] = 1
            self.map[i][0] = 1

            self.map[size-1][i] = 1
            self.map[i][size-1] = 1
        # print(self.map)

        # positive angle increase is clockwise
        self.cam = camera.player([int(size / 2), int(size/2), .5], [math.pi/2, 0], math.pi/3)


if __name__ == "__main__":
    world = world(20)
