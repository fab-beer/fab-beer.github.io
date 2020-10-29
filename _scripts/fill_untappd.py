
from pyquery import PyQuery as pq
import urllib.request, urllib.error, urllib.parse
import os
import sqlite3
import requests
import os,sys
import pytz
import time
import json
import sqlite3
import requests
import calendar
from dateutil import parser as dateparser
from requests.exceptions import HTTPError


def fillforward():

    requests.packages.urllib3.disable_warnings()

    db_file = os.path.join(os.getcwd(), 'untappd.db')
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    create = """
    create table if not exists checkins (
        cid INTEGER PRIMARY KEY,
        timestamp INTEGER NOT NULL,
        beer VARCHAR NOT NULL,
        venue VARCHAR NOT NULL,
        json VARCHAR NOT NULL,
        purchased VARCHAR NOT NULL
    )"""

    c.execute(create)

    UTC = pytz.utc
    EST = pytz.timezone('America/New_York')

    api_id     = 'E8847D1FA347C37248DEC90E1D21568E18FC5152'
    api_secret = '199C86117D183A9B6BCB3220098F34CFF81FD562'
    brewery_checkin_url = 'https://api.untappd.com/v4/brewery/checkins/451812'

    url = brewery_checkin_url
    params = {
        'client_id'     : api_id,
        'client_secret' : api_secret,
    }


    c.execute('select max(cid) from checkins')
    row = c.fetchone()
    if row and row[0]:
        existing_max_id = row[0]
    else:
        0


    # print(row)
    # if 'min_id' in params:
    #      del params['min_id']
    # params["min_id"] = 955494202
    
    #print(params["min_id"])

    while True:
        print(params)
        print("REPEATING")

        try:
            r = requests.get(url, params=params)
            r.raise_for_status()

        except HTTPError:
            break

        

        response = r.json()['response']
        checkins = response['checkins']
        print(len(checkins))
        max_id = None
        #print(checkins)
        print(f'N checks: {len(checkins)}')
        for checkin in checkins['items']:
            # #print (checkin)
            cid = checkin['checkin_id']
            # if cid == params['min_id']:
            #     continue
            # elif cid < params['min_id']:
            #     print('wtf, queried for min_id', params['min_id'], 'and got', cid)
            #     continue
            # if not max_id or cid > max_id: max_id = cid

            if max_id is None or cid < max_id:
                max_id = cid

            when_utc = dateparser.parse(checkin['created_at'])
            timestamp = calendar.timegm(when_utc.timetuple())
            when = EST.normalize(when_utc.astimezone(UTC))
            beer = checkin['beer']['beer_name']
            venue = checkin['venue']['venue_name'] if checkin['venue'] else ''
            checkin_json = json.dumps(checkin)
            purchased = ''

            
            #print(cid, when, beer.encode('utf8'), venue.encode('utf8'))
            c.execute('INSERT OR REPLACE INTO checkins(cid, timestamp, beer, venue, json,purchased) values (?, ?, ?, ?, ?,?)', \
                      (cid, timestamp, beer, venue, checkin_json,purchased))

        print(len(checkins['items']))


        if max_id is None:
            print("QUITTING")
            break
        #print("COMMITTING")
        conn.commit()
        params['max_id'] = max_id
        if max_id < existing_max_id:
            break
    conn.commit()


def attach_venues():
    url = 'http://untappd.com/fabcans'
    response = urllib.request.urlopen(url)
    webContent = response.read()
    d = pq(webContent)

    #alternate formulation, pullls from a downloaded HTML file
    #d = pq(filename="FAB 10-days.html")
    all_checkins = [e for e in d(".item") if pq(e).attr("data-checkin-id") is not None]
    meta = [ {"checkin":pq(e).attr("data-checkin-id"),
    "purchased": pq(e)(".purchased a").attr("href")} for e in all_checkins]

    requests.packages.urllib3.disable_warnings()
    db_file = os.path.join(os.getcwd(), 'untappd.db')
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    for item in meta:
        cid = item["checkin"]
        p = item["purchased"]
        if p is None:
            continue
        print(p)
        c.execute('update checkins set purchased= ? where cid = ?',(p,cid))    
    conn.commit()

# def backfill():

#     requests.packages.urllib3.disable_warnings()

#     db_file = os.path.join(os.getcwd(), 'untappd.db')
#     conn = sqlite3.connect(db_file)
#     c = conn.cursor()

#     c.execute('select min(cid) from checkins')
#     row = c.fetchone()



#     api_id     = 'E8847D1FA347C37248DEC90E1D21568E18FC5152'
#     api_secret = '199C86117D183A9B6BCB3220098F34CFF81FD562'
#     brewery_checkin_url = 'https://api.untappd.com/v4/brewery/checkins/451812'

#     url = brewery_checkin_url
#     params = {
#         'client_id'     : api_id,
#         'client_secret' : api_secret,
#         'limit'         : 100,
#     }

#     if row and row[0]:
#         params['max_id'] = row[0]

#     while True:
#         print(params)
#         r = requests.get(url, params=params)
#         r.raise_for_status()
#         response = r.json()['response']
#         checkins = response['checkins']
#         min_id = None
#         for checkin in checkins['items']:
#             cid = checkin['checkin_id']
#             if params['max_id'] and cid == params['max_id']:
#                 continue
#             if params['max_id'] and cid > params['max_id']:
#                 continue
#             if not min_id or cid < min_id: min_id = cid
#             when_utc = dateparser.parse(checkin['created_at'])
#             timestamp = int(when_utc.strftime('%s'))
#             when = EST.normalize(when_utc.astimezone(UTC))
#             beer = checkin['beer']['beer_name']
#             venue = checkin['venue']['venue_name'] if checkin['venue'] else ''
#             checkin_json = json.dumps(checkin)
#             print(cid, when, beer, venue)
#             c.execute('INSERT INTO checkins(cid, timestamp, beer, venue, json) values (?, ?, ?, ?, ?)', \
#                       (cid, timestamp, beer, venue, checkin_json))
#         conn.commit()
#         params['max_id'] = min_id
#         time.sleep(5)

def get_last_checkin(venue):
     c.execute('select max(timestamp) from checkins where venue=?', (venue,))
     row = c.fetchone()
     return row[0] if row and row[0] else None

def run():
    fillforward()
    attach_venues()
    
if __name__ == '__main__':
    os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

    run()