import cv2
import pygame

from flightCommandFromCoordinates import get_flight_command
from recognition import preprocess_image, process_image, draw_keypoint
from render import render

cap = cv2.VideoCapture('output.avi')
pygame.init()
W, H = 640, 360
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

while cap.isOpened():
    ret, frame = cap.read()
    imagergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    im = preprocess_image(imagergb)
    keypoint, offset = process_image(im)

    # Process image
    a, b, c, d = get_flight_command(keypoint, offset)
    if a is None:
        print("[DRONE] Landing!")
    else:
        print(a, b, c, d)

    if keypoint is None:
        rgb_im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
    else:
        rgb_im = draw_keypoint(keypoint, im)

    pygame.display.flip()
    render(screen, imagergb, rgb_im, True, offset, keypoint, a, b, c, d, False, False, "AUTOMATIC", False)
    clock.tick(20)
    pygame.display.set_caption("FPS: %.2f" % clock.get_fps())

cap.release()
cv2.destroyAllWindows()
