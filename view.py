import pygame
from pygame.locals import *
import world
import physical_items
import numpy as np
from math import sqrt, sin, cos, pi, atan
import operator

C = 50
WALL_HEIGHT = 30
W_H = .75


def draw_layout(DISPLAY, layout, origin, camera, w, h):
    """
    Draws the map on the screen when in 2-D mode. Draws the map in lowest
    resolution for faster refresh time.

    INPUTS:
    DISPLAY -> Pygame display to be drawn on
    layout  -> map of base width
    DRAW    -> Whether or not to draw the map
    """
    WHITE = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)

    # Refreshes screen
    pygame.draw.rect(DISPLAY, WHITE, (origin, 5, C/5*layout.shape[0], C/5*layout.shape[0]))

    cam_Map_x = int(camera.position[0]*C/5 + origin)
    cam_map_y = int(camera.position[1]*C/5 + 5)
    ray_length = 80

    line_points = (int(sin(camera.direction[0]+pi/2) * ray_length + cam_Map_x), int(cam_map_y + -cos(camera.direction[0]+pi/2)*ray_length))
    pygame.draw.line(DISPLAY, (50, 50, 255), (cam_Map_x, cam_map_y), line_points, 2)
    for (x, y), value in np.ndenumerate(layout):
        # Only Draws black rectangles
        if layout[y][x] == 1:
            pygame.draw.rect(DISPLAY, black, (x * C/5 + origin, y*C/5 + 5, C/5, C/5))

    pygame.draw.circle(DISPLAY, red, (cam_Map_x, cam_map_y), 5)


    # pygame.draw.line(DISPLAY, red, (C/5 * camera.position[0] + origin, C/5 * camera.position[1] + 5), camera.rays[0])
    # pygame.draw.line(DISPLAY, red, (C/5 * camera.position[0] + origin, C/5 * camera.position[1] + 5), camera.rays[1])


def draw_camera(DISPLAY, camera, layout, origin, DRAW=False):
    """
    Draws the player and player's rays in 2D mode, calculates the distances
    when in 3D mode.
    INPUTS:
    DISPLAY -> Pygame display to be drawn on
    camera  -> Player object that holds state variables and can be moved
    layout  -> map of base width
    DRAW    -> Whether or not to draw the map
    """
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

        ray = (C * pos[0] + int(length) * cos(ray) + origin,  C * pos[1] + int(length) * sin(ray) + 5)
        if i == 0:
            camera.rays[0] = ray
        elif i == len(rays) - 1:
            camera.rays[1] = ray
        if DRAW:
            pygame.draw.line(DISPLAY, red, (C * pos[0], C * pos[1]), ray)

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
        if mapX < 0 or mapX > 20 * C:
            side = 2
            break
        if mapY < 0 or mapY > 20 * C:
            side = 3
            break
        try:
            if layout[mapX][mapY] > 0:
                # print(mapX, mapY, end='\r')
                break
        except:
            pass

    # Whether to return square of the distance (for performance)

    distance = sqrt((mapX-locationX)**2 + (mapY-locationY)**2)

    return distance, [mapX, mapY], side


def draw_world(DISPLAY, w, h, camera, distances, sides, DRAW=False):
    """
    Most Fundemental Drawing strategy, fills a rectangle for each ray of
    vision. Precursor to later forms.

    INPUTS:
    DISPLAY     -> Pygame display to be drawn on
    w           -> width of the screen in pixels
    h           -> height of the screen in pixels
    camera      -> Player object that holds state variables and can be moved
    distances   -> Array of distances, from left to right, of the player's vision.
                    This is the actual "3D" component
    sides       -> Array of equal length to distances which holds which side of the
                    blocks a player is looking at, used for shading differentiation.
    DRAW        -> Whether or not to draw the map
    """
    WHITE = (255, 255, 255)
    blue = (0, 200, 255)
    gray = (100, 100, 100)
    green = (75, 150, 75)
    orange = (200, 150, 0)
    dark_orange = (175, 125, 0)

    if not DRAW:
        pygame.draw.rect(DISPLAY, blue, (0, 0, w, h/2))
        pygame.draw.rect(DISPLAY, green, (0, h/2, w, h/2))

    bins = len(distances)
    bin_width = int(w / bins)
    rays = camera.rays
    points = [[w, h/2]] * (2*(bins + 1))
    points[0] = [0, h/2]
    for i, distance in enumerate(distances):
        height = WALL_HEIGHT * h / distance
        height = int(height)
        points[i+1] = [i*bin_width, h/2 - height/2]
        points[2*(bins+1)-(i+1)] = [i*bin_width, h/2 + height/2]
        if not DRAW:
            if sides[i] == 1:
                color = (175, 175, 175)
            elif sides[i] == 0:
                color = (200, 200, 200)
            elif sides[i] == 2:
                color = orange
            elif sides[i] == 3:
                color = dark_orange
            pygame.draw.rect(DISPLAY, color, (i*bin_width, h/2 - height/2, bin_width, height))


