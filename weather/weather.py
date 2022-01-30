import pandas as pd
import os
import sys

import pandas as pd
from urllib.request import urlopen
import json
import numpy as np



def main():

# complete_noaa_weather_grid = pd.read_csv(
#     "https://www.ncei.noaa.gov/access/services/data/v1?dataset=global-marine&dataTypes=WIND_DIR,WIND_SPEED&startDate=2019-12-21&endDate=2019-12-22&boundingBox=42,-72,40,-70"
# )



    WIND_SPEED = "wind_speed"
    WIND_DEG = "wind_deg"
    SPEED = "speed"
    DEG = "deg"

    WIND_RAD = "wind_rad"
    WIND_DEG = "wind_deg"
    LAT = "lat"
    LON = "lon"


    API_KEY = "638cafd5f78c877a2169df3f20322a7a"
    lat0 = 42.3
    lon0 = -71
    delta = 1


    #open weather map grid query
    grid = pd.DataFrame()
    lat0 = 42
    lon0 = -71
    inc = .5
    for delta in inc*np.array( [-2,-1,0,1,2]):
        for delta2 in inc*np.array( [-2,-1,0,1,2]):
            
                url = f"https://api.openweathermap.org/data/2.5/onecall?lat={delta+lat0}&lon={delta2+lon0}&appid={API_KEY}"

    
                # store the response of URL
                response = urlopen(url)


                # storing the JSON response 
                # from url in data
                data_json = json.loads(response.read())
                grid = pd.concat([grid,pd.DataFrame(
                    pd.Series(data_json["current"]).append(pd.Series(data_json))
                ).T])

                
                
    # open weather map cities query
    cities = [
    "Quincy",
    "South Boston",
    "Boston",
    "Jamaica Plain",
    "Cambridge",
    "Newton",
    "Brockton",
    "Hanover",
    "Peabody",
    "Framingham",
    "Ashland",
    "Tewksbury",
    "Gloucester",
    "Taunton",
    "Marlborough",
    "Lowell",
    "Attleboro",
    "Milford",
    "Lawrence",
    "Woonsocket",
    "Somerset",
    "Amesbury",
    "Providence",
    "Nashua",
    "Worcester",
    "Leominster",
    "Fall River",
    "Derry Village",
    "New Bedford",
    "Warwick",
    "Manchester",
    "Gardner",
    # "Portsmouth",
    "Killingly Center",
    "Barnstable",
    "Yarmouth",
    "North Kingstown",
    "Dover",
    # "Plainfield",
    "Concord",
    # "East Concord",
    "Westerly",
        "Provincetown",
        "Springfield",
    ]



    city_grid = pd.DataFrame()

    for c in cities:
            url = f'https://api.openweathermap.org/data/2.5/weather?q={c.replace(" ","%20")},MA,US&appid={API_KEY}'
            response = urlopen(url)

            data_json = json.loads(response.read())


            city_grid = pd.concat([city_grid,pd.DataFrame(
                    pd.Series(data_json["wind"]
                            ).append(pd.Series(data_json["coord"])).append(pd.Series(data_json))
                ).T.assign(**{"name":c})],ignore_index=True)

            
            
    #grid combination and output
    both_grids =     pd.concat([
            city_grid,
            grid.rename({WIND_DEG:DEG,WIND_SPEED:SPEED},axis=1).assign(**{"name":"station"})])
    both_grids[SPEED] = both_grids[SPEED].astype(float)
    both_grids[DEG] = both_grids[DEG].astype(float)
    # both_grids[RAD] = both_grids[DEG].astype(float)/180 *np.pi

    both_grids.set_index("name")[[LAT,LON,DEG,SPEED]].rename(
        {
            LAT:"Lat",
            LON:"Lon"
        }
    ,axis=1).to_csv("../_data/weather.csv")







if __name__=="__main__":
    os.chdir(os.path.dirname(sys.argv[0]))
    main()