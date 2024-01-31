# Data-cross-with-gcn
Code finds cross of data on satellite from swx with gcn GRB circulars 

To run the program write time interval in findGRBs() in main.py. For example:
findGRBs('avion', '2023-08-12 18:53:12', '2023-08-12 19:03:12'),
here 'avion' is the satellite you want to get data from (if you want to add your sattelite, add it in getChannels() func in get_data.py), '2023-08-12 18:53:12' and '2023-08-12 19:03:12' are time interval (first < second).

Necessary headers to login on downloader.sinp.msu.ru are User-Agent, Referer and Cookie; necessary data is csrfmiddlewaretoken, username, password. I've hidden them in login_headers.json and login_data.json.

In result, there will be graphs of data from downloader.sinp.msu.ru in the moment of GRB trigger time from gcn circulars in two scales: 2000s and 240s.

## Sample result:
![231020A-1-1697828218](https://github.com/justgameartik/Data-cross-with-gcn/assets/112627431/894ca41e-3703-4d9b-bbb2-7c87a635eb83)
Gamma-ray burst registered by "Avion" satellite on 2023.10.20, the gcn circular number 34917 mentions this GRB.

## TODO:
- change draw logic
- add new satellites?
- add check if time interval is invalid?
