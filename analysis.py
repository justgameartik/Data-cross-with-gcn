from tqdm import tqdm

from draw import draw, find_nearest_idx
from grb_times import TriggerTimes
from get_data import Connection

def find_cross(trigger_times, ch1_time):
    for trigger_time in trigger_times:
        nearest_idx = find_nearest_idx(ch1_time, trigger_time)
        if (nearest_idx > 0 and
                abs(ch1_time[nearest_idx] - trigger_time) < 100 and
                abs(ch1_time[nearest_idx-1] - trigger_time) < 100):
            return True
    
    return False

def add_checked_grb(grb_title, grb_with_cross, all_grbs, min_time, is_in_data=False):
    if min_time[5:7] != grb_title[-5:-3]:
        return

    if is_in_data and grb_title not in all_grbs:
        grb_with_cross.add(grb_title)
    all_grbs.add(grb_title)

def find_GRBs(satellite, min_time, max_time):
    gcn = TriggerTimes()
    circular_times, grb_titles = gcn.get_trigger_times(min_time, max_time)
    account = Connection()
    grb_with_cross_total = set(); all_grbs_total = set()
    for channel in account.get_channels(satellite):
        # Getting GRBs where we have data and where we don't 
        grb_with_cross = set(); all_grbs = set()

        ch1, ch2 = account.get_data(channel, min_time, max_time)
        for circular_id, trigger_times in tqdm(circular_times.items()):
            if find_cross(trigger_times, ch1['time']):
                draw(satellite, channel, ch1, ch2, grb_titles[circular_id], trigger_times, circular_id)
                add_checked_grb(grb_titles[circular_id], grb_with_cross, all_grbs, min_time, True)
            add_checked_grb(grb_titles[circular_id], grb_with_cross, all_grbs, min_time)

        grb_with_cross_total |= grb_with_cross
        all_grbs_total |= all_grbs

    with open('GRBs/statistics.txt', 'a') as file:
        file.write(f'{min_time}-{max_time}: see {len(grb_with_cross_total)}, don\'t see {len(all_grbs_total)}\n')
        file.write(', '.join(sorted([grb for grb in grb_with_cross_total]))+'\n')
        file.write(', '.join(sorted([grb for grb in all_grbs_total]))+'\n')