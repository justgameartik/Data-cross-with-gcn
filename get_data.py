import json
import numpy as np
import requests
from datetime import datetime, timezone
import os

class Connection:
    def __init__(self):
        self.__login()

    def __login(self):
        LOGIN_URL = 'https://downloader.sinp.msu.ru/accounts/login/'
        with open('login_parameters/login_headers.json', 'r') as f:
            headers = json.load(f)
        with open('login_parameters/login_data.json', 'r') as f:
            data = json.load(f)
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.response = self.session.post(LOGIN_URL, data=data)
        
        if self.response.status_code is not requests.codes.ok:
            print(f"""Failed to authenticate, reason: 
                  {self.response.reason}""")

    def __download_data(self, ch, min_dt, max_dt):
        print(f'getting data for {ch} is in progress, month {datetime.fromtimestamp(min_dt/1000).month}')
        GET_DATA_URL = 'https://downloader.sinp.msu.ru/db_iface/api/v1/query/'
        data_request = {
            "request": {
                "select": [
                    ch+".ch1",
                    ch+".ch2",
                    ch+".ch3",
                ],
                "where": {
                    "resolution": "1s",
                    "min_dt": min_dt,
                    "max_dt": max_dt
                }
            }
        }
        data_response = self.session.post(
            GET_DATA_URL, data=json.dumps(data_request)
        )

        try:
            return json.loads(data_response.content.decode('utf-8'))
        except ValueError:
            print(data_response.reason)
            return self.__download_data(ch, min_dt, max_dt)
  

    def __filter(self, channel):
        channel['value'] = np.where(channel['value'] == None, 0, channel['value'])
        # filter = channel['value'] != None
        # channel['value'] = channel['value'][filter]
        # channel['time'] = channel['time'][filter].astype(np.int64)


    def get_data(self, satellite, ch, min_time, max_time, download=False):
        min_dt = 1000 * int(
            datetime.strptime(min_time, '%Y-%m-%d %H:%M:%S')
            .replace(tzinfo=timezone.utc).timestamp()
            )
        max_dt = 1000 * int(
            datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S')
            .replace(tzinfo=timezone.utc).timestamp()
            )
        data = self.__download_data(ch, min_dt, max_dt)

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

        ch3 = {
            'time': np.array(data['data'][2]['response'])[:, 0]/1000, 
            'value': np.array(data['data'][2]['response'])[:, 1]
        }
        self.__filter(ch3)

        if download:
            print('Starting saving...   ')
            if not os.path.exists(f'data/{satellite}/'):
                os.mkdir(f'data/{satellite}')
                
            np.savetxt(
                f'data/{satellite}/{ch}-{datetime.fromtimestamp(min_dt/1000).month}.txt',
                np.column_stack((ch1['time'], ch1['value'], ch2['value'], ch3['value'])),
                fmt='%1.3f'
            )

        return ch1, ch2, ch3
  

    def get_channels(self, satellite):
        satellites = {
            'avion': [
                'avion.avion_monitoring1',
                'avion.avion_monitoring21',
                'avion.avion_monitoring22',
                'avion.avion_monitoring3'
            ],
            "monitor2": [
                "monitor2.monitor2_monitoring21",
                "monitor2.monitor2_monitoring22",
                "monitor2.monitor2_monitoring31",
                "monitor2.monitor2_monitoring32"
            ],
            "monitor3": [
                "monitor3.monitor3_monitoring21",
                "monitor3.monitor3_monitoring22",
            ],
            "monitor4": [
                "monitor4.monitor4_monitoring21",
                "monitor4.monitor4_monitoring22"
            ],
            "utmn2": [
                "utmn2.utmn2_monitoring21",
                "utmn2.utmn2_monitoring22",
            ],
            "dekart": [
                "dekart.dekart_monitoring2"
            ]
        }

        return satellites[satellite]