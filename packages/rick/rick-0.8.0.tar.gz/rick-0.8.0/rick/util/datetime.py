import datetime


def iso8601_now():
    return datetime.datetime.now().astimezone().isoformat()
