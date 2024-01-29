import json
import os
import re
import requests
from datetime import datetime, timezone
from tqdm import tqdm

kURL = 'https://gcn.nasa.gov/circulars/'
kFolderPath = 'circulars/'

def binarySearchForBound(time, r_bound, add=0):
  time = int(datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
                     .replace(tzinfo=timezone.utc).timestamp())+add
  l = 30000; r = int(r_bound)
  while l < r:
    mean = (l + r) // 2
    circular = requests.get(kURL+str(mean)+'.json')
    created_on = json.loads(circular.content.decode('utf-8'))['createdOn']/1000
    if created_on > time:
      r = mean
    else:
      l = mean + 1

  return r


def getBoundaries(min_time, max_time):
  print('finding boundaries for circulars is in progress')
  URLAllCirculars = 'https://gcn.nasa.gov/circulars?_data=routes%2F_gcn.circulars._archive._index'
  response = requests.get(URLAllCirculars, stream=True)
  r_bound = json.loads(response.content.decode('utf-8'))['items'][0]['circularId']
  l_bound = binarySearchForBound(min_time, r_bound)
  r_bound = binarySearchForBound(max_time, r_bound, 604800)
  return (l_bound, r_bound)
    

def getCircular(filename):
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


def getTriggerTimes(min_time, max_time):  
  boundaries = getBoundaries(min_time, max_time)
  grb_times = {}
  for i in tqdm(range(min(boundaries), max(boundaries)+1)):
    filename = str(i) + '.json'
    content = getCircular(filename)
    grb_title = re.search(r'GRB \d{6}', content['subject'])
    if grb_title:
      grb_title = grb_title.group()
      if grb_title not in grb_times:
        grb_times[grb_title] = set()
      grb_times[grb_title] |= getGRBTime(content)

  return grb_times


def getGRBTime(circular):
  circular_times = set()

  date_match = re.search(r'GRB \d{6}(?!\d{2})', circular['subject'])
  if date_match is None:
    date_match = re.search(r'GRB \d{8}(?!\d)', circular['subject'])
  if date_match is None:
    return circular_times
  date_match = date_match.group()[-6:]

  pattern = r'(?<!\+|\-)\d{2}:\d{2}:\d{2}'
  time_matches = re.findall(pattern, circular['body'])
  for time_match in time_matches:
    try:
      circular_times.add(int(datetime.strptime(str(date_match)+str(time_match[:8]), '%y%m%d%H:%M:%S')
                          .replace(tzinfo=timezone.utc).timestamp()))
    except Exception as e:
      print(f'date={date_match}, time={time_match}, circular_id={circular['circularId']}, error={e}')

  return circular_times