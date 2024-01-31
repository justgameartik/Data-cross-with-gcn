import json
import os
import re
import requests
from datetime import datetime, timezone
from tqdm import tqdm

kURL = 'https://gcn.nasa.gov/circulars/'
kFolderPath = 'circulars/'

class TriggerTimes:
  def __init__(self):
    self.trigger_times = {} # key - grb_title, value - trigger_times
    self.circularIds = {} # key trigger_time, value - circularId
    self.boundaries = () # boundaries of circulars to research 

  def __binarySearchForBound(self, time, r_bound, add=0):
    time = int(datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                      .replace(tzinfo=timezone.utc).timestamp())+add
    l = 30000; r = int(r_bound)
    while l < r:
      mean = (l + r) // 2
      circular = self.__getCircular(str(mean)+'.json')
      created_on = circular['createdOn']/1000
      if created_on > time:
        r = mean
      else:
        l = mean + 1

    return r


  def getBoundaries(self, min_time, max_time):
    print('finding boundaries for circulars is in progress')
    URLAllCirculars = 'https://gcn.nasa.gov/circulars?_data=routes%2F_gcn.circulars._archive._index'
    response = requests.get(URLAllCirculars, stream=True)
    r_bound = json.loads(response.content.decode('utf-8'))['items'][0]['circularId']
    l_bound = self.__binarySearchForBound(min_time, r_bound)
    r_bound = self.__binarySearchForBound(max_time, r_bound, 604800)
    self.boundaries = (l_bound, r_bound)
    

  def __getCircular(self, filename):
    if os.path.exists(kFolderPath+filename):
      with open(kFolderPath+filename, 'r') as f:
        return json.load(f)
    
    circular = requests.get(kURL+filename)
    if circular.status_code == requests.codes.ok:
      content = json.loads(circular.content.decode('utf-8'))
      with open(kFolderPath+filename, 'w') as f:
        json.dump(content, f)
      return content
    print(f'Getting file {filename} failed, {circular.reason}')


  def getTriggerTimes(self, min_time, max_time):  
    self.getBoundaries(min_time, max_time)
    grb_times = {}
    for i in tqdm(range(min(self.boundaries), max(self.boundaries)+1)):
      filename = str(i) + '.json'
      content = self.__getCircular(filename)
      grb_title = re.search(r'GRB \d{6}\w', content['subject'])
      if grb_title:
        grb_title = grb_title.group()[-7:]
        self.__getGRBTime(content, grb_title)

    return self.trigger_times, self.circularIds


  def __getGRBTime(self, circular, grb_title):
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