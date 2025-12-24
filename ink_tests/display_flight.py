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

# Display the flight number with the flight big and the destination and origin airports

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
        bmp = Image.open(os.path.join(picdir, 'a320.bmp'))
        Himage.paste(bmp, (15, 0))
        draw = ImageDraw.Draw(Himage)

        # --- Current time (top-right corner) ---
        current_time = time.strftime("%H:%M")
        w_time, h_time = draw.textsize(current_time, font=font_time)
        x_time = epd.width - w_time -10
        y_time = 10
        draw.text((x_time, y_time), current_time, font=font_time, fill=0)

        # --- Flight number (big, center-right) ---
        flight_number = "FR1458"  
        w_flight, h_flight = draw.textsize(flight_number, font=font_no)
        x_flight = (epd.width // 2) - 150
        y_flight = 80
        draw.text((x_flight, y_flight), flight_number, font=font_no, fill=0)

        # --- Airline name (below flight number) ---
        airline = "Ryanair"
        w_airline, h_airline = draw.textsize(airline, font=font35)
        x_airline = x_flight
        y_airline = y_flight + h_flight + 10
        draw.text((x_airline, y_airline), airline, font=font35, fill=0)

        # --- From / To ---
        from_text = "From:  Luxembourg Findel Airport (LUX)"
        to_text   = "To:      London Stansted Airport (STN)"

        y_from = y_airline + h_airline + 50
        draw.text((40, y_from), from_text, font=font35, fill=0)

        y_to = y_from + 50
        draw.text((40, y_to), to_text, font=font35, fill=0)

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
