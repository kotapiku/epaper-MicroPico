from EPD_7in5_B import EPD_7in5_B
import machine
import network
import time
import ntptime
import urequests
from secret import SSID, PASSWORD, OWM_API_KEY, BATH_MEMBERS, LAT, LON, trash_map

##
## wlan and time
##


class Wlan:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)

    def connect(
        self, ssid: str = SSID, password: str = PASSWORD, host: str = "ntp.nict.jp"
    ):
        self.wlan.connect(ssid, password)
        cnt = 0
        while not self.wlan.isconnected():
            print("Waiting for connection...")
            time.sleep(1)
            cnt += 1
            if cnt > 60:
                raise RuntimeError("Failed to connect wifi")
        print("Network connected:", self.wlan.isconnected())
        print("IP address:", self.wlan.ifconfig())

        ntptime.host = host

        for _ in range(0, 10):
            try:
                print("settime")
                ntptime.settime()
            except OSError as e:
                if e.errno == 110:  # when ETIMEDOUT
                    continue
                else:
                    raise
            break

    def disconnect(self):
        self.wlan.active(False)
        self.wlan.deinit()
        print("Network connected:", self.wlan.isconnected())

    def isconnected(self):
        return self.wlan.isconnected()


weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def local_date_time_getter(offset_min: int = 9 * 60) -> dict:
    (year, month, day, hour, min, sec, weekday_num, yearday) = time.localtime(
        time.time() + offset_min * 60
    )
    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "min": min,
        "sec": sec,
        "weekday_num": weekday_num,
        "weekday": weekdays[weekday_num],
        "yearday": yearday,
    }


def draw_date_and_time(epd: EPD_7in5_B):
    time_info = local_date_time_getter()

    date_string = (
        "{year}-{month:02d}-{day:02d} ({weekday}) {hour:02d}:{min:02d}".format(
            **time_info
        )
    )
    print("succeeded to get date and time: ", date_string)

    epd.imageblack.large_text(date_string, 20, 10, 4, 0x00)  # s, x, y, m, c


##
## weather
##


class OpenWeatherMap:
    def __init__(self, city, units="metric", lang="en"):
        self.city = city
        self.units = units
        self.lang = lang
        self.lat = LAT
        self.lon = LON

    def get_current_weather(self):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={OWM_API_KEY}&units={self.units}&lang={self.lang}"

        res = urequests.post(url).json()
        print("succeeded to get weather data")

        return res

    def get_3hour_forecast_data(self, cnt=3):
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&units={self.units}&cnt={cnt}&appid={OWM_API_KEY}"

        res = urequests.post(url).json()
        print("succeeded to get 3hour forecast data")

        return res


def draw_icon(name: str, epd: EPD_7in5_B, x: int, y: int, m: int = 1):
    print(f"draw icon: images/{name}")
    with open(f"images/{name}", "r") as f:
        icon_rows = f.read().split()
        icon = [list(_) for _ in icon_rows]
        for i in range(len(icon)):
            for j in range(len(icon[0])):
                if icon[i][j] == "1":
                    if m == 1:
                        epd.imageblack.pixel(x + j, y + i, 0x00)
                    else:
                        epd.imageblack.fill_rect(x + j * m, y + i * m, m, m, 0x00)
                elif icon[i][j] == "2":
                    if m == 1:
                        epd.imagered.pixel(x + j, y + i, 0xFF)
                    else:
                        epd.imagered.fill_rect(x + j * m, y + i * m, m, m, 0xFF)


# wh = 16 or 32
def translate_weather_icon(icon: str, wh: int) -> str:
    icon_map = {
        "01d": "sun",
        "01n": "moon",
        "02d": "cloud_sun",
        "02n": "cloud_moon",
        "03d": "cloud",
        "03n": "cloud",
        "04d": "clouds",
        "04n": "clouds",
        "09d": "rain0",
        "09n": "rain0",
        "10d": "rain1_sun",
        "10n": "rain1_moon",
        "11d": "lightning",
        "11n": "lightning",
        "13d": "snow",
        "13n": "snow",
        "50d": "mist",
        "50n": "mist",
    }
    return f"{icon_map[icon]}_{wh}_{wh}.txt"


