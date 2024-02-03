from tqdm import tqdm

from draw import draw, find_nearest_idx
from grb_times import TriggerTimes
from get_data import Connection

def find_GRBs(satellite, min_time, max_time):
    gcn = TriggerTimes()
    trigger_times, circular_ids = gcn.get_trigger_times(min_time, max_time)
    
    account = Connection()
    for channel in account.get_channels(satellite):
        ch1, ch2 = account.get_data(channel, min_time, max_time)
        for grb_title, grb_times in tqdm(trigger_times.items()):
            for grb_time in grb_times:
                nearest_idx = find_nearest_idx(ch1['time'], grb_time)
                if (nearest_idx != -1 and 
                        abs(ch1['time'][nearest_idx] - grb_time) < 100 and 
                        nearest_idx != 0 and
                        abs(ch1['time'][nearest_idx-1] - grb_time) < 100):
                    draw(channel, ch1, ch2, grb_title, grb_time, circular_ids[grb_time])

if __name__ == "__main__":
    find_GRBs('avion', '2024-01-01 00:00:01', '2024-01-31 23:59:59')