import time
import pygame
import operator
import math


class projectile():
    def __init__(self, position, direction, velocity, ammo_type):
        print('projectile_created')
        self.position = list(position)
        self.direction = list(direction)
        self.velocity = velocity
        self.type = ammo_type

        self.acceleration = -9.81
        self.time = time.clock()

        if self.type == 0:
            self.image = pygame.image.load("resources/projectiles/0.png")  # Load image
        else:
            self.image = pygame.image.load("resources/projectiles/1.png")  # Load image

    def update_physics(self):
        new_time = time.clock()
        delta_time = new_time - self.time
        self.time = new_time

        vel_x = math.cos(self.direction[0]) * self.velocity
        vel_y = -math.sin(self.direction[0]) * self.velocity

        self.position[0] += vel_x * delta_time
        self.position[1] += vel_y * delta_time
        # self.position[2] += velocity[2] * delta_time + .5 * self.acceleration * (delta_time**2)

    def draw(self, DISPLAY, camera, w, h, C):

        differences = list(map(operator.sub, self.position, camera.position))
        differences[1] = -differences[1]
        for dif in differences:
            dif = dif * C
        distance = 0
        for direction in differences:
            distance += direction**2
        distance = distance**.5

        if differences[0] == 0:
            differences[0] = .01


        # print(distance)

        apparent_angle_xy = math.atan(differences[1] / differences[0])
        try:
            apparent_angle_z = math.atan(differences[2] / distance)
        except:
            apparent_angle_z = 0
        angle_difference_xy = apparent_angle_xy - camera.direction[0]

        FOV_side = camera.FOV / 2
        position_x = 0
        middle_x = w / 2
        middle_y = h / 2

        print(apparent_angle_xy-camera.direction[0], distance)

        if abs(angle_difference_xy) < FOV_side and abs(apparent_angle_z) < FOV_side:
            position_x = middle_x * (angle_difference_xy / FOV_side) + middle_x
            position_y = middle_y * -1 * (apparent_angle_z / FOV_side) + middle_y

            pygame.draw.circle(DISPLAY, (255, 255, 0), (int(position_x), int(position_y)), int(10 - distance))

            print(int(position_x), int(position_y), end='\r')
        return distance
