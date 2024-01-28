import json
import numpy as np
import requests
from datetime import datetime, timezone

class Connection:
  def __init__(self):
    self.__login()


  def __login(self):
    login_url = 'https://downloader.sinp.msu.ru/accounts/login/'
    with open('login_headers.json', 'r') as f:
      headers = json.load(f)
    with open('login_data.json', 'r') as f:
      data = json.load(f)
    self.session = requests.Session()
    self.session.headers.update(headers)
    self.response = self.session.post(login_url, data=data)
    
    if self.response.status_code is not requests.codes.ok:
      print(f"Failed to authenticate, reason: {self.response.reason}")


  def __downloadData(self, ch, min_dt, max_dt):
    print('getting data is in progress')
    get_data_url = 'https://downloader.sinp.msu.ru/db_iface/api/v1/query/'
    data_request = {
      "request": {
        "select": [
          ch+".ch1",
          ch+".ch2"
        ],
        "where": {
          "resolution": "1s",
          "min_dt": min_dt,
          "max_dt": max_dt
        }
      }
    }

    data_response = self.session.post(get_data_url, data=json.dumps(data_request))
    return json.loads(data_response.content.decode('utf-8'))
  

  def __filter(self, channel):
    filter = channel['value'] != None
    channel['value'] = channel['value'][filter]
    channel['time'] = channel['time'][filter].astype(np.int64)


  def getData(self, ch, min_time, max_time):
    min_dt = int(datetime.strptime(min_time, '%Y-%m-%d %H:%M:%S')
                  .replace(tzinfo=timezone.utc).timestamp())*1000
    max_dt = int(datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S')
                  .replace(tzinfo=timezone.utc).timestamp())*1000
    data = self.__downloadData(ch, min_dt, max_dt)

    ch1 = {
      'time': np.array(data['data'][0]['response'])[:, 0]/1000, 
      'value': np.array(data['data'][0]['response'])[:, 1]
    }
    self.__filter(ch1)

    ch2 = {
      'time': np.array(data['data'][1]['response'])[:, 0]/1000, 
      'value': np.array(data['data'][1]['response'])[:, 1]
    }
    self.__filter(ch2)

    return ch1, ch2
  

  def getChannels(self, satellite):
    satellites = {
      'avion': [
        'avion.avion_monitoring1_flux',
        'avion.avion_monitoring21_flux',
        'avion.avion_monitoring22_flux',
        'avion.avion_monitoring3_flux'
      ]
    }

    return satellites[satellite]