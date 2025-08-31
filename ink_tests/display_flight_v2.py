#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2.EPD()
    
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
    font35 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    font100 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 100)
    font_time = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 35)
    font_no = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 150)
    font_airports = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 80)

    '''
    logging.info("read waveshare file") # and hopefully display
    Himage = Image.open(os.path.join(picdir, '7in5_V2.bmp'))
    epd.display(epd.getbuffer(Himage))
    time.sleep(5)
    '''

    for i in range (10):
        logging.info("Drawing airplane and info")
        epd.init_fast()
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        bmp = Image.open(os.path.join(picdir, 'boeing747.bmp'))
        bmpheight = (256-bmp.height) // 2 
        Himage.paste(bmp, (10, 20))
        draw = ImageDraw.Draw(Himage)

        # --- Current time (top-right corner) ---
        current_time = time.strftime("%H:%M")
        w_time, h_time = draw.textsize(current_time, font=font_time)
        x_time = epd.width - w_time - 10
        y_time = 10
        draw.text((x_time, y_time), current_time, font=font_time, fill=0)


        # --- Origin, Destination, Airline, Aircraft ---
        origin, destination = "Origin: ", "Dest:"
        flight_origin, flight_destination = "LUX", "STN"
        airline, aircraft = "Ryanair", "Airbus A320"

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
        w_airline, _ = draw.textsize(airline, font=font35)
        w_airport, _ = draw.textsize(flight_origin, font=font_airports)

        x_airline = x_origin + w_origin + 10 + w_airport - w_airline
        y_airline = y_origin + h_origin * 2 + line_gap
        draw.text((x_airline, y_airline), airline, font=font35, fill=0)
        draw.text((20, y_airline), aircraft, font=font35, fill=0)


        # Send to e-paper
        epd.display(epd.getbuffer(Himage))
        epd.sleep()

        # Update once per minute
        time.sleep(60)





    logging.info("Clear...")
    epd.init()
    epd.Clear()

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit(cleanup=True)
    exit()
