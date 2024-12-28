from functions import read_configuration
from wifi import wifi_setup, connect_wlan


if __name__ == '__main__':
    config = read_configuration()

    if len(config) == 0:
        wifi_setup()

    wlan_status = connect_wlan(config)

    if not wlan_status:
        wifi_setup()
