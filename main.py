from EPD_7in5_B import EPD_7in5_B
import machine
import network
import time
import ntptime
from secret import SSID, PASSWORD

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
    print("{year}-{month}-{day} {hour}:{min}".format(year=year, month=month, day=day, hour=hour, min=min))
    epd.imageblack.large_text("{year}-{month}-{day} {hour}:{min}".format(year=year, month=month, day=day, hour=hour, min=min), 5, 10, 3, 0x00)
    epd.display()
    epd.delay_ms(5000)

if __name__ == '__main__':
    epd = EPD_7in5_B()
    epd.Clear()

    epd.imageblack.fill(0xff)
    epd.imagered.fill(0x00)

    draw_date_and_time(epd)
    print("sleep")
    epd.sleep()
    machine.reset() # to avoid memory allocation error