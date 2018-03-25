import cv2
import pygame

from flightCommandFromCoordinates import get_flight_command
from recognition import preprocess_image, process_image, draw_keypoint, ProcessingThread
from render import render

cap = cv2.VideoCapture('output.avi')
pygame.init()
W, H = 640, 360
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

need_to_land = False
land_counter = 0

image_mode = False

processor = ProcessingThread()
processor.start()

while cap.isOpened():
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                image_mode = not image_mode
    ret, frame = cap.read()
    imagergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    processor.input_queue.put(imagergb)

    #if keypoint is not None:
        #print(keypoint.pt[0], keypoint.pt[1])

    if not processor.output_queue.empty():
        keypoint, offset, im = processor.output_queue.get()

        if need_to_land and land_counter >= 30:
            print("[DRONE] Landing!")
            if land_counter > 60:
                need_to_land = False
                land_counter = 0
            else:
                land_counter += 1
        elif need_to_land:
            print("Landing in {}".format(land_counter - 30))
            land_counter += 1

        # Process image
        a, b, c, d = get_flight_command(keypoint, offset)
        if a is None:
            need_to_land = True

        if keypoint is None:
            rgb_im = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
        else:
            rgb_im = draw_keypoint(keypoint, im)

        pygame.display.flip()
        render(screen, imagergb, rgb_im, image_mode, offset, keypoint, a, b, c, d, False, False, "AUTOMATIC", False)
        clock.tick(20)
        pygame.display.set_caption("FPS: %.2f" % clock.get_fps())

cap.release()
cv2.destroyAllWindows()
