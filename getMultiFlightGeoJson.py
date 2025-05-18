# from flightaware.getFlightInfor import get_flight_route
# from flightaware.convertToGeoJson import convert_To_GeoJson
# from flightaware.getFlightNumber import get_flight_numbers_by_airport
import json
from getFlightInfor import get_flight_route
from convertToGeoJson import convert_To_GeoJson
from getFlightNumber import get_flight_numbers_by_airport

colors = [
    "#FF0000",
    "#00FF00",
    "#0000FF",
    "#FFA500",
    "#800080",
    "#FFFF00",
    "#00FFFF",
]


def get_multi_flight_geojson():
    airport = "RJAA"
    flight_data = get_flight_numbers_by_airport(airport)

    # Step 2: Get route information for each flight and convert to GeoJSON format
    geojson_list = []
    for idx, flight in enumerate(flight_data.get("departures", [])):
        fa_flight_id = flight.get("fa_flight_id")
        if fa_flight_id:
            print(f"Processing flight ID: {fa_flight_id}")
            routes = get_flight_route(fa_flight_id)
            geojson = convert_To_GeoJson(routes)

            # Add flight information to properties
            color = colors[idx % len(colors)]
            geojson["properties"] = {
                "name": flight.get("ident"),
                "fa_flight_id": fa_flight_id,
                "color": color,
            }
            # Include geojson in the list
            geojson_list.append(geojson)

    # Step 3: Save GeoJSON to a file
    # Convert to featureCollection format
    feature_collection = {
        "type": "FeatureCollection",
        "features": geojson_list,
    }
    # Save GeoJSON to a file
    with open("multi_flight_route.geojson", "w") as f:
        json.dump(feature_collection, f, ensure_ascii=False, indent=2)

    print("GeoJSON file saved as multi_flight_route.geojson")


if __name__ == "__main__":
    get_multi_flight_geojson()
