import re
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

def draw(channel, ch1, ch2, grb_title, grb_time, circular_id):
    fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(16, 6))

    bounds = get_bound_indexes(ch1['time'], ch2['time'], grb_time)
    axs[0].scatter(
        ch1['time'][bounds[0]['far'][0]: bounds[0]['far'][1]],
        ch1['value'][bounds[0]['far'][0]: bounds[0]['far'][1]],
        c='red', s=4, label='gamma'
    )
    axs[0].scatter(
        ch2['time'][bounds[1]['far'][0]: bounds[1]['far'][1]],
        ch2['value'][bounds[1]['far'][0]: bounds[1]['far'][1]],
        c='black', s=4, label='electrons'
    )
    axs[1].scatter(
        ch1['time'][bounds[0]['close'][0]: bounds[0]['close'][1]],
        ch1['value'][bounds[0]['close'][0]: bounds[0]['close'][1]],
        c='red', s=4, label='gamma'
    )
    axs[1].scatter(
        ch2['time'][bounds[1]['close'][0]: bounds[1]['close'][1]],
        ch2['value'][bounds[1]['close'][0]: bounds[1]['close'][1]],
        c='black', s=4, label='electrons'
    )

    for ax in axs:
        ax.grid(which="major", linewidth=1.2)
        ax.grid(which="minor", linestyle="--", color="gray", linewidth=0.5)
        ax.xaxis.set_minor_locator(AutoMinorLocator())
        ax.yaxis.set_minor_locator(AutoMinorLocator())
        ax.tick_params(which='major', length=10, width=2)
        ax.tick_params(which='minor', length=5, width=1)
        ax.axvline(x=grb_time, label=f'trigger in {circular_id}')
        ax.set_ylabel('Нормированный поток')
        ax.set_xlabel("Время, unix time")
        ax.set_yscale('log')
        ax.legend()

    channel = re.search(r'\d{1,2}', channel).group()
    fig.suptitle(f'{grb_title} on decor-{channel}, trigger at {grb_time}')

    plt.savefig(f'drawings/{grb_title[-7:]}-{channel}-{grb_time}.png')
    plt.cla(); plt.clf(); plt.close()


def get_bound_indexes(ch1_time, ch2_time, grb_time):
    return [
        {
            'far': [
                find_nearest_idx(ch1_time, grb_time-1000),
                find_nearest_idx(ch1_time, grb_time+1000)-1
            ],
            'close': [
                find_nearest_idx(ch1_time, grb_time-120),
                find_nearest_idx(ch1_time, grb_time+120)-1
            ]
        },
            {
            'far': [
                find_nearest_idx(ch2_time, grb_time-1000),
                find_nearest_idx(ch2_time, grb_time+1000)-1
            ],
            'close': [
                find_nearest_idx(ch2_time, grb_time-120),
                find_nearest_idx(ch2_time, grb_time+120)-1
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