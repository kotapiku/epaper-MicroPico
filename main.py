from EPD_7in5_B import EPD_7in5_B
import machine
import network
import time
import ntptime
import urequests
from secret import SSID, PASSWORD, OWM_API_KEY

def local_date_time_getter(ssid: str, password: str,
                            host: str = "ntp.nict.jp",
                            offset_min: int = 9 * 60) -> time.struct_time:
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
    return time.localtime(time.time() + offset_min * 60)

def draw_date_and_time(epd: EPD_7in5_B):
    (year, month, day, hour, min, sec, weekday_num,
         _) = local_date_time_getter(SSID, PASSWORD)

    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    date_string = "{year}-{month:02d}-{day:02d} ({weekday}) {hour:02d}:{min:02d}".format(year=year, month=month, day=day, hour=hour, min=min, weekday=weekdays[weekday_num])
    print("succeeded to get date and time: ", date_string)

    epd.imageblack.large_text(date_string, 5, 10, 4, 0x00) # s, x, y, m, c
    epd.display()
    epd.delay_ms(5000)

class OpenWeatherMap:
    def __init__(self, city, units='metric', lang='en'):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units={units}&lang={lang}"
        print("request post: ", url)
        res = urequests.post(url)
        self.current_json = res.json()
        print("succeeded to get weather data: ", self.current_json)
    # def get_icon_data(self):
    #     icon_id = self.current_json['weather'][0]['icon']
    #     url = 'http://openweathermap.org/img/wn/{icon}.png'.format(icon=icon_id)
    #     response = urequests.get(url, stream=True)
    #     return base64.encodebytes(response.raw.read())

def draw_weather(epd: EPD_7in5_B):
    epd.imageblack.vline(10, 80, 300, 0x00) # x, y, h, c

    owm = OpenWeatherMap('Tokyo')
    weather_data = owm.current_json

    temp_min = weather_data.get('main').get('temp_min')
    temp_max = weather_data.get('main').get('temp_max')
    temp = weather_data.get('main').get('temp')
    feels_like = weather_data.get('main').get('feels_like')
    weather = weather_data.get('weather')[0].get('main') # Rain, ...

    celsius = u"\u00b0" + "C"
    current_weather_string = "{weather} {temp}{degree}C (feels like {feels_like} {degree}C)".format(weather=weather, temp=temp, feels_like=feels_like, degree=chr(176))
    temp_min_max_string = "{0}{2} / {1}{2}".format(temp_min, temp_max, celsius)

    epd.imageblack.large_text(current_weather_string, 15, 80, 2, 0x00)
    epd.imageblack.large_text(temp_min_max_string, 15, 117, 2, 0x00)

    epd.display()
    epd.delay_ms(5000)

if __name__ == '__main__':
    epd = EPD_7in5_B()
    epd.Clear()

    epd.imageblack.fill(0xff)
    epd.imagered.fill(0x00)

    draw_date_and_time(epd)
    draw_weather(epd)

    print("sleep")
    epd.sleep()
    machine.reset() # to avoid memory allocation error