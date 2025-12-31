from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

# .envからAPIキーを取得
load_dotenv()
API_KEY = os.getenv("FLIGHTAWARE_API_KEY")
headers = {"x-apikey": API_KEY}

# MCPサーバの初期化
mcp = FastMCP("FlightAware-Tracker")


@mcp.tool()
def get_departures(airport_code: str):
    """指定された空港の出発便リストを取得します。"""
    url = f"https://aeroapi.flightaware.com/aeroapi/airports/{airport_code}/flights/departures"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # AIが読みやすいようにデータを整形して返す
        return response.json().get("departures", [])
    return "データが取得できませんでした。"


if __name__ == "__main__":
    mcp.run()
