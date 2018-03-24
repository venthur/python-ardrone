import math

notFoundCounter = -1000000

huegCounter = 0


def get_flight_command(keypoint, offset):
    global notFoundCounter, huegCounter
    if offset is None or offset[0] * offset[0] + offset[1] * offset[1] > 0.6:
        if notFoundCounter < 20:
            notFoundCounter += 1
            print(" NOT FOUND {}".format(notFoundCounter))
            return 0, -0.2, 0.5, 0
        else:
            print("LANDING")
            return None, None, None, None

    else:
        print(keypoint.size)
        if keypoint.size > 150:
            if huegCounter < 5:
                huegCounter += 1
            else:
                print("LANDING B/C OF SIZE")
                return None, None, None, None
        else:
            huegCounter = 0

    notFoundCounter = 0

    return offset[0], -0.2, -offset[1], 0
