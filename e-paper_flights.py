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
from PIL import Image,ImageDraw,ImageFont

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
font_time_big = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 250)
font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
font_very_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 25)
font_date = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 50)
font_airports = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 80)

# Mapping of aircraft name prefixes → image file
aircraft_map = {
    "Airbus": "a320.bmp",
    "Boeing 737": "boeing737.bmp",
    "Boeing 747": "boeing747.bmp",
    "De Havilland": "bombardier_dash8.png",
}



def get_curr_flight_info(bounds):
    fr_api = FlightRadar24API() # check if this has to be done twice (timeout?)
    flights = fr_api.get_flights(bounds=bounds, details=True)
    for flight in flights:
        if not flight.number: continue
        if flight.on_ground: continue
        return {
            "number": flight.number,
            "origin": flight.origin_airport_name,
            "origin_iata": flight.origin_airport_iata,
            "destination": flight.destination_airport_name,
            "destination_iata": flight.destination_airport_iata,
            "airline": flight.airline_short_name,
            "aircraft": flight.aircraft_model,
            "speed": flight.ground_speed
        }
        # additional possible information:
        # heading, altitude, vertical speed
    return None

def display_flight_info(epd, flight_info, time):
    logging.info("New flight detected")
    epd.init_fast()

    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    # Find first matching prefix, otherwise default to a320.bmp
    bmp_file = next(
        (fname for prefix, fname in aircraft_map.items() if flight_info['aircraft'].startswith(prefix)),
        "a320.bmp")
    bmp = Image.open(os.path.join(picdir, bmp_file))
    y_image = (256 - bmp.height) // 2
    Himage.paste(bmp, (15, y_image))
    draw = ImageDraw.Draw(Himage)

    # --- Current time (top-right corner) ---
    w_time, _ = draw.textsize(time, font=font_small)
    x_time = epd.width - w_time -10
    y_time = 10
    draw.text((x_time, y_time), time, font=font_small, fill=0)

    # --- Origin, Destination, Airline, Aircraft ---
    origin, destination = "Origin: ", "Dest:"
    flight_origin, flight_destination = flight_info['origin_iata'], flight_info['destination_iata']
    airline, aircraft = flight_info['airline'], flight_info['aircraft']

    x_origin, y_origin = 300, 80
    line_gap = 20  # spacing between lines

    # Draw origin and destination labels
    draw.text((x_origin, y_origin), origin, font=font_airports, fill=0)
    draw.text((x_origin, y_origin + (draw.textsize(destination, font=font_airports)[1] + line_gap)), destination, font=font_airports, fill=0)

    # Draw airport codes aligned with labels
    w_origin, h_origin = draw.textsize(origin, font=font_airports)
    draw.text((x_origin + w_origin + 10, y_origin), flight_origin, font=font_airports, fill=0)
    draw.text((x_origin + w_origin + 10, y_origin + h_origin + line_gap), flight_destination, font=font_airports, fill=0)

    # Airline (right-aligned with airport codes) and aircraft (left side)
    w_airline, _ = draw.textsize(airline, font=font_small)
    w_airport, _ = draw.textsize(flight_destination, font=font_airports)

    x_airline = x_origin + w_origin + 10 + w_airport - w_airline
    y_airline = y_origin + h_origin * 2 + line_gap
    draw.text((x_airline, y_airline), airline, font=font_small, fill=0)
    draw.text((20, y_airline), aircraft, font=font_small, fill=0)

    # --- From / To ---
    flight_no = f"Flight Number: {flight_info['number']}"
    from_text = f"{flight_info['origin_iata']}: {flight_info['origin']}"
    to_text   = f"{flight_info['destination_iata']}: {flight_info['destination']}"

    y_flight_no = y_airline + 70
    draw.text((20, y_flight_no), flight_no, font=font_very_small, fill=0)

    y_from = y_flight_no + 40
    draw.text((20, y_from), from_text, font=font_very_small, fill=0)

    y_to = y_from + 40
    draw.text((20, y_to), to_text, font=font_very_small, fill=0)

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

    try:
        logging.info("start")
        epd = epd7in5_V2.EPD()

        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        last_flight_number = None
        curr_temp = ""
        last_time = ""
        flight = 1

        # add error handling!!
        while True:
            flight_info = get_curr_flight_info(bounds)
            current_time = time.strftime("%H:%M")

            # No flight passing, therefore display time and temperature
            if not flight_info:
                # only update once per minute
                if current_time == last_time and not flight: continue
                last_time = current_time

                # get new temperature
                temp_info = get_weather()
                if temp_info: curr_temp = temp_info
                display_time(epd, current_time, time.strftime("%d. %B %Y"), curr_temp)
                flight = 0

            elif flight_info['number'] != last_flight_number:
                if (flight_info['speed'] > 300): continue
                display_flight_info(epd, flight_info, current_time)
                last_flight_number = flight_info['number']
                flight = 1
            time.sleep(5)


    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd7in5_V2.epdconfig.module_exit(cleanup=True)
        exit()


if __name__ == "__main__":
    main()
        