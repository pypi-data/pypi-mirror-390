from datetime import datetime

date_fmt = "%Y-%m-%d"
datetime_fmt = "%Y-%m-%d %H:%M:%S"

# datetime.isoformat()
# datetime.fromisoformat(str)


def datetime2str(dt):
    return datetime.strftime(dt, datetime_fmt)


def str2datetime(s):
    return datetime.strptime(s, datetime_fmt)
