from EPD_7in5_B import EPD_7in5_B
import machine
import network
import time
import ntptime
import urequests
from secret import SSID, PASSWORD, OWM_API_KEY

def connect_and_settime(ssid: str, password: str, host: str = "ntp.nict.jp"):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        print("Waiting for connection...")
        time.sleep(1)

    print("Network connected:", wlan.isconnected())
    print("IP address:", wlan.ifconfig())

    ntptime.host = host
    ntptime.settime()
    print("settime")

def local_date_time_getter(offset_min: int = 9 * 60) -> time.struct_time:
    return time.localtime(time.time() + offset_min * 60)

def draw_date_and_time(epd: EPD_7in5_B):
    (year, month, day, hour, min, _, weekday_num,
         _) = local_date_time_getter()

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    date_string = "{year}-{month:02d}-{day:02d} ({weekday}) {hour:02d}:{min:02d}".format(year=year, month=month, day=day, hour=hour, min=min, weekday=weekdays[weekday_num])
    print("succeeded to get date and time: ", date_string)

    epd.imageblack.large_text(date_string, 5, 10, 4, 0x00) # s, x, y, m, c

class OpenWeatherMap:
    def __init__(self, city, units='metric', lang='en'):
        self.city = city
        self.units = units
        self.lang = lang

        # set latitude and longitude
        try:
            url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&appid={OWM_API_KEY}"
            print("request: ", url)
            res = urequests.post(url).json() # TODO: 405 error occur
            print("geo info: ", res)

            self.lat = res[0].get('lat')
            self.lon = res[0].get('lon')
        except:
            self.lat = 35.6828387 # Tokyo
            self.lon = 139.7594549
        print("lat: ", self.lat, "lon: ", self.lon)

    def get_current_weather(self):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={OWM_API_KEY}&units={self.units}&lang={self.lang}"

        res = urequests.post(url).json()
        print("succeeded to get weather data: ", res)

        return res

    def get_3hour_forecast_data(self, cnt=5):
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&units={self.units}&cnt={cnt}&appid={OWM_API_KEY}"

        res = urequests.post(url).json()
        print("succeeded to get 3hour forecast data: ", res)

        return res
    # def get_icon_data(self):
    #     icon_id = self.current_json['weather'][0]['icon']
    #     url = 'http://openweathermap.org/img/wn/{icon}.png'.format(icon=icon_id)
    #     response = urequests.get(url, stream=True)
    #     return base64.encodebytes(response.raw.read())

celsius = u"\u00b0" + "C"

def draw_weather(epd: EPD_7in5_B, owm:OpenWeatherMap):
    weather_data = owm.get_current_weather()
    temp_min = weather_data.get('main').get('temp_min')
    temp_max = weather_data.get('main').get('temp_max')
    temp = weather_data.get('main').get('temp')
    feels_like = weather_data.get('main').get('feels_like')
    weather = weather_data.get('weather')[0].get('main') # Rain, ...


    current_weather_string = "{weather} {temp:.1f}{celsius} (feels like {feels_like:.1f}{celsius})".format(weather=weather, temp=temp, feels_like=feels_like, celsius=celsius)
    temp_min_max_string = "{0:.1f}{2} / {1:.1f}{2}".format(temp_min, temp_max, celsius)

    epd.imageblack.large_text(current_weather_string, 15, 80, 2, 0x00)
    epd.imageblack.large_text(temp_min_max_string, 15, 117, 2, 0x00)


# "2022-03-15 15:00:00" |-> "00:00" (UTC+9)
def format_dt_txt(dt_txt: str) -> str:
    hour, min = dt_txt.split(" ")[1].split(":")[:2]
    return "{:02d}:{}".format((int(hour)+9) % 24, min)

def draw_3hour_forecast_weather(epd: EPD_7in5_B, owm:OpenWeatherMap):
    forecast_data = owm.get_3hour_forecast_data()

    print("draw forecasts")
    for i, res in enumerate(forecast_data.get('list')):
        print("i: ", i, "res: ", res)
        x = 15+i*150
        if i != 0:
            epd.imageblack.vline(x-8, 154, 32, 0x00) # x, y, h, c

        temp = res.get('main').get('temp')
        weather = res.get('weather')[0].get('main')
        when = format_dt_txt(res.get('dt_txt'))
        print(temp, weather, when)

        epd.imageblack.large_text(when, x, 154, 1, 0x00)
        weather_temp_string = "{} {:.1f}{}".format(weather, temp, celsius)
        epd.imageblack.large_text(weather_temp_string, x, 170, 1, 0x00)


if __name__ == '__main__':
    epd = EPD_7in5_B()
    epd.Clear()

    # epd.imagered.fill(0x00)

    connect_and_settime(SSID, PASSWORD)

    owm = OpenWeatherMap('Tokyo')

    try:
        SLEEP_MINUTES = 30
        while True:
            epd.imageblack.fill(0xff)
            draw_date_and_time(epd)
            draw_weather(epd, owm)
            draw_3hour_forecast_weather(epd, owm)

            epd.display()

            time.sleep(SLEEP_MINUTES * 60)
    except:
        print("sleep")
        epd.sleep()
        machine.reset() # to avoid memory allocation error