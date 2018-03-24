import math

notFoundCounter = -1000000


def get_flight_command(offset):

    global notFoundCounter
    if offset is None:
        if notFoundCounter < 20:
            return 0, 0, 0, 0
        else:
            return None, None, None, None
    notFoundCounter = 0

    return -offset[0], 0.5, -offset[1], 0
