import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

API_KEY = os.getenv("FLIGHTAWARE_API_KEY")
apiUrl = "https://aeroapi.flightaware.com/aeroapi/"
auth_header = {"x-apikey": API_KEY}


def get_flight_route(fa_flight_id):
    # Step 2: Get route information with the obtained fa_flight_id
    track_response = requests.get(
        apiUrl + f"flights/{fa_flight_id}/track", headers=auth_header
    )

    if track_response.status_code == 200:
        print(track_response.json())
        # Want to output json to a file
        with open("flight_route.json", "w") as f:
            f.write(json.dumps(track_response.json(), ensure_ascii=False, indent=2))

    else:
        print(f"Route retrieval error: {track_response.status_code}")
    return track_response.json()


if __name__ == "__main__":
    fa_flight_id = "ANA182-1747206976-airline-1811p"
    get_flight_route(fa_flight_id)
