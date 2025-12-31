import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 設定
API_KEY = os.getenv("FLIGHTAWARE_API_KEY")
AIRPORT_CODE = "RJTT"  # 羽田空港
headers = {"x-apikey": API_KEY}


def get_flight_board(board_type="arrivals"):
    """
    board_type: 'arrivals' or 'departures'
    """
    if board_type not in ("arrivals", "departures"):
        print("board_type must be 'arrivals' or 'departures'")
        return
    url = f"https://aeroapi.flightaware.com/aeroapi/airports/{AIRPORT_CODE}/flights/{board_type}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        flights = response.json().get(board_type, [])
        if board_type == "arrivals":
            print(f"--- {AIRPORT_CODE} 到着予定ボード ---")
            print(f"{'便名':<8} | {'出発地':<6} | {'予定時刻(JST)':<20} | {'状態'}")
            print("-" * 60)
            for flight in flights:
                ident = flight.get("ident")
                origin = (
                    flight.get("origin").get("code") if flight.get("origin") else ""
                )
                scheduled_on = flight.get("scheduled_on")
                status = flight.get("status")
                # UTC→JST変換
                jst_time = ""
                if scheduled_on:
                    try:
                        dt_utc = datetime.fromisoformat(
                            scheduled_on.replace("Z", "+00:00")
                        )
                        dt_jst = dt_utc.astimezone()
                        jst_time = dt_jst.astimezone().strftime(
                            "%Y-%m-%d %H:%M:%S (JST)"
                        )
                    except Exception:
                        jst_time = scheduled_on
                print(f"{ident:<8} | {origin:<6} | {jst_time:<20} | {status}")
        else:
            print(f"--- {AIRPORT_CODE} 出発予定ボード ---")
            print(f"{'便名':<8} | {'目的地':<6} | {'出発予定(JST)':<20}")
            print("-" * 50)
            for flight in flights:
                ident = flight.get("ident")
                dest = (
                    flight.get("destination").get("code")
                    if flight.get("destination")
                    else ""
                )
                off_time = flight.get("scheduled_off")
                # UTC→JST変換
                jst_time = ""
                if off_time:
                    try:
                        dt_utc = datetime.fromisoformat(off_time.replace("Z", "+00:00"))
                        dt_jst = dt_utc.astimezone()
                        jst_time = dt_jst.astimezone().strftime(
                            "%Y-%m-%d %H:%M:%S (JST)"
                        )
                    except Exception:
                        jst_time = off_time
                print(f"{ident:<8} | {dest:<6} | {jst_time:<20}")
    else:
        print(f"エラーが発生しました: {response.status_code}")


if __name__ == "__main__":
    import sys

    # コマンドライン引数で切り替え（例: python getArrivalDeparture.py arrivals）
    board_type = sys.argv[1] if len(sys.argv) > 1 else "departures"
    get_flight_board(board_type)
