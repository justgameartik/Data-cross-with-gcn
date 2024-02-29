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
        # interval of circulars in researching period
        self.boundaries = ()
        # dict, where key is circularId and value is array of times in circular
        self.circular_times = {}
        # dict, where key is circularId and value is grb_title
        self.grb_titles = {}

    def __binary_search_for_bound(self, time, r_bound, add=0):
        time = add + int(
            datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            .replace(tzinfo=timezone.utc).timestamp()
            )
        l = 33000
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

        return self.circular_times, self.grb_titles

    def __get_GRB_time(self, circular, grb_title):
        try:
            circular_id = circular['circularId']
        except KeyError:
            print(f"circularId not found for {grb_title}")
            return

        date_match = grb_title[-7:-1]
        pattern = r'[\s\S]{10}(?<!\+|\-)\d{2}:\d{2}:\d{2}[\s\S]{10}'
        time_matches = self.__validate_time(re.findall(pattern, circular['body']))

        self.grb_titles[circular_id] = grb_title
        self.circular_times[circular_id] = self.__unix_time_convert(
            time_matches, date_match, circular_id)

    def __validate_time(self, time_matches, distance: int = 10):
        wrong_patterns = [
            'dec',
            'j2000',
            'ra'
        ]
        validated_times = []
        
        for time_str in time_matches:
            is_correct = True
            for pattern in wrong_patterns:
                if (re.findall(pattern, time_str.lower()[:distance]) or
                        re.findall(pattern, time_str.lower()[-distance:])):
                    is_correct = False
            if is_correct:
                validated_times.append(time_str[distance:-distance])
        
        return validated_times

    def __unix_time_convert(self, times_str, date, circular_id):
        unix_time_circular = []
        for time in times_str:
            try:
                unix_time_circular.append(
                    int(datetime.strptime(str(date)+str(time[:8]), '%y%m%d%H:%M:%S')
                       .replace(tzinfo=timezone.utc).timestamp())
                    )
            except Exception as e:
                print(f'date={date}, time={time}, circular_id={circular_id}, error={e}')
        
        return unix_time_circular