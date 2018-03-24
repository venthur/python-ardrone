# Screen: the screen to blit to
# originalImage: the image from the camera
# newImage: the process-result
# whichImage
# offset: how much the target is offset from the center
# keypoint: the keypoint object
# a: sideways movement
# b: forward movement
# c: up/down movement
# d: left-right rotation
# landing: the drone is landing
# takeOff: the drone is taking off
# mode: Manual or automatic
import pygame

W, H = 640, 360

def render(screen,  originalImage, newImage, whichImage, offset, keypoint, a,b,c,d, landing, takeOff, mode):
    surface = pygame.image.frombuffer(newImage, (W, H), 'RGB')
    screen.blit(surface, (0, 0))