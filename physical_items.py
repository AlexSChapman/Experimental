import time
import pygame
import operator
import math
import view


class projectile():
    def __init__(self, position, direction, velocity, ammo_type):
        # print('projectile_created')
        self.position = [0, 0, 0]
        self.position[0] = position[0] + math.cos(direction[0]) * .1
        self.position[1] = position[1] + math.sin(direction[0]) * .1
        self.position[2] = position[2] + math.sin(direction[1]) * .1

        self.direction = list(direction)

        self.velocity = [0, 0]
        self.velocity[0] = velocity
        self.velocity[1] = math.sin(direction[1]) * velocity

        self.type = ammo_type

        self.acceleration = -0.3
        self.time = time.clock()

        if self.type == 0:
            self.image = pygame.image.load("resources/projectiles/0.png")  # Load image
            self.image = pygame.transform.scale(self.image, (30, 30))
        else:
            self.image = pygame.image.load("resources/projectiles/1.png")  # Load image
        # print(self)

    def __str__(self):
        to_return = str(round(2, self.position)) + ', ' + str(round(2, self.direction)) + ', ' + str(round(2, self.velocity))
        return(to_return)

    def update_physics(self):
        new_time = time.clock()
        delta_time = new_time - self.time
        self.time = new_time

        vel_x = math.cos(self.direction[0]) * self.velocity[0]
        vel_y = math.sin(self.direction[0]) * self.velocity[0]

        self.position[0] += vel_x * delta_time
        self.position[1] += vel_y * delta_time
        self.position[2] += self.velocity[1] * delta_time + .5 * self.acceleration * (delta_time**2)

        self.velocity[1] += self.acceleration * delta_time
        # print(self.position[2])

    def draw(self, DISPLAY, camera, w, h, C):
        self.update_physics()
        drawn_x, drawn_y, distance = view.draw(self.position, camera, w, h)

        r = int(30 / ((distance/5) + 1))
        # self.image = pygame.transform.scale(self.image, (r, r))
        pygame.draw.circle(DISPLAY, (100, 255, 0), (drawn_x, drawn_y), r)

        return distance, self.position


def round(number_of_zeros, num):
    if type(num) is list:
        to_return = []
        for i in num:
            to_return.append(round(number_of_zeros, i))
        return to_return
    else:
        factor = 10**number_of_zeros
        return int(num * factor) / factor
