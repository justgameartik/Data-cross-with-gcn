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

def find_GRBs(satellite, min_time, max_time):
    gcn = TriggerTimes()
    circular_times, grb_titles = gcn.get_trigger_times(min_time, max_time)
    
    account = Connection()
    for channel in account.get_channels(satellite):
        ch1, ch2 = account.get_data(channel, min_time, max_time)
        for circular_id, trigger_times in tqdm(circular_times.items()):
            if find_cross(trigger_times, ch1['time']):
                draw(channel, ch1, ch2, grb_titles[circular_id], trigger_times, circular_id)


if __name__ == "__main__":
    find_GRBs('avion', '2024-01-01 00:00:01', '2024-01-31 23:59:59')