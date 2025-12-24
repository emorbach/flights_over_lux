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





## To-Do

- [x] Fix aircraft pictures
- [x] Figure out how to turn off during night? Possibly with crontab
- [ ] Add temperature warning?
- [ ] Add support for private planes?
- [x] Find clean way to stop program
- [x] Add more airports (important for Cargolux)
- [ ] Make font bigger
- [ ] Fix HTTPSConnectionPool Error
- [ ] Show correct airplane name
