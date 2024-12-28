from functions import write_configuration, blink

from time import sleep, time
from machine import Pin

import rp2
import network
import time
import socket
import ubinascii


def get_mac() -> str:
    """Returns the MAC address of the Pico"""
    mac = ''
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    ap.active(False)
    return mac


def web_page() -> str:
    """Return the HTML content for the form page."""
    return """\
<!DOCTYPE html>
<html>
<head>
    <title>WiFi Config</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            background-color: #f9f9f9;
        }
        h1 {
            color: #333;
        }
        form {
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 400px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 16px;
        }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        input[type="submit"]:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>WiFi Configuration</h1>
    <form action="/" method="post">
        <label for="ssid">SSID:</label>
        <input type="text" id="ssid" name="ssid" placeholder="Enter SSID">
        <label for="password">Password:</label>
        <input type="password" id="password" name="password" placeholder="Enter Password">
        <input type="submit" value="Save">
    </form>
</body>
</html>
"""


def start_server() -> None:
    """Start the web server"""
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print("Listening on", addr)

    while True:
        cl, addr = s.accept()
        print("Client connected from", addr)
        try:
            request = cl.recv(1024).decode("utf-8")
            print("Request:", request)

            # Check if the request is a POST
            if "POST / " in request:
                content_length = int(request.split(
                    "Content-Length: ")[1].split("\r\n")[0])
                body = request.split("\r\n\r\n")[1][:content_length]
                print("Body:", body)

                # Parse form data
                params = {kv.split("=")[0]: kv.split("=")[1]
                          for kv in body.split("&")}
                ssid = params.get("ssid", "").replace("+", " ")
                password = params.get("password", "").replace("+", " ")

                # Save to config.txt
                write_configuration(ssid, password)

                # Send response
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
                response += "<h1>Configuration Saved!</h1>"
                cl.send(response)

                print("Shutting down server..")
                cl.close()
                s.close()
                break
            else:
                # Serve the form page
                response = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n"
                response += web_page()
                cl.send(response)
        except Exception as e:
            print("Error:", e)
        finally:
            cl.close()


def wifi_setup() -> None:
    """Used to setup the Pico for wifi"""
    mac = get_mac().replace(':', '')
    ssid = f'PiHAN-{mac}'
    password = 'password'

    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while ap.active() == False:
        pass

    print('AP Mode Is Active, You can Now Connect')
    print('IP Address To Connect to:: ' + ap.ifconfig()[0])

    start_server()


def connect_wlan(config: dict) -> str:
    """Attempt wlan connection"""
    led = Pin('LED', Pin.OUT)
    timeout = time.time() + 30
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config['ssid'], config['password'])

    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1:
            wlan.active(False)
            return ''

        print('Waiting for connection...')
        led.on()
        sleep(0.5)
        led.off()
        sleep(0.5)

        if time.time() > timeout:
            blink(frequency=0.1, duration=1)
            return ''

    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')

    return ip
