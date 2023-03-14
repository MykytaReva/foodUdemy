from datetime import time

def hour_of_day_24():
    return [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0, 24) for m in (0, 30)]

    # for h in range(0, 24):
    #     ch = []
    #     for m in range(0, 30):
    #         t = (time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p'))
    #         ch.append(t)
    # return ch

