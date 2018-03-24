import math

already_FOUND = False


def get_flight_command(x, y):
    global already_FOUND
    if x is None or x*x + y*y > 0.3:
        if not already_FOUND:
            return 0, -0.3, 0.5, 0
        else:
            return None, None, None, None
    already_FOUND = True
    return x, -0.3, -y, 0