def draw_world_MkII(DISPLAY, camera, w, h, layout):
    blue = (0, 200, 255)
    green = (60,200,113)

    north = (100, 100, 100)
    east = (255, 255, 200)
    south = (100, 100, 200)
    west = (255, 100, 100)
    colors = [north, east, south, west]
    points = []

    # wall height
    for (x, y), value in np.ndenumerate(layout):
        if value != 0:
            # highest level organizing list
            highest = []

            # from the layout creates a list of 8 points for each square
            # jig for creating correct syntax
            jig = [[y, x, W_H], [y, x, 0]]
            highest.append(jig)

            jig = [[y+1, x, W_H], [y+1, x, 0]]
            highest.append(jig)

            jig = [[y, x+1, W_H], [y, x+1, 0]]
            highest.append(jig)

            jig = [[y+1, x+1, W_H], [y+1, x+1, 0]]
            highest.append(jig)

            points.append(highest)

    result = draw([100, 100, 0], camera, w, h)

    pygame.draw.rect(DISPLAY, blue, (0, 0, w, result[1]))

    pygame.draw.rect(DISPLAY, green, (0, result[1], w, h - result[1]))

    all_polygons = []
    for cube in points:
        # appends DRAWN points into pairs denoting uprights of cube (4 in total)
        uprights = []
        for vertical in cube:
            holder = []
            for point in vertical:
                holder.append(draw(point, camera, w, h))
            uprights.append(holder)

        # North -> 0
        # East  -> 1
        # South -> 2
        # West  -> 3
        faces = []
        faces.append([uprights[0], uprights[1]])
        faces.append([uprights[1], uprights[3]])
        faces.append([uprights[3], uprights[2]])
        faces.append([uprights[2], uprights[0]])

        # Creates list of points for polygon drawing of faces
        for i, face in enumerate(faces):
            # trigger for drawing, if no component is None it's drawn
            # None_bool = False
            face_points = []
            for upright_pair in face:
                for point in upright_pair:
                    if point is not None:
                        # appends x, y, and size, as well as index i for face coloring
                        face_points.append([point, i])
            # print(face_points)
            face_points[3], face_points[2] = face_points[2], face_points[3]
            all_polygons.append(face_points)
    all_polygons = sorted(all_polygons, key=lambda poly: (poly[0][0][2] + poly[2][0][2]))
    all_polygons = all_polygons[::-1]
    for polygon in all_polygons:
        polygon_points = []
        side = polygon[0][1]
        all_negative = True
        for point in polygon:
            if point[0][0] > 0:
                all_negative = False
            polygon_points.append((point[0][0], point[0][1]))
        if abs(polygon_points[1][0] - polygon_points[2][0]) < w*3 and all_negative is False:
            pygame.draw.polygon(DISPLAY, colors[side], polygon_points)


def draw(position, camera, w, h):
    differences = list(map(operator.sub, position, camera.position))
    distance = 0
    for i, dif in enumerate(differences):
        distance += dif**2
        if dif == 0:
            differences[i] = .01
    # to_draw = []
    if differences[0] > 0:
        if differences[1] > 0:
            # IV: atan is positive in this quad as differences[1] is positive here
            angle_xy = (pi * 2) - atan(differences[1] / differences[0])
        else:
            # I: atan is negative in this quad, as differences[1] is neg here
            angle_xy = -1 * atan(differences[1] / differences[0])
    else:
        if differences[1] > 0:
            # III: atan is negative here, and thus needs to be inverted to add onto pi
            angle_xy = pi - atan(differences[1] / differences[0])
        else:
            # II: atan is positive here
            angle_xy = pi - atan(differences[1] / differences[0])
    angle_xy = pi * 2 - angle_xy
    # angle_xy = round(2, angle_xy - camera.direction[0])
    angle_difference_xy = angle_xy - camera.direction[0]
    if angle_difference_xy > 2*pi - camera.FOV:
        angle_difference_xy -= 2*pi
    if angle_difference_xy < -(2*pi - camera.FOV):
        angle_difference_xy += 2*pi

    distance = distance**.5
    xy_dist = (differences[0]**2 + differences[1]**2)**.5

    angle_difference_z = camera.direction[1] - atan(differences[2]/xy_dist)
    H_FOV = camera.FOV / 2

    x_drawn = ((angle_difference_xy / H_FOV) + 1) * (w/2)
    y_drawn = ((angle_difference_z / H_FOV) + 1) * (h/2)
    return [int(x_drawn), int(y_drawn), distance]


    # RETURNS NONE IF BLOCK IS NOT IN SIGHT
    # if abs(angle_difference_xy) < H_FOV:
    #     x_drawn = ((angle_difference_xy / H_FOV) + 1) * (w/2)
    #     y_drawn = ((angle_difference_z / H_FOV) + 1) * (h/2)
    #     r = int(5 / ((distance/5) + 1))
    #     return [int(x_drawn), int(y_drawn), r]
    # else:
    #     return None
        # image = pygame.transform.scale(image, (r, r))
        # pygame.draw.circle(DISPLAY, (255, 255, 0), (int(x_drawn), int(y_drawn)), r)
        # DISPLAY.blit(image, (int(x_drawn - r/2), int(y_drawn - r/2)))


