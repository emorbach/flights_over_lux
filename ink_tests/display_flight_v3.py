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
font_airport = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 175)
font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 45)
# font_very_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)


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
    Himage.paste(bmp, (20, y_image))
    draw = ImageDraw.Draw(Himage)


    # --- Origin, Destination, Airline, Aircraft ---
    origin = "Origin:"
    airport = flight_info['origin_iata']
    if airport == "LUX":
        origin = "Destination:"
        airport = flight_info['destination_iata']
        
    airline = flight_info['airline']
    aircraft = flight_info['aircraft']

    x_origin, y_origin = 350, 10
    line_gap = 10  # spacing between lines

    # Draw "origin:" and iata airport label
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


def main():
    try:
        logging.info("start")
        epd = epd7in5_V2.EPD()

        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        
        flight_info = {"number": "LX1234",
                "origin": "Porto Francisco Sá Carneiro Airport",
                "origin_iata": "OPO",
                "destination": "Luxembourg Findel Airport",
                "destination_iata": "LUX",
                "airline": "Cargolux",
                "aircraft": "B74",}

        display_flight_info(epd, flight_info)

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
        