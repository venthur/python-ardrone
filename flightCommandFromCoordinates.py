import math

notFoundCounter = -1000000


def get_flight_command(offset):
    global notFoundCounter
    if offset is None or offset[0] * offset[0] + offset[1] * offset[1] > 0.6:
        if notFoundCounter < 20:
            notFoundCounter += 1
            print(" NOT FOUND {}".format(notFoundCounter))
            return 0, -0.2, 0.5, 0
        else:
            print("LANDING")
            return None, None, None, None
    notFoundCounter = 0

    return offset[0], -0.2, -offset[1], 0
