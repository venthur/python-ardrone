import math

notFoundCounter = -1000000
startCounter = 0

huegCounter = 0
has100 = False
prevFlightSpeed = -0.2

takeoff_limit = 40
notfound_limit = 20

keypoint_minsize = 95
keypoint_maxsize = 115

image_landing_cutoff = 300

def get_flight_command(keypoint, offset):
    global notFoundCounter, huegCounter, startCounter, has100, prevFlightSpeed
    flight_speed = -0.2
    if offset is None or offset[0] * offset[0] + offset[1] * offset[1] > 0.6:
        if startCounter < takeoff_limit or notFoundCounter < notfound_limit:
            notFoundCounter += 1
            print(" NOT FOUND {}".format(notFoundCounter))
            prevFlightSpeed = prevFlightSpeed * 0.85 + 0.15 * flight_speed
            return 0, prevFlightSpeed, 1, 0
        else:
            print("LANDING")
            return None, None, None, None

    else:
        print(keypoint.size)
        flight_speed = max(-0.2, (0.5 + (0.5 - offset[1])) / 2 * -0.4)
        if keypoint.size > keypoint_minsize:

            if keypoint.size >= keypoint_maxsize:
                has100 = True
            if huegCounter < 15:
                huegCounter += 1
            else:
                print("LANDING B/C OF SIZE AND POSITION")
                return None, None, None, None
        else:
            huegCounter = 0
            has100 = False

    startCounter += 1
    notFoundCounter = 0
    prevFlightSpeed = prevFlightSpeed * 0.85 + 0.15 * flight_speed

    return 0.5 * offset[0], prevFlightSpeed, 0.00 - offset[1], 1 * offset[0]
