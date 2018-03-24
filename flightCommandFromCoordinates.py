import math

notFoundCounter = -1000000
startCounter = 0


def get_flight_command(offset):
    global notFoundCounter
    global startCounter
    if offset is None or offset[0] * offset[0] + offset[1] * offset[1] > 0.6:
        if startCounter > 30 and notFoundCounter < 20:
            notFoundCounter += 1
            print(" NOT FOUND {}".format(notFoundCounter))
            return 0, -0.2, 0.5, 0
        else:
            print("LANDING")
            return None, None, None, None
    startCounter += 1
    notFoundCounter = 0

    return 0.5*offset[0], -0.2, 0.1-offset[1], 0.2*offset[0]
