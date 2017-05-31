import time
import pygame
import operator
import math


class projectile():
    def __init__(self, position, direction, velocity, ammo_type):
        print('projectile_created')
        self.position = [0, 0, 0]
        self.position[0] = position[0] + math.cos(direction[0]) * .5
        self.position[1] = position[1] + math.sin(direction[0]) * .5
        self.position[2] = position[2]
        self.direction = list(direction)
        self.velocity = []
        self.velocity.append(velocity)
        self.velocity.append(0)
        self.type = ammo_type

        self.acceleration = .05
        self.time = time.clock()

        if self.type == 0:
            self.image = pygame.image.load("resources/projectiles/0.png")  # Load image
        else:
            self.image = pygame.image.load("resources/projectiles/1.png")  # Load image
        print(self)

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
        differences = list(map(operator.sub, self.position, camera.position))
        # to_draw = []
        distance = 0
        for i, dif in enumerate(differences):
            # to_draw.append(round(2, dif))

            # dif = dif * C
            distance += dif**2

            if dif == 0:
                differences[i] = .0001

        distance = distance**.5

        # xy_angle = (math.atan(-differences[1] / differences[0]) % (math.pi * 2))
        if differences[0] > 0:
            if differences[1] > 0:
                # print('IV     ', end='\r')
                # IV: atan is positive in this quad as differences[1] is positive here
                angle_xy = (math.pi * 2) - math.atan(differences[1] / differences[0])
            else:
                # print('I     ', end='\r')
                # I: atan is negative in this quad, as differences[1] is neg here
                angle_xy = -1 * math.atan(differences[1] / differences[0])
        else:
            if differences[1] > 0:
                # print('III     ', end='\r')
                # III: atan is negative here, and thus needs to be inverted to add onto pi
                angle_xy = math.pi - math.atan(differences[1] / differences[0])
            else:
                # print('II     ', end='\r')
                # II: atan is positive here
                angle_xy = math.pi - math.atan(differences[1] / differences[0])
        angle_xy = math.pi * 2 - angle_xy
        # angle_xy = round(2, angle_xy - camera.direction[0])
        angle_difference_xy = angle_xy - camera.direction[0]
        angle_difference_z = math.atan(self.position[2]/distance)
        H_FOV = camera.FOV / 2

        if abs(angle_difference_xy) < H_FOV:
            x_drawn = ((angle_difference_xy / H_FOV) + 1) * (w/2)
            y_drawn = ((angle_difference_z / H_FOV) + 1) * (h/2)
            r = 10 / ((distance/5) + 1)
            pygame.draw.rect(DISPLAY, (255, 255, 0), (int(x_drawn - r/2), int(y_drawn - r/2), r, r))

        # print(round(2, self.position), round(2, camera.position), round(2, self.direction), round(2, camera.direction[0]), round(2, angle_difference_xy), to_draw, end='\r')

        # pygame.draw.rect(DISPLAY, (255, 255, 0), (int(x_drawn_pos), int(y_drawn_pos), 5, 5))
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
