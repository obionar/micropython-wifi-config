# ESP32 Easy WiFi Config

**ESP32 Easy WiFi Config** is a MicroPython project designed to simplify the process of connecting your ESP32 board to a WiFi network. This project enables a web-based interface that allows users to scan for available WiFi networks, enter credentials, and store them on the device. The configuration mode can be triggered using a GPIO pin, making it easy to switch between normal operation and configuration mode.

## Features

- **Configuration Mode**: Trigger configuration mode via a GPIO pin.
- **Network Scanning**: Scans and displays available WiFi networks.
- **Easy WiFi Configuration**: Simple web interface to select and connect to WiFi networks.
- **Secure Storage**: Stores WiFi credentials in a JSON file on the device.
- **Automatic Connection**: Attempts to connect to the stored WiFi network on boot.
- **Fallback to Configuration Mode**: If connection fails, automatically starts the web interface for reconfiguration.

## Usage

1. **Configuration Mode**: On device boot, if the defined GPIO pin is high, the device enters configuration mode, starting a web server.
2. **Web Interface**: Connect to the device's access point (ESP32_Config) and open a web browser to the device's IP 192.168.4.1 to access the configuration page.
3. **Network Selection**: Select a WiFi network from the list, enter the password, and save the configuration.
4. **Connection**: The device will attempt to connect to the selected network. If successful, it will run the main application code; otherwise, it will re-enter configuration mode.

