import time
import requests
from FlightRadar24 import FlightRadar24API

def get_curr_flight_info(bounds):
    fr_api = FlightRadar24API() # check if this has to be done twice
    flights = fr_api.get_flights(bounds=bounds, details=True)
    for flight in flights:
        if not flight.number: continue
        if flight.on_ground: continue
        return {
            "number": flight.number,
            "origin": flight.origin_airport_name,
            "destination": flight.destination_airport_name,
            "airline": flight.airline_short_name,
            "aircraft": flight.aircraft_code # This needs to be changed, weird short code
        }
        # additional possible information:
        # heading, altitude, vertical speed
    return None

def print_flight_info(flight_info):
    print("\n--- Current passing flight ---")
    print(f"Flight Number: {flight_info['number']}")
    print(f"  From: {flight_info['origin']}")
    print(f"  To:   {flight_info['destination']}")
    print(f"  Airline:   {flight_info['airline']}")
    print(f"  Aircraft:   {flight_info['aircraft']}")
    print()

def get_weather():
    # This website could do a lot more than just temperature (i think)
    try:
        response = requests.get("https://wttr.in/Luxembourg?format=%t", timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException:
        return ""


def main():
    fr_api = FlightRadar24API()
    # Location of Luxembourg 34, Rue Cents
    lux_latitude = 49.6166
    lux_longitude = 6.16

    # 2km, might have to be adapted but flights on ground are ignored
    radius = 2000

    bounds = fr_api.get_bounds_by_point(
        latitude=lux_latitude,
        longitude=lux_longitude,
        radius=radius   
    )

    last_flight = None
    curr_temp = ""

    while True:
        flight_info = get_curr_flight_info(bounds)
        temp_info = get_weather()
        if not flight_info:
            # only show updated temperature if new and valid temp
            if curr_temp == temp_info or not temp_info: continue
            print("Current temperature in Luxembourg:", temp_info)
            curr_temp = temp_info
        elif flight_info != last_flight:
            print_flight_info(flight_info)
            last_flight = flight_info
        time.sleep(5)

if __name__ == "__main__":
    main()
        