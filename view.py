import pygame, sys
from pygame.locals import *
import world
import numpy as np
from math import sqrt, sin, cos


C = 50


def draw_layout(DISPLAY, layout, DRAW=False):
    if(DRAW):
        WHITE = (255, 255, 255)
        black = (0, 0, 0)

        DISPLAY.fill(WHITE)

        for (x, y), value in np.ndenumerate(layout):
            if layout[y][x] == 1:
                pygame.draw.rect(DISPLAY, black, (x * C, y*C, C, C))


def draw_camera(DISPLAY, camera, layout, DRAW=False):
    blue = (0, 0, 255)
    red = (255, 0, 0)

    pos = camera.position

    r = int(C / 8)
    rays = list(camera.rays)

    distances = [0] * len(rays)
    sides = [0] * len(rays)
    for i, ray in enumerate(rays):
        length, intersection, side = raycast(ray, camera, layout)
        sides[i] = side
        distances[i] = length

        ray = (C * pos[0] + int(length) * cos(ray),  C * pos[1] + int(length) * sin(ray))

        pygame.draw.line(DISPLAY, red, (C * pos[0], C * pos[1]), ray)
        if DRAW:
            pygame.draw.circle(DISPLAY, red, (int(intersection[1]), int(intersection[0])), 5)
            pygame.draw.circle(DISPLAY, blue, (int(pos[0]*C), int(pos[1]*C)), r)
    return distances, sides


def raycast(ray, camera, layout):
    """ Return the distance from car to the nearest wall, in the direction
    of angle. Also returns coordinates of lidar hit.

    Uses raycasting to find the hit location.
    See (lodev.org/cgtutor/raycasting.html) for more information.

    Input: angle of ray (relative to car), return_square_distance (for performance)
    Returns: Distance, [mapX, mapY]
    """

    locationY = camera.position[0] * C
    locationX = camera.position[1] * C

    # Position in map
    mapX = int(locationX)
    mapY = int(locationY)

    # Ray goes until the map changes values
    try:
        curr_map_value = layout[mapX][mapY]
        # print(curr_map_value)
    except:
        # If off the screen
        # print("Off the screen")
        pass

    ray_angle = ray

    dirX = sin(ray_angle)
    dirY = cos(ray_angle)
    # print(str(dirX) + ',' + str(dirY))
    # Set deltaDist based on angle. Ifs are to remove divide by zero.
    # sideDist is incremented by deltaDist every x or y step
    if dirX == 0:
        deltaDistX = 0
    else:
        deltaDistX = sqrt(1 + dirY**2 / dirX**2)

    if dirY == 0:
        deltaDistY = 0
    else:
        deltaDistY = sqrt(1 + dirX**2 / dirY**2)

    # Set init sideDist and what direction to step
    if (dirX < 0):
        stepX = -1
        sideDistX = (locationX - mapX) * deltaDistX
    else:
        stepX = 1
        sideDistX = (mapX - locationX + 1) * deltaDistX

    if (dirY < 0):
        stepY = -1
        sideDistY = (locationY - mapY) * deltaDistY
    else:
        stepY = 1
        sideDistY = (mapY - locationY + 1) * deltaDistY

    # Step through boxes until you hit a wall
    while(True):
        # Step in the direction of the shorter sideDist
        # This makes the steps follow the actual slope of the ray
        if sideDistX < sideDistY:
            sideDistX += deltaDistX
            mapX += stepX
            side = 0
        else:
            sideDistY += deltaDistY
            mapY += stepY
            side = 1

        # Hit end of ray
        if (mapX-locationX)**2 + (mapY-locationY)**2 > 1000**2:
            break
        # Hit something that is not the current map value
        try:
            if layout[mapX][mapY] > 0:
                # print(mapX, mapY, end='\r')
                break
        except:
            break

    # Whether to return square of the distance (for performance)

    distance = sqrt((mapX-locationX)**2 + (mapY-locationY)**2)

    return distance, [mapX, mapY], side


def draw_world(DISPLAY, w, h, camera, distances, sides, DRAW=False):
    WHITE = (255, 255, 255)
    blue = (0, 200, 255)
    gray = (100, 100, 100)
    dark_gray = (200, 200, 200)

    if not DRAW:
        pygame.draw.rect(DISPLAY, blue, (0, 0, w, h/2))
        pygame.draw.rect(DISPLAY, gray, (0, h/2, w, h/2))

    bins = len(distances)
    bin_width = int(w / bins)
    rays = camera.rays
    points = [[w, h/2]] * (2*(bins + 1))
    points[0] = [0, h/2]
    for i, distance in enumerate(distances):
        height = 25 * h / distance
        height = int(height)
        points[i+1] = [i*bin_width, h/2 - height/2]
        points[2*(bins+1)-(i+1)] = [i*bin_width, h/2 + height/2]
        if not DRAW:
            if sides[i] == 1:
                color = (175, 175, 175)
            else:
                color = (200, 200, 200)
            pygame.draw.rect(DISPLAY, color, (i*bin_width, h/2 - height/2, bin_width, height), 3)


def draw_walls(distances, sides):
    walls = []
    last_side = -1
    run = True
    while run:
        wall = []
        for i, side in enumerate(sides):
            if i > 0:
                delta_dist = distances[i] - distances[i-1]
            else:
                delta_dist = 0
            if last_side < 0:
                last_side = side
            if last_side != side or abs(delta_dist) > 25:
                last_side = side
                walls.append(wall)
                wall = []
            else:
                wall.append(side)
        run = False
    print(walls)


def get_large_layout(layout):
    rows, columns = layout.shape
    blank = np.zeros((rows * C, columns * C))
    # print(blank.shape)
    for (x, y), value in np.ndenumerate(layout):
        value = layout[x][y]
        # print(value)
        if value > 0:
            for i in range(C):
                for j in range(C):
                    blank[i + x*C][j + y*C] = value
    return blank


def get_input():
    """
    Returns a list of user input values (keys, mouse presses, mouse pos).
    """
    get_events()
    keys = pygame.key.get_pressed()
    keys_down = [idx for idx, val in enumerate(keys) if val == 1]
    # The event values representing the keys pressed
    event_keys = (pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT)
    # Convert the list of pressed keys to a list of each relevant key's state
    key_states = [int(key in keys_down) for key in event_keys]
    return key_states


def get_events():
    """
    Handles getting Pygame events.
    """
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:  # If a quit event is received, exit
            pygame.quit()
    return events


if __name__ == "__main__":
    DRAW = False
    layout_size = 20
    wrld = world.world(layout_size)

    layout = wrld.map
    camera = wrld.cam

    layout_hd = get_large_layout(layout)

    pygame.init()
    size = layout_size * C
    DISPLAY = pygame.display.set_mode((2*size, size), 0, 32)

    while True:
        keys = get_input()
        camera.move(keys)

        draw_layout(DISPLAY, layout, DRAW)
        # draw_layout_hd(DISPLAY, layout_hd)
        distances, sides = draw_camera(DISPLAY, camera, layout_hd, DRAW)
        draw_walls(distances, sides)
        draw_world(DISPLAY, 2*size, size, camera, distances, sides, DRAW)
        pygame.display.update()

        clock = pygame.time.Clock()
        clock.tick(60)
