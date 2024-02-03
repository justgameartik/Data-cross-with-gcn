import json
import os
import re
import requests
from datetime import datetime, timezone
from tqdm import tqdm

GCN_URL = 'https://gcn.nasa.gov/circulars/'
CIRCULAR_FOLDER_PATH = 'circulars/'
URL_ALL_CIRCULARS = 'https://gcn.nasa.gov/circulars?_data=routes%2F_gcn.circulars._archive._index'

class TriggerTimes:
    def __init__(self):
        self.trigger_times = {} # key - grb_title, value - trigger_times
        self.circularIds = {} # key trigger_time, value - circularId
        self.boundaries = () # boundaries of circulars to research     

    def __binary_search_for_bound(self, time, r_bound, add=0):
        time = add + int(
            datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            .replace(tzinfo=timezone.utc).timestamp()
            )
        l = 30000
        r = int(r_bound)
        while l < r:
            mean = (l + r) // 2
            circular = self.__getCircular(str(mean)+'.json')
            created_on = circular['createdOn']/1000
            if created_on > time:
                r = mean
            else:
                l = mean + 1

        return r

    def calc_boundaries(self, min_time, max_time):
        print('finding boundaries for circulars is in progress')
        
        response = requests.get(URL_ALL_CIRCULARS, stream=True)
        r_bound = json.loads(response.content.decode('utf-8'))
        r_bound = r_bound['items'][0]['circularId']
        
        l_bound = self.__binary_search_for_bound(min_time, r_bound)
        r_bound = self.__binary_search_for_bound(max_time, r_bound, 604800)
        self.boundaries = (l_bound, r_bound)

    def __getCircular(self, filename):
        if os.path.exists(CIRCULAR_FOLDER_PATH+filename):
            with open(CIRCULAR_FOLDER_PATH+filename, 'r') as f:
                return json.load(f)

        circular = requests.get(GCN_URL+filename)
        if circular.status_code == requests.codes.ok:
            content = json.loads(circular.content.decode('utf-8'))
            with open(CIRCULAR_FOLDER_PATH+filename, 'w') as f:
                json.dump(content, f)
            return content
        print(f'Getting file {filename} failed, {circular.reason}')

    def get_trigger_times(self, min_time, max_time):  
        self.calc_boundaries(min_time, max_time)
        grb_times = {}
        for i in tqdm(range(min(self.boundaries), max(self.boundaries)+1)):
            filename = str(i) + '.json'
            content = self.__getCircular(filename)
            grb_title = re.search(r'GRB \d{6}\w', content['subject'])
            if grb_title:
                grb_title = grb_title.group()[-7:]
                self.__get_GRB_time(content, grb_title)

        return self.trigger_times, self.circularIds

    def __get_GRB_time(self, circular, grb_title):
        date_match = grb_title[-7:-1]

        pattern = r'(?<!\+|\-)\d{2}:\d{2}:\d{2}'
        time_matches = re.findall(pattern, circular['body'])
        for time_match in time_matches:
            if grb_title not in self.trigger_times:
                self.trigger_times[grb_title] = []
            try:
                trigger_time = int(datetime.strptime(str(date_match)+str(time_match[:8]), '%y%m%d%H:%M:%S')
                                  .replace(tzinfo=timezone.utc).timestamp())
                self.trigger_times[grb_title].append(trigger_time)
                self.circularIds[trigger_time] = circular['circularId']
            except Exception as e:
                print(f'date={date_match}, time={time_match}, circular_id={circular['circularId']}, error={e}')