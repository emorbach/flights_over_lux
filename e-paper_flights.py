#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import time
import requests
from FlightRadar24 import FlightRadar24API
from waveshare_epd import epd7in5_V2
import logging
import time
from flight_maps import AIRPORT_MAP, AIRLINE_MAP, AIRCRAFT_MAP
from PIL import Image,ImageDraw,ImageFont

logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
font_time_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 250)
font_date = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 50)
font_airports = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 175)
font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 45)


def get_curr_flight_info(fr_api, bounds):
    try: 
        # fr_api = FlightRadar24API()
        flights = fr_api.get_flights(bounds=bounds)
        if not flights: return None

        for flight in flights:
            # if not flight.number: continue
            if flight.on_ground: continue

            icao_prefix = flight.callsign[:3] if flight.callsign else ""
            airline_name = AIRLINE_MAP.get(icao_prefix, icao_prefix)
            origin_iata = flight.origin_airport_iata
            dest_iata = flight.destination_airport_iata
            
            return {
                "number": flight.number if flight.number else "",
                "origin": AIRPORT_MAP.get(origin_iata, origin_iata),
                "origin_iata": origin_iata,
                "destination": AIRPORT_MAP.get(dest_iata, dest_iata),
                "destination_iata": dest_iata,
                "airline": airline_name,
                "aircraft": flight.aircraft_code,
                "speed": flight.ground_speed
            }
    except Exception as e:
        logging.error(f"Error fetching flight data: {e}")
        time.sleep(60)
        logging.info("Continue")
        return None
    
    return None

def display_flight_info(epd, flight_info):
    logging.info("New flight detected")
    epd.init_fast()

    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    # Find first matching prefix, otherwise default to a320.bmp
    bmp_file = next(
        (fname for prefix, fname in AIRCRAFT_MAP.items() if flight_info['aircraft'].startswith(prefix)),
        "a320.bmp")
    bmp = Image.open(os.path.join(picdir, bmp_file))
    y_image = (256 - bmp.height) // 2
    Himage.paste(bmp, (15, y_image))
    draw = ImageDraw.Draw(Himage)

    # --- Origin, Destination, Airline, Aircraft ---
    origin = "Origin:"
    airport = flight_info['origin_iata']
    if airport == "LUX":
        origin = "Destination:"
        airport = flight_info['destination_iata']
    airline, aircraft = flight_info['airline'], flight_info['aircraft']

    x_origin, y_origin = 350, 10
    line_gap = 10  # spacing between lines

    # Draw origin and destination labels
    draw.text((x_origin, y_origin), origin, font=font_date, fill=0)
    draw.text((x_origin, y_origin + (draw.textsize(airport, font=font_date)[1] + line_gap)), airport, font=font_airport, fill=0)

    # Aircraft
    draw.text((20, 10), aircraft, font=font_small, fill=0)

    # Airline
    y_airline = y_origin + 200 + 2*line_gap
    draw.text((20, y_airline), airline, font=font_date, fill=0)

    # Flight number
    y_flight_no = y_airline + 70
    draw.text((20, y_flight_no), flight_info['number'], font=font_date, fill=0)   
    
    # Full airport name 
    from_text = AIRPORT_MAP.get(airport, airport)
    y_from = y_flight_no + 80
    draw.text((20, y_from), from_text, font=font_small, fill=0)

    # Send to e-paper
    epd.display(epd.getbuffer(Himage))
    epd.sleep()


def display_time(epd, time, date, temperature):
    logging.info("Updating time and weather")
    epd.init_fast()

    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)
    
    # --- Center the time ---
    w_time, h_time = draw.textsize(time, font=font_time_big)
    x_time = (epd.width - w_time) // 2
    y_time = (epd.height // 2) - ((h_time+50) // 2)  # slightly above center
    draw.text((x_time, y_time), time, font=font_time_big, fill=0)

    # --- Put the date below the time ---
    x_date = x_time  # align left with time
    y_date = y_time + h_time + 10  # small gap below time
    draw.text((x_date, y_date), date, font=font_date, fill=0)

    # --- Temperature in lower-right corner of time ---
    w_temp, h_temp = draw.textsize(temperature, font=font_date)
    x_temp = x_time + w_time - w_temp  # theoretisch aligned links
    y_temp = y_time + h_time + 10  # small gap below time
    draw.text((x_temp, y_temp), temperature, font=font_date, fill=0)

    # Send to e-paper
    epd.display(epd.getbuffer(Himage))
    epd.sleep()


def print_flight_info(flight_info):
    print("\n--- Current passing flight ---")
    print(f"Flight Number: {flight_info['number']}")
    print(f"  From: {flight_info['origin']}")
    print(f"  To:   {flight_info['destination']}")
    print(f"  Airline:   {flight_info['airline']}")
    print(f"  Aircraft:   {flight_info['aircraft']}")
    print(f"  Speed:   {flight_info['speed']}")
    print()

def get_weather(session):
    # This website could do a lot more than just temperature (i think)
    try:
        response = session.get("https://wttr.in/Luxembourg?format=%t", timeout=5)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException:
        logging.error("Weather could not be found")
        return ""


def main():
    fr_api = FlightRadar24API(timeout=5)
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

    session = requests.session()

    try:
        logging.info("start")
        epd = epd7in5_V2.EPD()

        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        origin = None
        destination = None
        curr_temp = ""
        last_time = time.time()
        last_weather_time = 0
        flight = 1

        # add error handling!!
        while True:
            flight_info = get_curr_flight_info(fr_api, bounds)            
            now = time.time()

            # No flight passing, therefore display time and temperature
            if not flight_info:

                # update weather every 15mins and check night
                if now - last_weather_time > 900:
                    temp = get_weather(session)
                    if temp: curr_temp = temp
                    last_weather_time = now
                    t = time.localtime()
                    if t.tm_hour > 22 or t.tm_hour < 6:
                        logging.info("Night mode. Sleeping...")
                        epd.init()
                        epd.Clear()
                        epd.sleep()
                        while t.tm_hour > 22 or t.tm_hour < 6:
                            time.sleep(3600)
                            # get new api here?
                
                # only update once per minute
                current_time = time.strftime("%H:%M")
                if current_time == last_time and not flight: continue
                last_time = current_time
                display_time(epd, current_time, time.strftime("%d. %B %Y"), curr_temp)
                flight = 0

            elif flight_info['origin_iata'] != origin or flight_info['destination_iata'] != destination:
                if (flight_info['speed'] > 300): continue
                display_flight_info(epd, flight_info)
                origin = flight_info['origin_iata']
                destination = flight_info['destination_iata']
                flight = 1

            time.sleep(20)


    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd.init()
        epd.Clear()
        epd7in5_V2.epdconfig.module_exit(cleanup=True)
        exit()


if __name__ == "__main__":
    main()
        