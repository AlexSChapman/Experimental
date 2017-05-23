import math
import time


class player():
    def __init__(self, position, direction, FOV):
        self.OLD_TIME = time.clock()
        self.position = position
        self.direction = direction
        self.FOV = FOV
        self.update_rays()
        self.rays = [0, 0]
        print(position)

    def __str__(self):
        return 'this is a camera'

    def update_rays(self, resolution=80):
        start = self.direction[0] - self.FOV / 2
        step = self.FOV / resolution
        self.rays = [i*step+start for i in range(resolution)]
        # print(rays)

    def move(self, input_keys):
        new_time = time.clock()
        delta_time = new_time - self.OLD_TIME
        self.OLD_TIME = new_time
        speed = 2 * delta_time
        if input_keys[0]:
            self.position[0] += speed * math.cos(-self.direction[0])
            self.position[1] += -speed * math.sin(-self.direction[0])
        if input_keys[1]:
            self.position[0] -= speed * math.cos(-self.direction[0])
            self.position[1] -= -speed * math.sin(-self.direction[0])
        if input_keys[2]:
            self.direction[0] += speed/2
        if input_keys[3]:
            self.direction[0] -= speed/2

        self.update_rays()
