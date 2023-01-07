from machine import Pin, PWM
from time import sleep
import machine
import time

class HCSR04:
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us):
        self.echo_timeout_us = echo_timeout_us
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)
        self.led = PWM(Pin(26), 5000)
        self.led.duty(0)

    def _send_pulse_and_wait(self):
        self.trigger.value(0)  # Stabilize the sensor
        time.sleep_us(5)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110:  # 110 = истекло время подключения
                raise OSError('ETIMEDOUT: Connection timed out')
            raise ex

    def distance_cm(self):
        pulse_time = self._send_pulse_and_wait()
        cms = (pulse_time / 2) / 29.1
        if cms < 10.0:  # если растояние меньше 10 см
            self.led.duty(1023)  # включаем лампочку
        else:  # иначе
            self.led.duty(0)
        return cms


esp32 = HCSR04(trigger_pin=13, echo_pin=12, echo_timeout_us=10000)

while True:
    distance = esp32.distance_cm()
    print('Distance:', distance, 'cm')
    sleep(1)
