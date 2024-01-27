from grb_times import getCirculars
from get_data import Connection

import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from tqdm import tqdm

def draw(ch1, ch2, grb_title, grb_time):
  fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(16, 6))

  bounds = getBoundIndexes(ch1['time'], ch2['time'], grb_time)
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
    ax.axvline(x=grb_time, label='trigger')
    ax.set_ylabel('Нормированный поток')
    ax.set_xlabel("Время, unix time")
    ax.set_yscale('log')
    ax.legend()
  fig.suptitle(f'{grb_title}, trigger at {grb_time}')

  plt.savefig(f'drawings/{grb_title}-{grb_time}.png')
    

def findNearestIdx(time, grb_time):
  left = 0; right = len(time) - 1
  while left < right:
      medium = (left+right) // 2
      if time[medium] > grb_time:
          right = medium
      else:
          left = medium+1
  return right


def getBoundIndexes(ch1_time, ch2_time, grb_time):
  return [
    {
      'far': [
        findNearestIdx(ch1_time, grb_time-1000),
        findNearestIdx(ch1_time, grb_time+1000)-1
      ],
      'close': [
        findNearestIdx(ch1_time, grb_time-120),
        findNearestIdx(ch1_time, grb_time+120)-1
      ]
    },
    {
      'far': [
        findNearestIdx(ch2_time, grb_time-1000),
        findNearestIdx(ch2_time, grb_time+1000)-1
      ],
      'close': [
        findNearestIdx(ch2_time, grb_time-120),
        findNearestIdx(ch2_time, grb_time+120)-1
      ]
    }
  ]


def findGRBs(min_time, max_time):
  trigger_times = getCirculars(min_time, max_time)
  
  account = Connection()
  ch1, ch2 = account.getData(min_time, max_time)
  
  for grb_title, grb_times in tqdm(trigger_times.items()):
    for grb_time in grb_times:
      nearest_idx = findNearestIdx(ch1['time'], grb_time)
      if (nearest_idx != -1 and abs(ch1['time'][nearest_idx] - grb_time) < 100 and 
          nearest_idx != 0 and abs(ch1['time'][nearest_idx-1] - grb_time) < 100):
        draw(ch1, ch2, grb_title, grb_time)

findGRBs('2023-08-12 18:53:12', '2023-08-12 19:03:12')