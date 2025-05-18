import requests
import os
from dotenv import load_dotenv
 
load_dotenv() 

API_KEY = os.getenv("FLIGHTAWARE_API_KEY")
apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
 
payload = {'max_pages': 1}
auth_header = {'x-apikey':API_KEY}

def get_airport_info(airport):
    response = requests.get(apiUrl + f"airports/{airport}", headers=auth_header)
    # no max_pages params required
 
    if response.status_code == 200:
        print(response.json())
    else:
        print("Error executing request")
 
#
#{'airport_code': 'RJNA', 
# 'alternate_ident': 'NKM', 
# 'code_icao': 'RJNA', 
# 'code_iata': 'NKM',
#  'code_lid': None,
#  'name': 'Nagoya Airfield (Prefectural Nagoya)',
#  'type': 'Airport', 
# 'elevation': 52, 
# 'city': 'Toyoyama', 
# 'state': 'Aichi',
#  'longitude': 136.924444,
#  'latitude': 35.255,
#  'timezone': 'Asia/Tokyo',
#  'country_code': 'JP',
#  'wiki_url': 'https://en.wikipedia.org/wiki/Nagoya_Airfield',
#  'airport_flights_url': '/airports/RJNA/flights',
#  'alternatives': []}
#
