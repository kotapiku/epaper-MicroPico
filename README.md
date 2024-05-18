# Raspberry Pi Pico + e-paper

This project is a library for displaying date, weather, bath cleaning duty, and trash collection days using a Raspberry Pi Pico and a Waveshare 7.5-inch ePaper (black, white, red) display.

## Features

- Display date and weather
- Display bath cleaning duty
- Display trash collection days
- Update the screen every hour

## Weather Icons

The weather icons in `images/*_16_16.txt` (except for `images/mist_16_16.txt`) are created using `images/icon.py` and [Dhole/weather-pixel-icons](https://github.com/Dhole/weather-pixel-icons) with some color changes.

## Tested Environment

- MicroPython v1.22.2

## Preparation

Create a file named `secret.py` and fill in the following information:

- WiFi SSID and password (`SSID`, `PASSWORD`)
- OpenWeatherMap API key (`OWM_API_KEY`), latitude (`LAT`), longitude (`LON`)
- Names for bath cleaning duty members (`BATH_MEMBERS`)
- A function to display trash collection days (`trash_map`)

Example of `secret.py`:

```python:secret.py
SSID = "ssid"
PASSWORD = "password"
OWM_API_KEY = "API key"
LAT = 35.6828387  # Tokyo
LON = 139.7594549
BATH_MEMBERS = ["person 1", "person 2"]

# Function to return trash type based on the day of the week
def trash_map(day: int, weekday_num: int) -> str:
    if weekday_num == 3:  # Thursday
        if (day - 1) // 7 == 1 or (day - 1) // 7 == 3:
            return "Non-Burnable"
    elif weekday_num == 2 or weekday_num == 5:  # Tuesday, Friday
        return "Burnable"
    elif weekday_num == 4:  # Wednesday
        return "Recyclable"
    return ""

```

## License

![CC](https://licensebuttons.net/l/by-sa/3.0/88x31.png)

**[Creative Commons Attribution-ShareAlike](https://creativecommons.org/licenses/by-sa/4.0/)**

**CC BY-SA**
