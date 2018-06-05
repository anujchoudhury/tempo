import requests
import time

params = (
    ('db', 'NOAA_water_database'),
)

time.sleep(5)   # delays for 5 seconds. You can Also Use Float Value.

data = 'h2o_feet,location=coyote_creek value=0.64 1434055562000000000'

response = requests.post('http://localhost:8086/write', params=params, data=data)

#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.post('http://localhost:8086/write?db=mydb', data=data)
