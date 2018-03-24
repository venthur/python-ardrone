import cv2
import pygame

from recognition import preprocess_image, process_image, draw_keypoint

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

    if keypoint is None:
        rgb_im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
    else:
        rgb_im = draw_keypoint(keypoint, im)
    surface = pygame.image.frombuffer(rgb_im, (W, H), 'RGB')
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    clock.tick(20)
    pygame.display.set_caption("FPS: %.2f" % clock.get_fps())

cap.release()
cv2.destroyAllWindows()
