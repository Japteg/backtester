import datetime


def clean_time(time_string):
    # time_string should be like "9,20" or "15,00" etc
    time_string = time_string.split(",")
    time_int = [int(t) for t in time_string]
    time = datetime.time(time_int[0], time_int[1])
    return time