def draw_weather(epd: EPD_7in5_B, owm: OpenWeatherMap):
    weather_data = owm.get_current_weather()
    temp_min = weather_data.get("main").get("temp_min")
    temp_max = weather_data.get("main").get("temp_max")
    temp = weather_data.get("main").get("temp")
    weather_icon = weather_data.get("weather")[0].get("icon")  # e.g. 02n

    draw_icon(translate_weather_icon(weather_icon, 32), epd, 15, 70, 2)

    current_weather_string = f"{temp:.1f}"

    epd.imageblack.large_text(current_weather_string, 90, 85, 4, 0x00)
    draw_icon("degree_32_32.txt", epd, 90 + 32 * 4, 85, 2)
    epd.imageblack.large_text(f"H:{temp_max:.1f}  L:{temp_min:.1f}", 20, 149, 2, 0x00)
    draw_icon("degree_32_32.txt", epd, 20 + 16 * 6, 149)
    draw_icon("degree_32_32.txt", epd, 20 + 16 * 14, 149)


# "2022-03-15 16:00:00" |-> "01" (UTC+9)
def format_dt_txt(dt_txt: str) -> str:
    hour = dt_txt.split(" ")[1].split(":")[0]
    return "{:02d}".format((int(hour) + 9) % 24)


def draw_3hour_forecast_weather(epd: EPD_7in5_B, owm: OpenWeatherMap):
    forecast_data = owm.get_3hour_forecast_data()

    print("draw forecasts")
    for i, res in enumerate(forecast_data.get("list")):
        x = i * 250
        if i != 0:
            epd.imageblack.vline(x, 195, 64, 0x00)  # x, y, h, c

        temp = res.get("main").get("temp")
        when = format_dt_txt(res.get("dt_txt"))
        weather_icon = res.get("weather")[0].get("icon")  # e.g. 02n

        draw_icon(translate_weather_icon(weather_icon, 32), epd, x + 50, 200, 2)
        epd.imageblack.large_text(when, x + 122, 205, 2, 0x00)
        weather_temp_string = f"{temp:.1f}"
        epd.imageblack.large_text(weather_temp_string, x + 122, 229, 2, 0x00)
        draw_icon("degree_16_16.txt", epd, x + 122 + 16 * 4, 229, 2)


##
## bath
##


def who_in_charge() -> str:
    local_time = time.localtime(time.time() + 9 * 60 * 60)
    hour = local_time[3]
    seconds_from_2000 = time.mktime(local_time)
    day_num = seconds_from_2000 // (24 * 60 * 60)  # day numbers from 2000-1-1
    idx = (day_num - (1 if hour < 4 else 0)) % len(BATH_MEMBERS)
    return BATH_MEMBERS[idx]


def draw_bath_in_charge(epd: EPD_7in5_B):
    print("draw who is in charge of boiling bath")
    person_string = who_in_charge()
    epd.imageblack.large_text(f"Bath  {person_string}", 20, 280, 3, 0x00)


def draw_trash(epd: EPD_7in5_B):
    time_info = local_date_time_getter()
    if time_info["hour"] > 8:
        time_info = local_date_time_getter(60 * 24)
    trash = trash_map(
        time_info["day"],
        time_info["weekday_num"],
    )
    if trash:
        epd.imageblack.large_text(f"Trash {trash}", 20, 325, 3, 0x00)


epd = EPD_7in5_B()
epd.Clear()

machine.Pin(23, machine.Pin.OUT).high()
wlan = Wlan()
wlan.connect()

owm = OpenWeatherMap("Tokyo")


epd.imageblack.fill(0xFF)
epd.imagered.fill(0x00)

print("---draw date and time---")
draw_date_and_time(epd)
print("---draw weather---")
draw_weather(epd, owm)
print("---draw 3hour forecast weather---")
draw_3hour_forecast_weather(epd, owm)
print("---draw bath in charge---")
draw_bath_in_charge(epd)
print("---draw trash day---")
draw_trash(epd)

print("---display---")
epd.display()
epd.delay_ms(5000)

SLEEP_MINUTES = 60 - local_date_time_getter()["min"]

print("---sleep---")
wlan.disconnect()
machine.Pin(23, machine.Pin.OUT).low()
machine.deepsleep(SLEEP_MINUTES * 60 * 1000)
