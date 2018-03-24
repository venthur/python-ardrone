import math

notFoundCounter = -1000000


def get_flight_command(offset):

    global notFoundCounter
    if offset is None:
        if notFoundCounter < 3:
            notFoundCounter += 1
            return 0, -0.2, 0.5, 0
        else:
            return None, None, None, None
    notFoundCounter = 0

    return -offset[0], -0.2, -offset[1], 0
