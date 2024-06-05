import time
import network
import ujson
from machine import Pin, ADC
import usocket as socket

# GPIO pin to enter configuration mode
config_pin = Pin(0, Pin.IN)

# Initialize WiFi in access point and station modes
ap = network.WLAN(network.AP_IF)
sta = network.WLAN(network.STA_IF)
sta.active(True)

web_enabled = False

# Read WiFi credentials from JSON file
def json_read():
    global essid, key 
    try:
        with open('wifi.json', 'r') as f:
            s = ujson.load(f)
            essid = s['essid']
            key = s['key']
    except Exception as e:
        essid = ''
        key = ''
        print('Failed to read JSON:', e)

# Write WiFi credentials to JSON file
def json_write(essid, key):
    try:
        with open('wifi.json', 'w') as wf:
            ujson.dump({'essid': essid, 'key': key}, wf)
    except Exception as e:
        print('Failed to write JSON:', e)

# Attempt to connect to WiFi using saved credentials
def do_connect():
    json_read()
    if essid and key:
        sta.connect(essid, key)
        timeout = 10
        while not sta.isconnected() and timeout > 0:
            print('Connecting...')
            time.sleep(1)
            timeout -= 1
        if sta.isconnected():
            print('Connected to:', essid)
        else:
            print('Connection failed!')
    else:
        print('No WiFi credentials found!')

# Scan for available WiFi networks
def wifi_scan():
    sta.active(True)
    wifi_list = []
    for i in sta.scan():
        scan_essid = str(i[0], 'utf-8')
        signal = i[3]
        wifi_list.append([scan_essid, signal])
    return wifi_list

# Start the web server for WiFi configuration
def start_web_server():
    global web_enabled
    ap.active(True)
    ap.config(essid='ESP32_Config')
    ap.config(authmode=0)
    print(ap.ifconfig())

    print('Starting web server')

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.bind(('', 80))
    my_socket.listen(1)

    while web_enabled:
        connection, address = my_socket.accept()
        request = connection.recv(1024).decode('utf-8')
        get_req = request.split(' ')[1]

        html = generate_html(get_req)
        
        response = 'HTTP/1.1 200 OK\n'
        response += 'Content-Type: text/html\n'
        response += 'Connection: close\n\n'
        response += html

        connection.sendall(response.encode('utf-8'))
        connection.close()

# Generate HTML content based on the request
def generate_html(get_req):
    html = '''
        <a href="/">Status</a> |
        <a href="/wifi">WiFi Settings</a> |
    '''
    
    if get_req == '/':
        # Display device status
        if sta.isconnected():
            wifi_status = '{} ({} dB)'.format(essid, sta.status('rssi'))
        else:
            wifi_status = 'disconnected'
        html += '''
            <h2>Device status</h2>
            <table border="1">
                <tr>
                    <td>WiFi</td> <td>{}</td>
                </tr>
            </table>
        '''.format(wifi_status)

    elif get_req == '/wifi':
        # Display WiFi configuration form
        html += '<h2>Network Configuration</h2>'
        option_essid = ''.join(['<option value="{}">{} {} dB</option>'.format(i[0], i[0], i[1]) for i in wifi_scan()])
        html += '''
            <h3>Connect to WiFi:</h3>
            <form action="/connect">
                Select Network:<br>
                <select name="essid">
                    {}
                </select><br>
                Password:<br>
                <input type="password" name="key"><br>
                <input type="submit" value="Save & Connect"><br>
            </form>
        '''.format(option_essid)

    elif get_req.startswith("/connect"):
        # Handle WiFi connection form submission
        params = get_req.split('?')[1]
        new_essid = params.split('&')[0].split('=')[1]
        new_key = params.split('&')[1].split('=')[1]
        json_write(new_essid, new_key)
        do_connect()
        if sta.isconnected():
            html += "Connection Successful!"
        else:
            html += "Connection Failed!"

    elif get_req == "/disconnect":
        # Handle WiFi disconnection
        sta.disconnect()
        json_write('', '')
        html += "Disconnected and forgot network."

    return '''
        <html>
            <head>
                <title>ESP32 WiFi Config</title>
                <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
                <style>
                    .container { font: 1.2em Arial; max-width: 99%; margin: 1em auto; padding: 1em; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Device Configuration Page</h2>
                    ''' + html + '''
                </div>
            </body>
        </html>
    '''

# Start configuration mode (web server)
def start_config_mode():
    global web_enabled
    web_enabled = True
    start_web_server()

# Main function to determine operation mode
def main():
    if config_pin.value() == 1:
        # Enter configuration mode if GPIO pin is high
        start_config_mode()
    else:
        # Attempt to connect to WiFi using saved credentials
        json_read()
        if not sta.isconnected():
            do_connect()
        if not sta.isconnected():
            # Enter configuration mode if connection failed
            start_config_mode()
        else:
            # Main code execution after successful connection
            print("Running main code...")
            # Your main code here
            pass

# Run the main function
if __name__ == '__main__':
    main()