def draw_walls(DISPLAY, distances, sides, w, h, DRAW):
    """
    Drawing strategy which attempts to interpolate the walls by drawing a
    polygon with vertices on the corners of the first and last bins of a
    percieved side. Usually causes slight visual discrepancies (like corners
    not being aligned, as well as rudely removing fisheye effect.)

    INPUTS:
    DISPLAY     -> Pygame display to be drawn on
    distances   -> Array of distances, from left to right, of the player's vision.
                    This is the actual "3D" component
    sides       -> Array of equal length to distances which holds which side of the
                    blocks a player is looking at, used for shading differentiation.
    w           -> width of the screen in pixels
    h           -> height of the screen in pixels
    DRAW        -> Whether or not to draw the map
    """
    blue = (0, 200, 255)
    gray = (150, 150, 150)
    light_gray = (175, 175, 175)
    green = (75, 150, 75)

    if not DRAW:
        pygame.draw.rect(DISPLAY, blue, (0, 0, w, h/2))
        pygame.draw.rect(DISPLAY, green, (0, h/2, w, h/2))

    bins = len(distances)

    bin_width = int(w / bins)

    walls = find_walls(distances, sides)
    # print(walls)

    x = 0
    for i, wall in enumerate(walls):
        left_x = x
        left_y = 0
        right_x = len(wall) * bin_width + x
        right_y = 0

        x = right_x
        try:
            side = wall[0][1]
            last_distance = wall[len(wall) - 1]
            first_distance = wall[0]

            # subtract from h/2 for top, add for bottom
            left_y = int((WALL_HEIGHT * h / first_distance[0])/2)
            right_y = int((WALL_HEIGHT * h / last_distance[0])/2)
            """
            if wall[2] < 40:
                next_left = int((WALL_HEIGHT * h / walls[i][0][0])/2)
                right_y = next_left"""

            left_top = [left_x, h/2 - left_y]
            left_bottom = [left_x, h/2 + left_y]

            right_top = [right_x, h/2 - right_y]
            right_bottom = [right_x, h/2 + right_y]

            points = [left_top, right_top, right_bottom, left_bottom]
            if side == 1:
                color = gray
            else:
                color = light_gray
            pygame.draw.polygon(DISPLAY, color, points)
        except:
            pass


def smooth_walls(DISPLAY, distances, sides, w, h, DRAW):
    """
    Drawing strategy which attempts to interpolate the walls by drawing a
    polygon with vertices on the corners of EACH bin. In progress 5.23

    INPUTS:
    DISPLAY     -> Pygame display to be drawn on
    distances   -> Array of distances, from left to right, of the player's vision.
                    This is the actual "3D" component
    sides       -> Array of equal length to distances which holds which side of the
                    blocks a player is looking at, used for shading differentiation.
    w           -> width of the screen in pixels
    h           -> height of the screen in pixels
    DRAW        -> Whether or not to draw the map
    """
    blue = (0, 200, 255)
    gray = (150, 150, 150)
    light_gray = (175, 175, 175)
    green = (75, 150, 75)

    if not DRAW:
        pygame.draw.rect(DISPLAY, blue, (0, 0, w, h/2))
        pygame.draw.rect(DISPLAY, green, (0, h/2, w, h/2))

    bins = len(distances)

    bin_width = int(w / bins)

    walls = find_walls(distances, sides)
    # print(walls)

    x = 0
    for i, wall in enumerate(walls):

        try:
            side = wall[0][1]
            points_T = []
            points_B = []
            for q, distance in enumerate(wall):
                point_T = []
                point_B = []
                if q == 0:
                    point_T.append(x)
                    point_B.append(x)
                    x += bin_width
                else:
                    x += bin_width
                    point_T.append(x)
                    point_B.append(x)

                left_y = int((WALL_HEIGHT * h / distance[0])/2)
                point_T.append(h/2 - left_y)

                point_B.append(h/2 + left_y)

                points_T.append(point_T)
                points_B.append(point_B)
            points_B = points_B[::-1]
            points = points_T + points_B
            if side == 1:
                color = gray
            else:
                color = light_gray
            pygame.draw.polygon(DISPLAY, color, points)
        except:
            pass


