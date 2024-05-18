# from machine import Pin
import machine
import time

led = machine.Pin("LED", machine.Pin.OUT)

led.on()
time.sleep(1)
led.off()
machine.Pin(23, machine.Pin.OUT).low()
machine.deepsleep(5 * 1000)
