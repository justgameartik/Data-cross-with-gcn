import re
import matplotlib.pyplot as plt
from matplotlib import dates
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from datetime import datetime, timezone

def draw(satellite, channel, ch1, ch2, grb_title, grb_times, circular_id):
    fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(16, 6))

    bounds = get_bound_indexes(ch1['time'], ch2['time'], grb_times)
    axs[0].plot(
        clock(ch1['time'][bounds[0]['far'][0]: bounds[0]['far'][1]]),
        ch1['value'][bounds[0]['far'][0]: bounds[0]['far'][1]],
        c='red', linewidth=1, label='gamma'
    )
    axs[0].plot(
        clock(ch2['time'][bounds[1]['far'][0]: bounds[1]['far'][1]]),
        ch2['value'][bounds[1]['far'][0]: bounds[1]['far'][1]],
        c='black', linewidth=1, label='electrons'
    )
    axs[1].scatter(
        clock(ch1['time'][bounds[0]['close'][0]: bounds[0]['close'][1]]),
        ch1['value'][bounds[0]['close'][0]: bounds[0]['close'][1]],
        c='red', s=4, label='gamma'
    )
    axs[1].scatter(
        clock(ch2['time'][bounds[1]['close'][0]: bounds[1]['close'][1]]),
        ch2['value'][bounds[1]['close'][0]: bounds[1]['close'][1]],
        c='black', s=4, label='electrons'
    )
    
    axs[0].xaxis.set_major_formatter(dates.DateFormatter('%H:%M'))
    axs[1].xaxis.set_major_formatter(dates.DateFormatter('%H:%M:%S'))
    for ax in axs:
        ax.grid(which="major", linewidth=1.2)
        ax.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.tick_params(which='major', length=10, width=2)
        ax.tick_params(which='minor', length=5, width=1)
        for grb_time in grb_times: 
            ax.axvline(x=clock([grb_time])[0])
        ax.set_ylabel('Нормированный поток')
        ax.set_xlabel("Время, unix time")
        ax.set_yscale('log')
        ax.legend()

    channel = re.search(r'monitoring\d{1,2}', channel).group()
    channel = re.search(r'\d{1,2}', channel).group()
    fig.suptitle(f'{grb_title} on {satellite}-{channel}, circularId - {circular_id}')
    fig.autofmt_xdate()

    plt.savefig(f'drawings/{grb_title[-7:]}-{channel}-{circular_id}.png')
    plt.cla(); plt.clf(); plt.close()


def get_bound_indexes(ch1_time, ch2_time, grb_times):
    left_bound = min(grb_times)
    right_bound = max(grb_times)
    return [
        {
            'far': [
                find_nearest_idx(ch1_time, left_bound-600),
                find_nearest_idx(ch1_time, right_bound+600)-1
            ],
            'close': [
                find_nearest_idx(ch1_time, left_bound-60),
                find_nearest_idx(ch1_time, right_bound+120)-1
            ]
        },
            {
            'far': [
                find_nearest_idx(ch2_time, left_bound-600),
                find_nearest_idx(ch2_time, right_bound+600)-1
            ],
            'close': [
                find_nearest_idx(ch2_time, left_bound-60),
                find_nearest_idx(ch2_time, right_bound+60)-1
            ]
        }
    ]

def find_nearest_idx(time, grb_time):
    left = 0; right = len(time) - 1
    while left < right:
        medium = (left+right) // 2
        if time[medium] > grb_time:
            right = medium
        else:
            left = medium+1
    return right

def clock(time_lst):
    return [datetime.fromtimestamp(time, timezone.utc) for time in time_lst]