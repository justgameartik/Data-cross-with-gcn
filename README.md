# Data-cross-with-gcn
Code finds cross of data on satellite from swx with gcn GRB circulars 

To run the program write time interval in findGRBs() in main.py. For example:
findGRBs('2023-08-12 18:53:12', '2023-08-12 19:03:12')

Necessary headers to login on downloader.sinp.msu.ru are User-Agent, Referer and Cookie; necessary data is csrfmiddlewaretoken, username, password. I've hidden them in login_headers.json and login_data.json.

In result, there will be graphs of data from downloader.sinp.msu.ru in the moment of GRB trigger time from gcn circulars in two scales: 2000s and 240s.