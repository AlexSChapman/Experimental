import pygame.surfarray as surfarray
import world

if __name__ == "__main__":
    test = world.world(10)
    map = test.map
    surfdemo_show(map, 'striped')
