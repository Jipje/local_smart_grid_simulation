from pandas import NaT

from helper_objects.congestion_helper.month_congestion_size_and_timer import get_month_congestion_timings
import matplotlib.pyplot as plt
import datetime as dt
import dateutil.tz
from random import randint

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


if __name__ == '__main__':
    res_df = get_month_congestion_timings(verbose_lvl=1)
    print(res_df.to_string())

    prep_starts = res_df.loc['prep_start'].array
    congestion_starts = res_df.loc['congestion_start'].array
    preparing_max_kwh = res_df.loc['prep_max_soc']
    solving_congestion_until = res_df.loc['congestion_end'].array

    prep_starts_y_min = []
    prep_starts_y_max = []
    colors = []
    for i in range(len(prep_starts)):
        if prep_starts[i] is NaT:
            prep_starts[i] = dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
            congestion_starts[i] = dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
            solving_congestion_until[i] = dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
            prep_starts_y_min.append(None)
            prep_starts_y_max.append(None)
        else:
            prep_starts[i] = dt.datetime(1970, 1, 1, prep_starts[i].hour, prep_starts[i].minute, tzinfo=utc)
            congestion_starts[i] = dt.datetime(1970, 1, 1, congestion_starts[i].hour, congestion_starts[i].minute, tzinfo=utc)
            solving_congestion_until[i] = dt.datetime(1970, 1, 1, solving_congestion_until[i].hour, solving_congestion_until[i].minute, tzinfo=utc)
            prep_starts_y_min.append(i * 20)
            prep_starts_y_max.append((i * 20) + 20)
        colors.append('#%06X' % randint(0, 0xFFFFFF))

    for i in range(12):
        y_min = prep_starts_y_min[i]
        y_max = prep_starts_y_max[i]
        color = colors[i]
        plt.plot([prep_starts[i], prep_starts[i]], [y_min, y_max], color=color)
        plt.fill([prep_starts[i], prep_starts[i], congestion_starts[i], congestion_starts[i]], [y_min, y_max, y_max, y_min], color=color, alpha=0.5)
        plt.plot([congestion_starts[i], congestion_starts[i]], [y_min, y_max], color=color)
        plt.fill([congestion_starts[i], congestion_starts[i], solving_congestion_until[i], solving_congestion_until[i]], [y_min, y_max, y_max, y_min], color=color, alpha=0.5)
        plt.plot([solving_congestion_until[i], solving_congestion_until[i]], [y_min, y_max], color=color)

    plt.xlim(dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc), dt.datetime(1970, 1, 1, 23, 59))
    plt.ylim(0, 250)
    plt.show()
