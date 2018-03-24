import pygame

# Dimensions
W, H = 640, 360

# Colours
colour_stop = (255, 0, 0)
colour_mode = (0, 0, 255)
colour_control = (0, 255, 255)
colour_target = (255, 0, 255)
colour_reticle = (255, 0, 0)
colour_crosshair = (0, 0, 0)
colour_bars = (0, 255, 0)


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

    # Draw reticule

    # Draw crosshair

    # Draw thrust

    # Draw vertical

    # Draw rotation

    # Draw strafe

    # Draw mode

    # Draw control

    # Draw emergency