def find_walls(distances, sides):
    walls = []
    last_side = -1
    run = True
    while run:
        wall = []
        last_distance = 1000
        for i, side in enumerate(sides):
            if i > 0:
                delta_dist = distances[i] - distances[i-1]
                last_distance = distances[i-1]
            else:
                delta_dist = 0

            if last_side < 0:
                last_side = side

            if last_side != side or abs(delta_dist) > 30:
                if len(walls) > 0:
                    wall.append([last_distance, last_side, abs(delta_dist)])
                last_side = side
                walls.append(wall)
                wall = []
            else:
                wall.append([distances[i], side, abs(delta_dist)])
        walls.append(wall)
        run = False
    return walls


def draw_HUD(DISPLAY, reticles, hands, dodgeballs, weapon_state, iteration, w, h, ratio, camera):
    index = iteration/ratio
    if index > len(reticles)-1:
        index = len(reticles)-1
    elif index < 0:
        index = 0
    hold = index
    index = int(index)
    i_w, i_h = reticles[0].get_rect().size

    image_to_use = reticles[index]
    camera.FOV = camera.original_FOV - hold*.02
    DISPLAY.blit(image_to_use, (20, 200))

    # Dodgeball Placeholders
    DISPLAY.blit(dodgeballs[0], (920 + int(hold*25), 575 - int(hold*25)))
    # Hands
    DISPLAY.blit(hands[0], (250, 600 + int(hold*25)))
    DISPLAY.blit(hands[3], (950 + int(hold*25), 600 - int(hold*25)))


def load_images():
    hands = []
    hands.append(pygame.image.load("resources/Hand_Bunched_L.png"))  # Load image
    hands.append(pygame.image.load("resources/Hand_Spread_L.png"))  # Load image
    hands.append(pygame.image.load("resources/Hand_Bunched.png"))  # Load image
    hands.append(pygame.image.load("resources/Hand_Spread.png"))  # Load image
    for i, hand in enumerate(hands):
        hands[i] = pygame.transform.rotozoom(hand, 0, .6)

    reticles = []
    reticles.append(pygame.image.load("resources/Reticle/0.png"))
    reticles.append(pygame.image.load("resources/Reticle/1.png"))
    reticles.append(pygame.image.load("resources/Reticle/2.png"))
    reticles.append(pygame.image.load("resources/Reticle/3.png"))
    reticles.append(pygame.image.load("resources/Reticle/4.png"))
    reticles.append(pygame.image.load("resources/Reticle/5.png"))

    charges = []
    charges.append(pygame.image.load("resources/charge/0.png"))
    charges.append(pygame.image.load("resources/charge/1.png"))
    charges.append(pygame.image.load("resources/charge/2.png"))
    charges.append(pygame.image.load("resources/charge/3.png"))
    charges.append(pygame.image.load("resources/charge/4.png"))
    charges.append(pygame.image.load("resources/charge/5.png"))
    charges.append(pygame.image.load("resources/charge/6.png"))
    charges.append(pygame.image.load("resources/charge/7.png"))
    charges.append(pygame.image.load("resources/charge/8.png"))
    charges.append(pygame.image.load("resources/charge/9.png"))

    dodgeballs = []
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/0.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/1.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/2.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/3.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/4.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/5.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/6.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/7.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/8.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/9.png"))
    dodgeballs.append(pygame.image.load("resources/Projectiles/0/10.png"))
    for i, dodgeball in enumerate(dodgeballs):
        dodgeballs[i] = pygame.transform.rotozoom(dodgeball, 0, 5)

    return hands, reticles, charges, dodgeballs


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


def get_input(clicked_state, shot_state):
    """
    Returns a list of user input values (keys, mouse presses, mouse pos).
    """
    unused, clicked_state, shot_state = get_events(clicked_state, shot_state)
    keys = pygame.key.get_pressed()
    keys_down = [idx for idx, val in enumerate(keys) if val == 1]
    # The event values representing the keys pressed
    event_keys = (pygame.K_w, pygame.K_s, pygame.K_d, pygame.K_a, pygame.K_ESCAPE, pygame.K_SPACE)
    # Convert the list of pressed keys to a list of each relevant key's state
    key_states = [int(key in keys_down) for key in event_keys]
    return key_states, clicked_state, shot_state


