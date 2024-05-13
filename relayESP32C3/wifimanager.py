import network
import ujson as json
import socket
import ure
from time import sleep

# Configuration:
staData = "data/sta.data"  # file with STA wifi names and passwords
apiEndpoint = "data/api.endpoint"  # file with API endpoint url
logoBase64 = "data/logo.base64"  # file with logo on base64
apName = "re001b"  # default wifi AP name
apPassword = "re001b_pass"  # default wifi AP password
apAuthmode = 3  # set WPA2 encryption

# WLAN interfaces:
wlanSTA = network.WLAN(network.STA_IF)  # STA
wlanAP = network.WLAN(network.AP_IF)  # AP

# Global socket:
serverSocket = None  # Global socket variable


def send_file_chunks(client, filePath):
    try:
        with open(filePath, "rb") as file:
            while True:
                print("Reading 1024 bytes from file")
                chunk = file.read(1024)
                if not chunk:
                    break
                client.sendall(chunk)
    except OSError as e:
        print(f"Error in send_file_chunks: {str(e)}")


def read_from_file():
    try:
        with open(staData, "r") as file:
            try:
                staDataDictionary = json.load(file)
                print("Credentials readed from " + staData + " \n", staDataDictionary)
                return staDataDictionary
            except:
                return {}
    except:
        print(staData, "file not found - creating...")
        open(staData, "w").close()
        return {}


def write_to_file(data, fileWithPath):
    with open(fileWithPath, "w") as file:
        print("Data saved to " + fileWithPath + " \n", data)
        json.dump(data, file)


def clear_files():
    print("Clearing file:", staData)
    open(staData, "w").close()
    print("Clearing file:", apiEndpoint)
    open(apiEndpoint, "w").close()


def try_connect_to_network():
    if wlanSTA.isconnected():
        print("Device is connected to WiFi network.", wlanSTA.ifconfig())
        return 1
    else:
        connectionStatus = 0
        print("The device is not connected to Wi-Fi, I turn on the wlanSTA interface")
        wlanSTA.active(True)

    try:
        staDataDictionary = read_from_file()
        print("Scanning ether...")
        scanedNetworks = wlanSTA.scan()
        scanedNetworks = sorted(scanedNetworks, key=lambda x: x[3], reverse=True)
        print("Here we have avaliable networks:\n", scanedNetworks)

        for ssid, bssid, channel, rssi, security, hidden in scanedNetworks:
            ssid = ssid.decode("utf-8")
            if security > 0:
                print("Trying connect to network")
                if ssid in staDataDictionary:
                    print("SSID is in database")
                    connectionStatus = do_connect(ssid, staDataDictionary[ssid])
            else:
                print("Connecting to open network")
                if ssid in staDataDictionary:
                    connectionStatus = do_connect(ssid, None)
            if connectionStatus:
                break

    except OSError as e:
        print("Error:", str(e))

    if not connectionStatus:
        print("Starting configuration webpage, no matching SSIDs in database")
        connectionStatus = www_start()

    return wlanSTA if connectionStatus else None


def do_connect(ssid, password=None):
    wlanSTA.active(True)
    wlanSTA.config(dhcp_hostname=apName)
    if not wlanSTA.isconnected():
        if password:
            print("Trying connect to", ssid, "using password", password)
        else:
            print("Trying connect to", ssid, "without password")
        wlanSTA.connect(ssid, password)
        for retry in range(200):
            connectionStatus = wlanSTA.isconnected()
            if connectionStatus:
                print("Connected")
                break
            sleep(0.1)
    return connectionStatus


def do_scan_and_get_wifi_names():
    wlanSTA.active(True)
    print("Scanning ether...")
    scanedNetworks = wlanSTA.scan()
    scanedNetworksArray = []
    for item in scanedNetworks:
        if not item[5] and item[0] != b"":
            scanedNetworksArray.append(item[0].decode("utf-8"))
    print("Avaliable networks\n", scanedNetworksArray)
    return scanedNetworksArray


def send_header(client, statusCode=200, contentLength=None):
    print("Sending header", statusCode)
    client.sendall("HTTP/1.0 {} OK\r\n".format(statusCode))
    client.sendall("Content-Type: text/html\r\n")
    if contentLength is not None:
        client.sendall("Content-Length: {}\r\n".format(contentLength))
    client.sendall("\r\n")


def send_response(client, payload, statusCode=200):
    print("Sending response", statusCode)
    contentLength = len(payload)
    send_header(client, statusCode, contentLength)
    if contentLength > 0:
        client.sendall(payload)
    client.close()


def page_main(client):
    scanedNetworksArray = do_scan_and_get_wifi_names()

    send_header(client)
    send_file_chunks(client, "data/head.html")
    send_file_chunks(client, logoBase64)
    send_file_chunks(client, "data/mainBody1.html")

    for ssid in scanedNetworksArray:
        client.sendall(
            """\
                <tr>
                    <td class="padding_r"><label><input type="radio" name="ssid" value="{ssid}"> {ssid}</label></td>
                </tr>
            """.format(
                ssid=ssid
            )
        )

    send_file_chunks(client, "data/mainBody2.html")
    client.close()


