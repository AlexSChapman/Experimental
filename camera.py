import math
import time


class player():
    def __init__(self, position, direction, FOV):
        self.OLD_TIME = time.clock()
        self.position = list(position)
        self.direction = direction
        self.FOV = FOV
        self.update_rays()
        self.rays = [0, 0]
        self.x_sensitivity = 200
        self.y_sensitivity = 400
        self.velocity = [0, -0.75]

        self.speed = 1

        self.resting_z = self.position[2]
        self.original_FOV = self.FOV
        # print(position)

    def __str__(self):
        return 'this is a camera'

    def update_rays(self, resolution=80):
        start = self.direction[0] - self.FOV / 2
        step = self.FOV / resolution
        self.rays = [i*step+start for i in range(resolution)]
        # print(rays)

    def limit_rotation(self):
        self.direction[0] = self.direction[0] % (math.pi * 2)
        if self.direction[1] > self.FOV/2:
            self.direction[1] = self.FOV/2
        elif self.direction[1] < -self.FOV/2:
            self.direction[1] = -self.FOV/ 2

    def move(self, input_keys, dx, dy, layout):
        dimensions = layout.shape
        new_time = time.clock()
        delta_time = new_time - self.OLD_TIME
        self.OLD_TIME = new_time
        speed = self.speed * delta_time / 5

        if self.velocity[0] == 0:
            speed = self.speed * delta_time
        if input_keys[0]:
            future_pos_x = speed * math.cos(-self.direction[0]) + self.position[0]
            # print(future_pos_x, end='\r')
            future_pos_y = -speed * math.sin(-self.direction[0]) + self.position[1]

            if future_pos_x > 0 and future_pos_x < dimensions[0]:
                future_pos_x = int(future_pos_x)
                if layout[int(self.position[1])][future_pos_x] == 0:
                    self.position[0] += speed * math.cos(-self.direction[0])

            if future_pos_y > 0 and future_pos_y < dimensions[0]:
                future_pos_y = int(future_pos_y)
                if layout[future_pos_y][int(self.position[0])] == 0:
                    self.position[1] += -speed * math.sin(-self.direction[0])

        if input_keys[1]:
            future_pos_x = int(self.position[0] - speed * math.cos(-self.direction[0]))
            future_pos_y = int(self.position[1] - -speed * math.sin(-self.direction[0]))

            if future_pos_x > 0 and future_pos_x < dimensions[0]:
                future_pos_x = int(future_pos_x)
                if layout[int(self.position[1])][future_pos_x] == 0:
                    self.position[0] -= speed * math.cos(-self.direction[0])
            if future_pos_y > 0 and future_pos_y < dimensions[0]:
                future_pos_y = int(future_pos_y)
                if layout[future_pos_y][int(self.position[0])] == 0:
                    self.position[1] -= -speed * math.sin(-self.direction[0])

        # Right
        if input_keys[2]:
            future_pos_x = int(.6 * speed * math.cos(-(self.direction[0] + (math.pi / 2))) + self.position[0])
            future_pos_y = int(.6 * -speed * math.sin(-(self.direction[0] + (math.pi / 2))) + self.position[1])

            if future_pos_x > 0 and future_pos_x < dimensions[0]:
                future_pos_x = int(future_pos_x)
                if layout[int(self.position[1])][future_pos_x] == 0:
                    self.position[0] += .6 * speed * math.cos(-(self.direction[0] + (math.pi / 2)))

            if future_pos_y > 0 and future_pos_y < dimensions[0]:
                future_pos_y = int(future_pos_y)
                if layout[future_pos_y][int(self.position[0])] == 0:
                    self.position[1] += .6 * -speed * math.sin(-(self.direction[0] + (math.pi / 2)))

        # Left
        if input_keys[3]:
            future_pos_x = int(.6 * speed * math.cos(-(self.direction[0] - (math.pi / 2))) + self.position[0])
            future_pos_y = int(.6 * -speed * math.sin(-(self.direction[0] - (math.pi / 2))) + self.position[1])

            if future_pos_x > 0 and future_pos_x < dimensions[0]:
                future_pos_x = int(future_pos_x)
                if layout[int(self.position[1])][future_pos_x] == 0:
                    self.position[0] += .6 * speed * math.cos(-(self.direction[0] - (math.pi / 2)))
            if future_pos_y > 0 and future_pos_y < dimensions[0]:
                future_pos_y = int(future_pos_y)
                if layout[future_pos_y][int(self.position[0])] == 0:
                    self.position[1] += .6 * -speed * math.sin(-(self.direction[0] - (math.pi / 2)))

        if input_keys[5] and self.velocity[0] == 0:
            self.velocity[0] = 1.25

        if dx / self.x_sensitivity < math.pi / 5:
            self.direction[0] += dx / self.x_sensitivity

        if dy / self.y_sensitivity < math.pi / 5:
            self.direction[1] -= dy / self.y_sensitivity

        new_z = self.position[2] + self.velocity[0] * delta_time + .5 * self.velocity[1] * (delta_time**2)
        self.velocity[0] += self.velocity[1] * delta_time
        if new_z >= self.resting_z:
            self.position[2] = new_z
        else:
            self.velocity[0] = 0
        # self.update_rays()
        self.limit_rotation()
