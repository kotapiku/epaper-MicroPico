from EPD_7in5_B import EPD_7in5_B
import machine
import network
import time
import ntptime
import urequests
from secret import SSID, PASSWORD, OWM_API_KEY, PERSON0, PERSON1

##
## wlan and time
##


def connect_wlan_and_settime(ssid: str, password: str, host: str = "ntp.nict.jp"):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    cnt = 0
    while not wlan.isconnected():
        print("Waiting for connection...")
        time.sleep(1)
        cnt += 1
        if cnt > 60:
            raise RuntimeError("Failed to connect wifi")

    print("Network connected:", wlan.isconnected())
    print("IP address:", wlan.ifconfig())

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


def disconnect_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.deinit()
    print("Network connected:", wlan.isconnected())


def local_date_time_getter(offset_min: int = 9 * 60) -> time.struct_time:
    return time.localtime(time.time() + offset_min * 60)


def draw_date_and_time(epd: EPD_7in5_B):
    (year, month, day, hour, min, _, weekday_num, _) = local_date_time_getter()

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    date_string = (
        f"{year}-{month:02d}-{day:02d} ({weekdays[weekday_num]}) {hour:02d}:{min:02d}"
    )
    print("succeeded to get date and time: ", date_string)

    epd.imageblack.large_text(date_string, 5, 10, 4, 0x00)  # s, x, y, m, c


##
## weather
##


class OpenWeatherMap:
    def __init__(self, city, units="metric", lang="en"):
        self.city = city
        self.units = units
        self.lang = lang

        # set latitude and longitude
        try:
            url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&appid={OWM_API_KEY}"
            print("request: ", url)
            res = urequests.post(url).json()  # TODO: 405 error occur
            print("geo info: ", res)

            self.lat = res[0].get("lat")
            self.lon = res[0].get("lon")
        except:
            self.lat = 35.6828387  # Tokyo
            self.lon = 139.7594549
        print("lat: ", self.lat, "lon: ", self.lon)

    def get_current_weather(self):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={OWM_API_KEY}&units={self.units}&lang={self.lang}"

        res = urequests.post(url).json()
        print("succeeded to get weather data")

        return res

    def get_3hour_forecast_data(self, cnt=5):
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&units={self.units}&cnt={cnt}&appid={OWM_API_KEY}"

        res = urequests.post(url).json()
        print("succeeded to get 3hour forecast data")

        return res


celsius = "\u00b0" + "C"


def draw_icon(name: str, epd: EPD_7in5_B, x: int, y: int, wh: int):
    print(f"draw icon: images/{translate_weather_icon(name, wh)}")
    with open(f"images/{translate_weather_icon(name, wh)}", "r") as f:
        icon_rows = f.read().split()
        icon = [list(_) for _ in icon_rows]
        for i in range(len(icon)):
            for j in range(wh):
                if icon[i][j] == "1":
                    epd.imageblack.pixel(x + j, y + i, 0x00)
                elif icon[i][j] == "2":
                    epd.imagered.pixel(x + j, y + i, 0xFF)


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
    feels_like = weather_data.get("main").get("feels_like")
    weather_icon = weather_data.get("weather")[0].get("icon")  # e.g. 02n

    draw_icon(weather_icon, epd, 15, 70, 32)

    current_weather_string = (
        f"{temp:.1f}{celsius} (feels like {feels_like:.1f}{celsius})"
    )
    temp_min_max_string = f"H:{temp_max:.1f}{celsius}  L:{temp_min:.1f}{celsius}"

    epd.imageblack.large_text(current_weather_string, 50, 80, 2, 0x00)
    epd.imageblack.large_text(temp_min_max_string, 20, 117, 2, 0x00)


# "2022-03-15 16:00:00" |-> "01" (UTC+9)
def format_dt_txt(dt_txt: str) -> str:
    hour = dt_txt.split(" ")[1].split(":")[0]
    return "{:02d}".format((int(hour) + 9) % 24)


def draw_3hour_forecast_weather(epd: EPD_7in5_B, owm: OpenWeatherMap):
    forecast_data = owm.get_3hour_forecast_data()

    print("draw forecasts")
    for i, res in enumerate(forecast_data.get("list")):
        x = i * 150
        if i != 0:
            epd.imageblack.vline(x, 154, 32, 0x00)  # x, y, h, c

        temp = res.get("main").get("temp")
        when = format_dt_txt(res.get("dt_txt"))
        weather_icon = res.get("weather")[0].get("icon")  # e.g. 02n

        epd.imageblack.large_text(when, x + 70, 154, 1, 0x00)

        draw_icon(weather_icon, epd, x + 30, 154, 32)
        weather_temp_string = f"{temp:.1f}{celsius}"
        epd.imageblack.large_text(weather_temp_string, x + 70, 170, 1, 0x00)


class BathInCharge:
    def __init__(self):
        self.date = local_date_time_getter()[2]
        self.person = 0

    def who_in_charge(self) -> int:
        date, hour = local_date_time_getter()[2:4]
        if date != self.date and hour > 4:
            self.person = (self.person + 1) % 2
            self.date = date
        return self.person


##
## bath
##


def draw_bath_in_charge(epd: EPD_7in5_B, bic: BathInCharge):
    print("draw who is in charge of boiling bath")
    person_string = [PERSON0, PERSON1][bic.who_in_charge()]
    epd.imageblack.large_text(f"bath: {person_string}", 15, 200, 2, 0x00)


if __name__ == "__main__":
    epd = EPD_7in5_B()
    epd.Clear()

    connect_wlan_and_settime(SSID, PASSWORD)

    owm = OpenWeatherMap("Tokyo")
    bic = BathInCharge()

    try:
        SLEEP_MINUTES = 60
        while True:
            epd.imageblack.fill(0xFF)
            epd.imagered.fill(0x00)

            print("---draw date and time---")
            draw_date_and_time(epd)
            print("---draw weather---")
            draw_weather(epd, owm)
            print("---draw 3hour forecast weather---")
            draw_3hour_forecast_weather(epd, owm)
            print("---draw bath in charge---")
            draw_bath_in_charge(epd, bic)

            print("---display---")
            epd.display()
            epd.delay_ms(5000)

            print("---sleep---")
            disconnect_wlan()
            epd.sleep()
            time.sleep(SLEEP_MINUTES * 60)

            print("---wakeup---")
            epd.init()
            connect_wlan_and_settime(SSID, PASSWORD)

    except:
        print("sleep and reset")
        epd.sleep()
        machine.reset()  # to avoid memory allocation error
