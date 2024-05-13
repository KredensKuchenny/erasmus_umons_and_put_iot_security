import gc
import json
import sender
import ntptime
import wifimanager
from time import sleep, localtime, time
from machine import Pin
import modules.sx127x as sx127x

SERIAL_NUMBER = "re001b"
DATA_FILE = "data/collected.data"
UTC_OFFSET = +2 * 60 * 60


def factory_reset():
    button = Pin(0, mode=Pin.IN, pull=Pin.PULL_UP)
    led = Pin(8, Pin.OUT)
    if not button.value() == True:
        print(
            "Device factory reset process incomming, hold button while led start blinking"
        )
        sleep(2)
        for i in range(2):
            led.off()
            sleep(0.2)
            led.on()
            sleep(0.2)
        if not button.value() == True:
            print("Device factory reset start")
            led.off()
            wifimanager.clear_files()
            sleep(3)
            print("Device factory reset done")
            led.on()

    button = Pin(0, Pin.IN)


def device_start():
    led = Pin(8, Pin.OUT)

    for i in range(0, 4):
        led.off()
        sleep(0.3)
        led.on()
        sleep(0.3)

    del led


def on_receive(tr, payload, crcOk):
    try:
        tr.blink()
        payload_string = payload.decode()
        payload_json = json.loads(payload_string)
        rssi = tr.getPktRSSI()
        snr = tr.getSNR()
        print("--- Received message ---")
        print(payload_string)
        print("^^^ CrcOk={}, RSSI={}, SNR={}\n".format(crcOk, rssi, snr))

        timestamp = time() + UTC_OFFSET
        time_tuple = localtime(timestamp)

        formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            time_tuple[0],
            time_tuple[1],
            time_tuple[2],
            time_tuple[3],
            time_tuple[4],
            time_tuple[5],
        )

        data = {
            "sn": SERIAL_NUMBER,
            "crcok": crcOk,
            "rssi": rssi,
            "snr": snr,
            "timestamp": formatted_time,
            "payload": payload_json,
        }

        sender.save_to_file_line_by_line(
            DATA_FILE, sender.convert_python_dictionary_to_json(data)
        )

        return data

    except Exception as e:
        print("Error in on_receive:", e)


def try_transmitter(data):
    tr.blink()
    tr.send(str(data), FIXED)


def try_reseiver():
    tr.onReceive(on_receive)  # set the receive callback

    # go into receive mode
    if FIXED:
        tr.receive(6)  # implicit header / fixed size: 6=size("Hello!")
    else:
        tr.receive(0)  # explicit header / variable packet size


# init SX127x RF module
tr = sx127x.RADIO(mode=sx127x.LORA)
# tr = sx127x.RADIO(mode=sx127x.FSK)
# tr = sx127x.RADIO(mode=sx127x.OOK)

tr.setFrequency(433000, 000)  # kHz, Hz
tr.setPower(10, True)  # power dBm (RFO pin if False or PA_BOOST pin if True)
tr.setHighPower(False)  # add +3 dB (up to +20 dBm power on PA_BOOST pin)
tr.setOCP(120, True)  # set OCP trimming (> 120 mA if High Power is on)
tr.enableCRC(True, True)  # CRC, CrcAutoClearOff (FSK/OOK mode)
tr.setPllBW(2)  #  0=75, 1=150, 2=225, 3=300 kHz (LoRa/FSK/OOK)

if tr.isLora():  # LoRa mode
    tr.setBW(250.0)  # BW: 7.8...500 kHz
    tr.setCR(8)  # CR: 5..8
    tr.setSF(10)  # SF: 6...12
    tr.setLDRO(False)  # Low Datarate Optimize
    tr.setPreamble(6)  # 6..65535 (8 by default)
    tr.setSW(0x12)  # SW allways 0x12

else:  # FSK/OOK mode
    tr.setBitrate(4800)  # bit/s
    tr.setFdev(5000.0)  # frequency deviation [Hz]
    tr.setRxBW(10.4)  # 2.6...250 kHz
    tr.setAfcBW(2.6)  # 2.6...250 kHz
    tr.enableAFC(True)  # AFC on/off
    tr.setFixedLen(False)  # fixed packet size or variable
    tr.setDcFree(0)  # 0=Off, 1=Manchester, 2=Whitening

tr.dump()
tr.collect()

# SELECT MODE (RX / TX)
# MODE = 1  # transmitter
MODE = 2  # receiver

# implicit header (LoRa) or fixed packet length (FSK/OOK)
# FIXED = True
FIXED = False

factory_reset()

try:
    wifimanager.wlanSTA.disconnect()
except:
    print("First WiFi module configuration")

wifimanager.wlanSTA.active(False)
wlan = wifimanager.try_connect_to_network()

if wlan is None:
    print("Could not initialize the network connection.")
    while True:
        wlan = wifimanager.try_connect_to_network()
        if wlan not in None:
            break

print("Connection initialized")
gc.collect()

print("Starting device...")

ntptime.host = "time.google.com"
ntptime.settime()

device_start()
print("Ready to go")

if MODE == 1:
    # transmitter
    while True:
        try_transmitter(str(SERIAL_NUMBER))
        sleep(5)

elif MODE == 2:
    # reseiver
    try_reseiver()
    # sleep(-1)  # wait interrupt

    while True:
        print("device in while loop...")

        sender.read_and_send_first_line(
            DATA_FILE, sender.read_from_file(wifimanager.apiEndpoint)
        )

        sleep(2)