def page_configuration(client, request):
    print("Starting configuraction page")
    match = ure.search("ssid=([^&]*)&password=([^&]*)&api=(.*)", request)

    if match is None:
        print("No parameters")
        send_response(client, "No parameters", 400)
        return 0

    try:
        ssid = (
            match.group(1)
            .decode("utf-8")
            .replace("%3F", "?")
            .replace("%21", "!")
            .replace("%20", " ")
            .replace("%28", "(")
            .replace("%29", ")")
            .replace("+", " ")
        )
        password = (
            match.group(2)
            .decode("utf-8")
            .replace("%3F", "?")
            .replace("%21", "!")
            .replace("%20", " ")
            .replace("%28", "(")
            .replace("%29", ")")
            .replace("+", " ")
        )
        api = (
            match.group(3)
            .decode("utf-8")
            .replace("%2F", "/")
            .replace("%3A", ":")
            .replace("%2E", ".")
            .replace("%5F", "-")
        )

        print("Readed parameters:", ssid, password, api)
    except Exception:
        ssid = (
            match.group(1)
            .replace("%3F", "?")
            .replace("%21", "!")
            .replace("%20", " ")
            .replace("%28", "(")
            .replace("%29", ")")
            .replace("+", " ")
        )
        password = (
            match.group(2)
            .replace("%3F", "?")
            .replace("%21", "!")
            .replace("%20", " ")
            .replace("%28", "(")
            .replace("%29", ")")
            .replace("+", " ")
        )
        api = match.group(3).replace("%2F", "/").replace("%3A", ":").replace("%2E", ".").replace("%5F", "-")

        print("Readed parameters:", ssid, password, api)

    if len(ssid) == 0:
        print("SSID is empty")
        send_response(client, "Select WiFi networks", 400)
        return 0

    if len(api) == 0:
        print("API is empty")
        send_response(client, "Set the API address", 400)
        return 0

    if do_connect(ssid, password):
        write_to_file(api, apiEndpoint)
        send_header(client)
        send_file_chunks(client, "data/head.html")
        send_file_chunks(client, logoBase64)

        client.sendall(
            """\
                "/>
                <h2>The module has successfully connected to the network: {ssid}</h2>
            </div>
        </body>

        </html>
            """.format(
                ssid=ssid
            )
        )

        sleep(1)
        wlanAP.active(False)
        try:
            staDataDictionary = read_from_file()
        except OSError:
            print("Error, creating empty array")
            staDataDictionary = {}
        staDataDictionary[ssid] = password
        write_to_file(staDataDictionary, staData)

        sleep(5)
        return 1
    else:
        send_header(client)
        send_file_chunks(client, "data/head.html")
        send_file_chunks(client, logoBase64)

        client.sendall(
            """\
                "/>
                <h2 style="text-align: center;">The module failed to connect to the network: {ssid}</h2>
                <form style="text-align: center;">
                    <input class="button" type="button" value="Reconnect" onclick="history.back()"></input>
                </form>
            </div>
        </body>

        </html>
        """.format(
                ssid=ssid
            )
        )
        return 0


def handle_not_found(client, url):
    print("404 not exist")
    send_response(client, "Error 404: {}".format(url), 404)


def www_stop():
    global serverSocket

    if serverSocket:
        try:
            print("Closing socket")
            serverSocket.close()
        except OSError as e:
            print("Error occurred while closing the socket:", e)
        finally:
            serverSocket = None


def www_start(port=80):
    global serverSocket

    print("Socket opening on port:", port)
    addr = socket.getaddrinfo("0.0.0.0", port)[0][-1]

    www_stop()

    wlanSTA.active(True)
    wlanAP.active(True)

    wlanAP.config(essid=apName, password=apPassword, authmode=apAuthmode)

    try:
        serverSocket = socket.socket()
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind(addr)
        serverSocket.listen(2)

        print("Connect to WiFi ssid " + apName + ", default password: " + apPassword)
        print("Configuration panel avaliable via http://192.168.4.1")
        print("Listening on:", addr)

        while True:
            if wlanSTA.isconnected():
                wlanAP.active(False)
                return 1

            client, addr = serverSocket.accept()
            print("Client connected from", addr)
            try:
                client.settimeout(5.0)

                request = b""
                try:
                    while "\r\n\r\n" not in request:
                        request += client.recv(512)
                except OSError:
                    pass

                try:
                    request += client.recv(1024)
                    print(
                        "Received form data after \\r\\n\\r\\n(i.e. from Safari on macOS or iOS)"
                    )
                except OSError:
                    pass

                print("Request is: {}".format(request))
                if "HTTP" not in request:
                    continue

                try:
                    url = (
                        ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request)
                        .group(1)
                        .decode("utf-8")
                        .rstrip("/")
                    )
                except Exception:
                    url = (
                        ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request)
                        .group(1)
                        .rstrip("/")
                    )
                print("URL is {}".format(url))

                if url == "":
                    page_main(client)
                elif url == "configuration":
                    page_configuration(client, request)
                else:
                    handle_not_found(client, url)

            finally:
                client.close()

    except OSError as e:
        print("Error occurred during socket setup:", e)
        www_stop()
        try_connect_to_network()


def restart_wlan_sta():
    print("Disconnecting STA WiFi")
    wlanSTA.disconnect()
    sleep(0.5)
    print("Set STA WiFi interface enable")
    wlanSTA.active(True)
    return 1
