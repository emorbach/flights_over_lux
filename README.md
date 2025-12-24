# Tracker for Passing Flights

The file `e-paper_flights.py` runs on the Raspberry Pi when it is connected to the e-paper display. It shows time and date, as well as temperataure. When a flight is passing, it shows information about that flight.


## Raspberry Pi

To connect for the first time, you need either a micro HDMI or use a LAN cable to connect to the Wi-Fi. It should be connected to my Hotspot (Girlscamp4) as well as the Fritz Box in Cents. By opening `raspi-config` you can add the WLAN data.

### Configuration

At reboot the program starts after 30 seconds of sleeping. This is done with `crontab`. You can edit the file with `crontab -e` and just read its contents with `crontab -l`

### Important Commands

Reading out temperature:
> `vcgencmd measure_temp`

Track log file contents:
> `tail -f /home/pi/flugi_lux/flight_tracker.log`

Check which processes are running:
> `ps aux | grep e-paper_flights.py`
> `pgrep -fl python3`

Kill a running process with SIGINT which triggers my Keyboard Interrupt and cleanly closes the program (clear the e-paper, ...):
> `kill -2 <PID>`

Without the `-2`, a SIGTERM is sent, which directly terminates the program.

Reboot the Raspi to start the program again:
> `sudo reboot`


## Code



## Errors
ERROR:root:Error fetching flight data: HTTPSConnectionPool(host='data-cloud.flightradar24.com', port=443): Max retries exceeded with url: /zones/fcgi/feed.js?faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=1&air=1&vehicles=1&estimated=1&maxage=14400&gliders=1&stats=1&limit=5000&bounds=49.634583111433045%2C49.598610250237165%2C6.1322490860080885%2C6.187771405847902 (Caused by NewConnectionError('<urllib3.connection.VerifiedHTTPSConnection object at 0xaff2f1b0>: Failed to establish a new connection: [Errno -3] Temporary failure in name resolution'))


## To-Do

- [x] Fix aircraft pictures
- [x] Figure out how to turn off during night? Possibly with crontab
- [x] Add support for private planes?
- [x] Find clean way to stop program
- [x] Add more airports (important for Cargolux)
- [x] Make font bigger
- [ ] Add temperature warning?
- [ ] Fix HTTPSConnectionPool Error
- [ ] Show correct airplane name
