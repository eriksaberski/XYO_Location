import requests
import re
import numpy as np
import math
from itertools import combinations
import json
import time
import datetime
from datetime import datetime
def printj(obj):
    print(json.dumps(obj, indent=2))
import numpy as np
from mpl_toolkits.basemap import Basemap
import  matplotlib.pyplot as plt
import pandas as pd
def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    archivist = 'http://3.80.173.107:11001/'
    headers = {"Authorization": "Bearer YOUR API KEY"}
    request = requests.post(archivist, json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
def get_origin_chain(key, date = ['a','b'], location = ['a', 'b'], radius = 1):
    query = """
        {
          blocksByPublicKey(publicKeys:" """ +key +""" "){
            blocks{bytes,
                humanReadable,
                signedHash
                
            }
          }
        }
        """
    query = re.sub(' ', '', query) #deletes spaces in query that I couldn't get rid of otherwise...
    result = run_query(query); # Execute the query
    result = result["data"]["blocksByPublicKey"][0]['blocks'];  #strips data down to just blocks
    result2 = []
    if date[0] != 'a':
        try:
            start = time.mktime(datetime.strptime(date[0], "%m/%d/%Y").timetuple())
            end = time.mktime(datetime.strptime(date[1], "%m/%d/%Y").timetuple())
            start = start - 7*60*60
            end = end + 17*60*60
        except:
            start = time.mktime(datetime.strptime(date[0], "%m/%d/%Y %H:%M").timetuple())
            end = time.mktime(datetime.strptime(date[1], "%m/%d/%Y %H:%M").timetuple())
        for block in result:
            blockH = block['humanReadable']
            try:
                date = blockH[0]['date']
            except:
                date = blockH[1]['date']
            if date/1000 >= start and date/1000 <= end:
                result2.append(block)
        result = result2
    result2 = []
    if location[0] != 'a':
        
        for block in result:
            blockH = block['humanReadable']
            try:
                try:
                    gps = blockH[0]['gps']
                except:
                    gps = blockH[1]['gps']
            except:
                a=2
                
            distance = coordinate_distance(location, [gps['lat'], gps['lng']])
            if distance < radius:
                result2.append(block)
        result = result2
    return result
def order_chain(chain):
    times = np.ones(len(chain))
    times = times + 10**20
    times = list(times)
    
    result = np.ones(len(chain))
    result = result + 10**10
    result = list(result)
    for block in chain:
        try:
            try:
                date = block['humanReadable'][0]['date']
            except:
                date = block['humanReadable'][1]['date']
        except:
            a=2
        t = 0
        try:
            while date > times[t]:
                t=t+1
            times.insert(t, date)
            result.insert(t, block)
            
            
        except:
            a=2
            times.pop()
            result.pop()
    while 1+10**10 in result:
        result.pop()
    
    return(result)
def get_real_chain(key, time = ['a', 'b'], location = ['a','b']):
    chain = get_origin_chain(key, time, location)
    result = []
    for block in chain: 
        if contains_rssi(block):
            result.append(block)
    return(result)
def contains_rssi(block):
    rssi = False
    try:
        blockH = block['humanReadable']
    except:
        print(block)
        blockH = block['humanReadable']
    for i in range(int(len(blockH)/2)):
        current = blockH[i]
        try:
            current = current['rssi']
            rssi = True
        except:
            a = 2
    return(rssi)
def get_trajectory(key):
    chain = get_real_chain(key)
    chain = order_chain(chain)
    lats = []
    longs = []
    for block in chain:
        try:
            try:
                gps = block['humanReadable'][0]['gps']
            except:
                gps = block['humanReadable'][1]['gps']
        except:
            a=2
        try:
            lats.append(gps['lat'])
            longs.append(gps['lng'])
        except:
            a=2
        
    return([lats,longs])
        
            