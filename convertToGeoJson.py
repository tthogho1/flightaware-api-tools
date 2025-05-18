import json


def convert_To_GeoJson(data):
    # Script to convert the obtained route information to GeoJSON format
    # Load json file
    positions = []
    # with open("flight_route.json", "r") as f:
    #     data = json.load(f)
    #     # Create a positions list by getting latitude and longitude from the obtained data
    #     for position in data["positions"]:
    #         positions.append(
    #             {
    #                 "latitude": position["latitude"],
    #                 "longitude": position["longitude"],
    #             }
    #         )

    for position in data["positions"]:
        positions.append(
            {
                "latitude": position["latitude"],
                "longitude": position["longitude"],
            }
        )
    # Create the basic structure of GeoJSON
    geojson = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": [[pos["longitude"], pos["latitude"]] for pos in positions],
        },
        "properties": {},
    }

    # Display the result
    print(json.dumps(geojson, ensure_ascii=False, indent=2))
    # Save GeoJSON to a file
    with open("flight_route.geojson", "w") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    return geojson


if __name__ == "__main__":
    convert_To_GeoJson()
