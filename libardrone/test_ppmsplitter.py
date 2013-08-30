import paveparser
import mock
import ppmsplitter
import os

import Image
import cv2
import numpy as np
import StringIO

class DisplayPPMImages():
    def __init__(self, display):
        self.num_image = 0
        self.display = display

    def image_ready(self, image):
        self.num_image += 1
        im = np.asarray(Image.open(StringIO.StringIO(image)))
        if (self.display):
            cv2.imshow("display", np.asarray(im))
            cv2.waitKey(1)

def test_ppmsplitter(display=False):
    listener = DisplayPPMImages(display)
    splitter = ppmsplitter.PPMSplitter(listener)
    example_ppm_stream = open(os.path.join(os.path.dirname(__file__), 'example_ppm_stream.ppm'))
    while True:
        data = example_ppm_stream.read(10000)
        if len(data) == 0:
            break
        splitter.write(data)

    assert listener.num_image == 7

if __name__ == "__main__":
    test_ppmsplitter(True)
