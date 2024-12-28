from machine import Pin

import time


def write_configuration(ssid: str, password: str) -> None:
    """Write wifi configuration to file"""
    with open('config.txt', 'w', encoding='utf-8') as file:
        file.write(f'SSID={ssid}\nPassword={password}\n')


def read_configuration() -> dict:
    """Reads and returns the wifi configuration, if it exists"""
    try:
        with open('config.txt', 'r', encoding='utf-8') as file:
            config = file.readlines()

        config = [c.split('=')[1].strip() for c in config]

        return {
            'ssid': config[0],
            'password': config[1]
        }

    except OSError:
        print("Wifi configuration file not found")
        return {}


def blink(frequency: float = 0.5, duration: int = 10) -> None:
    led = Pin('LED', Pin.OUT)
    end = -1

    if duration != 0:
        end = time.time() + duration

    while True:
        led.toggle()
        time.sleep(frequency)

        if time.time() > end and end != -1:
            led.off()
            break
