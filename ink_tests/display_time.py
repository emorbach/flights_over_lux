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
    font_time = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 250)
    font_date = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 50)


    logging.info("read waveshare file") # and hopefully display
    Himage = Image.open(os.path.join(picdir, '7in5_V2.bmp'))
    epd.display(epd.getbuffer(Himage))
    time.sleep(5)


    for i in range (10):
        logging.info("Drawing time and weather")
        epd.init_fast()
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)

        # current date and time
        current_time = time.strftime("%H:%M")
        current_date = time.strftime("%d. %B %Y") # e.g. 25. August 2025
        temperature = "+20°C" # to be replaced by actual temperature

        # --- Center the time ---
        w_time, h_time = draw.textsize(current_time, font=font_time)
        logging.info(f"Time size: {w_time}x{h_time}")
        x_time = (epd.width - w_time) // 2
        y_time = (epd.height // 2) - ((h_time+50) // 2)  # slightly above center
        draw.text((x_time, y_time), current_time, font=font_time, fill=0)

        # --- Center the date below the time ---
        # x_date = (epd.width - w_date) // 2
        # --- Put the date below the time ---
        w_date, h_date = draw.textsize(current_date, font=font_date)
        x_date = x_time  # align left with time
        y_date = y_time + h_time + 10  # small gap below time
        draw.text((x_date, y_date), current_date, font=font_date, fill=0)

        # --- Temperature in lower-right corner of time ---
        w_temp, h_temp = draw.textsize(temperature, font=font_date)
        x_temp = x_time + w_time - w_temp  # theoretisch aligned links
        y_temp = y_time + h_time + 10  # small gap below time
        draw.text((x_temp, y_temp), temperature, font=font_date, fill=0)

        # Send to e-paper
        epd.display(epd.getbuffer(Himage))

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
