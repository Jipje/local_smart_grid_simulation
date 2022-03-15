import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def retrieve_quarters(year=2021):
    starting_times = []
    ending_times = []
    for i in range(4):
        start_month = i * 3 + 1
        end_month = start_month + 3

        if end_month == 13:
            end_q = dt.datetime(year + 1, 1, 1, tzinfo=utc)
        else:
            end_q = dt.datetime(year, end_month, 1, tzinfo=utc)
        start_q = dt.datetime(year, start_month, 1, tzinfo=utc)

        starting_times.append(start_q)
        ending_times.append(end_q)
    return starting_times, ending_times


def retrieve_months(year=2021):
    starting_times = []
    ending_times = []
    for i in range(12):
        start_month = i + 1
        end_month = start_month + 1

        start_period = dt.datetime(year, start_month, 1, tzinfo=utc)

        if end_month > 12:
            year = year + 1
            end_month = 1

        end_period = dt.datetime(year, end_month, 1, tzinfo=utc)

        starting_times.append(start_period)
        ending_times.append(end_period)
    return starting_times, ending_times