import pygame

# Dimensions
W, H = 640, 360
CW, CH = int(W / 2), int(H / 2)

# Component sizes
reticle_radius_factor = 0.5
crosshair_size = 30
crosshair_small_size = 5
bar_height = int(H / 2)
bar_width = 10

# Colours
colour_stop = (255, 0, 0)
colour_mode = (0, 0, 255)
colour_control = (0, 255, 255)
colour_target = (255, 0, 255)
colour_reticle = (255, 0, 0)
colour_crosshair = (0, 0, 0)
colour_bar = (0, 255, 0)
colour_bar_background = (0, 0, 0)


def render(screen, originalImage, newImage, isNewImage, offset, keypoint, strafe, thrust, vertical, yaw, isLanding,
           isTakeOff, isAuto, isEmergency):
    """
    Renders an image on the screen with additional information
    :param screen: The screen to blit to
    :param originalImage: The image from the camera
    :param newImage: The process-result
    :param isNewImage: Flag for selecting which image to use (default = false)
    :param offset: Offset of target from center (format: (x, y), range: (-1...1, 1...-1)
    :param keypoint: Keypoint object (ask Kevin)
    :param strafe: Sideways movement
    :param thrust: Forward movement
    :param vertical: Vertical movement
    :param yaw: Left-right rotation
    :param isLanding: Flag, is currently landing
    :param isTakeOff: Flag, is currently taking off
    :param isAuto: Flag, is currently flying on auto pilot
    :param isEmergency: Flag, is currently making emergency landing
    :return:
    """
    # Draw image
    surface = pygame.image.frombuffer(newImage if isNewImage else originalImage, (W, H), 'RGB')
    screen.blit(surface, (0, 0))

    # Draw reticle
    if not isNewImage and offset is not None:
        surface = pygame.Surface((W, H))
        reticle = (CW + offset[0] * W, CH + offset[1] * H)
        radius = reticle_radius_factor * keypoint.size
        pygame.draw.polygon(surface, colour_reticle, [
            (reticle[0] + radius, reticle[1]),
            (reticle[0], reticle[1] + radius),
            (reticle[0] - radius, reticle[1]),
            (reticle[0], reticle[1] - radius),
        ], 3)
        surface.set_colorkey((0, 0, 0))
        screen.blit(surface, (0, 0))

    # Draw crosshair
    surface = pygame.Surface((W, H))
    surface.fill((255, 255, 255))
    pygame.draw.line(surface, colour_crosshair, (CW - crosshair_size, CH), (CW + crosshair_size, CH), 1)
    pygame.draw.line(surface, colour_crosshair, (CW - crosshair_size, CH - crosshair_small_size),
                     (CW - crosshair_size, CH + crosshair_small_size), 1)
    pygame.draw.line(surface, colour_crosshair, (CW + crosshair_size, CH - crosshair_small_size),
                     (CW + crosshair_size, CH + crosshair_small_size), 1)

    pygame.draw.line(surface, colour_crosshair, (CW, CH - crosshair_size), (CW, CH + crosshair_size), 1)
    pygame.draw.line(surface, colour_crosshair, (CW - crosshair_small_size, CH - crosshair_size),
                     (CW + crosshair_small_size, CH - crosshair_size), 1)
    pygame.draw.line(surface, colour_crosshair, (CW - crosshair_small_size, CH + crosshair_size),
                     (CW + crosshair_small_size, CH + crosshair_size), 1)

    surface.set_colorkey((255, 255, 255))
    screen.blit(surface, (0, 0))

    # Draw strafe
    strafe = strafe if strafe is not None else 0
    surface = pygame.Surface((W, H))
    surface.fill((255, 255, 255))
    rectangle = pygame.Rect(CW, H - 2 * bar_width, bar_height * abs(strafe), bar_width)

    pygame.draw.rect(surface, colour_bar, rectangle, 0)
    pygame.draw.rect(surface, colour_bar_background, rectangle, 1)

    if strafe <= 0:
        surface = pygame.transform.flip(surface, True, False)

    surface.set_colorkey((255, 255, 255))
    screen.blit(surface, (0, 0))

    # Draw thrust
    thrust = thrust if thrust is not None else 0
    surface = pygame.Surface((W, H))
    surface.fill((255, 255, 255))
    rectangle = pygame.Rect(W - bar_width, CH, bar_width, bar_height * abs(thrust))

    pygame.draw.rect(surface, colour_bar, rectangle, 0)
    pygame.draw.rect(surface, colour_bar_background, rectangle, 1)

    if thrust <= 0:
        surface = pygame.transform.flip(surface, False, True)

    surface.set_colorkey((255, 255, 255))
    screen.blit(surface, (0, 0))

    # Draw vertical
    vertical = vertical if vertical is not None else 0
    surface = pygame.Surface((W, H))
    surface.fill((255, 255, 255))
    rectangle = pygame.Rect(0, CH, bar_width, bar_height * abs(vertical))

    pygame.draw.rect(surface, colour_bar, rectangle, 0)
    pygame.draw.rect(surface, colour_bar_background, rectangle, 1)

    if vertical > 0:
        surface = pygame.transform.flip(surface, False, True)

    surface.set_colorkey((255, 255, 255))
    screen.blit(surface, (0, 0))

    # Draw yaw
    yaw = yaw if yaw is not None else 0
    surface = pygame.Surface((W, H))
    surface.fill((255, 255, 255))
    rectangle = pygame.Rect(CW, H - bar_width, bar_height * abs(yaw), bar_width)

    pygame.draw.rect(surface, colour_bar, rectangle, 0)
    pygame.draw.rect(surface, colour_bar_background, rectangle, 1)

    if yaw <= 0:
        surface = pygame.transform.flip(surface, True, False)

    surface.set_colorkey((255, 255, 255))
    screen.blit(surface, (0, 0))

    # Draw mode

    # Draw control

    # Draw emergency