def get_events(clicked_state, shot_state):
    """
    Handles getting Pygame events.
    """
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 3:
            clicked_state = True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 3:
            clicked_state = False

        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            shot_state = True
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            shot_state = False

        if e.type == pygame.QUIT:  # If a quit event is received, exit
            pygame.quit()
    return events, clicked_state, shot_state


def collide(shots, layout):
    collisions = []
    for i, shot in enumerate(shots):
        try:
            if layout[int(shot.position[1])][int(shot.position[0])] != 0 and shot.position[2] < W_H:
                del shots[i]
                collisions.append(shot.position)
        except:
            del shots[i]
            collisions.append(shot.position)
    return collisions


if __name__ == "__main__":
    DRAW = False
    layout_size = 22
    wrld = world.world(layout_size)

    layout = wrld.map
    camera = wrld.cam

    layout_hd = get_large_layout(layout)
    # print(layout.shape, layout_hd.shape)
    pygame.init()
    size = layout_size * C
    size_factor = 1.6
    DISPLAY = pygame.display.set_mode((int(size_factor*size), size), 0, 32)

    clock = pygame.time.Clock()

    hands, reticles, charges, dodgeballs = load_images()
    weapon_state = False
    last_weapon_state = False
    animation_iteration = 0
    ratio = 3

    shot_state = False
    last_shot_state = False

    paused = 0
    ready_to_change = 1

    origin = int(size_factor*size) - ((layout.shape[0] * C/5) + 5)

    shots = []

    while True:
        fps = int(clock.get_fps()*100) / 100
        keys, weapon_state, shot_state = get_input(weapon_state, shot_state)

        if keys[4] == 1 and paused == 0 and ready_to_change == 1:
            paused = keys[4]
            ready_to_change = 0

        if keys[4] == 0:
            ready_to_change = 1

        if paused == 1 and keys[4] == 1 and ready_to_change == 1:
            paused = 0
            ready_to_change = 0

        if keys[3] == 1:
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)

        if shot_state != last_shot_state and shot_state and weapon_state:
            shots.append(physical_items.projectile(camera.position, camera.direction, 10, 0, dodgeballs))

        if not paused:
            dx, dy = pygame.mouse.get_rel()
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)

            if weapon_state != last_weapon_state:
                if weapon_state:
                    animation_iteration = 0
            if weapon_state:
                animation_iteration += 1
            else:
                animation_iteration -= 1

            camera.move(keys, dx, dy, layout)

            # distances, sides = draw_camera(DISPLAY, camera, layout_hd, origin, False)

            # draw_world(DISPLAY, int(size_factor*size), size, camera, distances, sides, DRAW)
            draw_world_MkII(DISPLAY, camera, int(size_factor*size), size, layout)
            draw_HUD(DISPLAY, charges, hands, dodgeballs, weapon_state, animation_iteration, int(size_factor*size), size, ratio, camera)
            draw_layout(DISPLAY, layout, origin, camera, int(size_factor*size), size)

            # if len(shots) > 1:
            #     del shots[0]

            collide(shots, layout)
            for i, shot in enumerate(shots):
                distance, pos = shot.draw(DISPLAY, camera, int(size_factor*size), size, C)
                if pos[2] <= 0:
                    del shots[i]
                # if shot.draw(DISPLAY, camera, int(size_factor*size), size, C) > 10:
                #    del shots[i]
            # render text
            myfont = pygame.font.SysFont("monospace", 35)

            label = myfont.render('fps:' + str(fps), 1, (255, 255, 255))
            DISPLAY.blit(label, (10, 10))
        else:

            draw_world_MkII(DISPLAY, camera, int(size_factor*size), size, layout)
            draw_HUD(DISPLAY, charges, weapon_state, animation_iteration, int(size_factor*size), size, ratio, camera)
            draw_layout(DISPLAY, layout, origin, camera, int(size_factor*size), size)

            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
            myfont = pygame.font.SysFont("monospace", 75)

            s = pygame.Surface((int(size_factor*size) - 20, size - 20))  # the size of your rect
            s.set_alpha(175)                # alpha level
            s.fill((100, 100, 100))           # this fills the entire surface
            DISPLAY.blit(s, (10, 10))    # (0,0) are the top-left coordinates
            label = myfont.render('PAUSED.', 1, (255, 255, 0))
            DISPLAY.blit(label, (10, 10))

        last_weapon_state = weapon_state
        last_shot_state = shot_state

        pygame.display.update()
        clock.tick(60)
