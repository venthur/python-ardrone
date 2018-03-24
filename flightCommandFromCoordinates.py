import math

notFoundCounter = -1000000
startCounter = 0

huegCounter = 0
has100 = False

def get_flight_command(keypoint, offset):
    global notFoundCounter, huegCounter, startCounter, has100
    flight_speed = -0.2
    if offset is None or offset[0] * offset[0] + offset[1] * offset[1] > 0.6:
        if startCounter < 30 or notFoundCounter < 20:
            notFoundCounter += 1
            print(" NOT FOUND {}".format(notFoundCounter))
            return 0, flight_speed, 0.5, 0
        else:
            print("LANDING")
            return None, None, None, None

    else:
        print(keypoint.size)
        flight_speed = max(-0.2, -0.3+0.2*keypoint.size/130)
        if keypoint.size > 90:
            if keypoint.size >= 100:
                has100 = True
            if huegCounter < 15:
                huegCounter += 1
            else:
                print("LANDING B/C OF SIZE")
                return None, None, None, None
        else:
            huegCounter = 0
            has100 = False

    startCounter += 1
    notFoundCounter = 0

    return 0.3*offset[0], flight_speed, 0.00-offset[1], 0.5*offset[0]
