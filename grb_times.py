import re
import requests
import json
from datetime import datetime, timezone
from tqdm import tqdm

kURL = 'https://gcn.nasa.gov/circulars/'

def binarySearchForBound(min_time, r_bound):
  min_time = int(datetime.strptime(min_time, '%Y-%m-%d %H:%M:%S')
                     .replace(tzinfo=timezone.utc).timestamp())
  l = 30000; r = int(r_bound)
  print(type(r))
  while l < r:
    mean = (l + r) // 2
    circular = requests.get(kURL+str(mean)+'.json', stream=True)
    created_on = json.loads(circular.content.decode('utf-8'))['createdOn']/1000
    if created_on > min_time:
      r = mean
    else:
      l = mean + 1

  return r


def getBoundaries(min_time, max_time):
  print('finding boundaries for circulars are in progress')
  URLAllCirculars = 'https://gcn.nasa.gov/circulars?_data=routes%2F_gcn.circulars._archive._index'
  response = requests.get(URLAllCirculars, stream=True)
  r_bound = json.loads(response.content.decode('utf-8'))['items'][0]['circularId']
  l_bound = binarySearchForBound(min_time, r_bound)
  r_bound = binarySearchForBound(max_time, r_bound)
  return (l_bound, r_bound)
    

def getCirculars(min_time, max_time):  
  boundaries = getBoundaries(min_time, max_time)
  grb_times = {}
  for i in tqdm(range(min(boundaries), max(boundaries)+1)):
    filename = str(i) + '.json'
    circular = requests.get(kURL+filename, stream=True)
    if circular.status_code == requests.codes.ok:
      content = json.loads(circular.content.decode('utf-8'))
      grb_pattern = re.compile(r'GRB \d{6}\w')
      grb_title = re.search(grb_pattern, content['subject'])
      if grb_title:
        grb_title = grb_title.group()
        if grb_title not in grb_times:
          grb_times[grb_title] = set()
        trigger_time = getGRBTime(content)
        if trigger_time:
          grb_times[grb_title].add(getGRBTime(content))
    else:
      print(f'Getting file {filename} failed, reason: {circular.reason}')
  
  return grb_times


def getGRBTime(circular):
  patterns = [
    r'\d{2}:\d{2}:\d{2} UT',
    r'\d{2}:\d{2}:\d{2}.\d{2} UT',
    r'\d{2}:\d{2}:\d{2}.\d{3}',
  ]

  time_match = ''
  for pattern in patterns:
    match = re.search(pattern, circular['body'])
    if match:
      time_match = match.group()[:8]
  if time_match == '':
    return
  date_match = re.search(r'GRB \d{6}', circular['subject']).group()[-6:]
  unix_time = datetime.strptime(str(date_match)+str(time_match), '%y%m%d%H:%M:%S').replace(tzinfo=timezone.utc).timestamp()
  return int(unix_time)