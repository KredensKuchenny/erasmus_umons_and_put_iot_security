import gc
import json
import hashlib
import ubinascii
from time import sleep
from ucryptolib import aes
import modules.sx127x as sx127x
from machine import Pin, I2C, deepsleep, ADC
from modules.sht3x_16bit import SHT3x

SERIAL_NUMBER = "in001b"
AES_KEY = b"32_char_string"
SLEEP_TIME_FILE = "data/sleep_time.txt"
SLEEP_TIME_ARRAY = {1: 50, 2: 110, 3: 290, 4: 590, 5: 890, 6: 1790, 7: 3590}


def sleep_settings(pin):
    button = Pin(23, mode=Pin.OUT, pull=Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_FALLING, handler=None)

    key_temp = 0
    value_temp = 0
    current_sleep_time = int(read_from_file(SLEEP_TIME_FILE))
    print("Current sleep time: ", current_sleep_time)

    for key, value in SLEEP_TIME_ARRAY.items():
        if current_sleep_time == value:
            print("Current sleep time key: ", key)
            key_temp = key

    if key_temp == len(SLEEP_TIME_ARRAY):
        print("No more settings, back to beginning")
        key_temp = 0

    value_temp = SLEEP_TIME_ARRAY[key_temp + 1]

    print("Setting new sleep time: ", value_temp)
    write_to_file(SLEEP_TIME_FILE, str(value_temp))

    led = Pin(17, Pin.OUT)

    led.on()
    print("Diode info start")
    sleep(1)
    led.off()
    sleep(1)

    for i in range(0, key_temp):
        print("Show mode using blink inetration: ", i)
        led.on()
        sleep(0.2)
        led.off()
        sleep(0.2)

    del led

    button = Pin(23, mode=Pin.IN, pull=Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_FALLING, handler=sleep_settings)


def device_start():
    led = Pin(17, Pin.OUT)

    for i in range(0, 4):
        led.on()
        sleep(0.3)
        led.off()
        sleep(0.3)

    del led


def aes_encryption(data):
    sha256 = hashlib.sha256()
    sha256.update(AES_KEY)
    aes_iv = sha256.digest()[:16]

    MODE_CBC = 2
    cipher = aes(AES_KEY, MODE_CBC, aes_iv)

    print(f"Data to encrypt: {data}")
    print("Using AES{}-CBC cipher".format(len(AES_KEY * 8)))

    # AES works in 16-bytes blocks, so we must pad the input text

    padded = data + " " * (16 - len(data) % 16)

    encrypted = cipher.encrypt(padded)
    encrypted_base64_b2a = ubinascii.b2a_base64(encrypted).decode().strip()
    encrypted_base64_a2b = ubinascii.a2b_base64(encrypted_base64_b2a)

    print("Encrypted: {}".format(encrypted))
    print("Encrypted (Base64): {}".format(encrypted_base64_b2a))
    print("Encrypted (Base64 to Binary): {}".format(encrypted_base64_a2b))

    # decipher = aes(AES_KEY, MODE_CBC, aes_iv)
    # decrypted = decipher.decrypt(encrypted_base64_a2b)
    # decrypted_plain = decrypted.rstrip()
    # decrypted_plain_str = decrypted_plain.decode('utf-8')
    # print(f"Decrypted: {decrypted}")

    # encrypted_str = str(encrypted)
    # # Data parse str to bytes
    # parsed_bytes = bytes.fromhex(data_hex.hex())
    # print(parsed_bytes)

    return encrypted_base64_b2a


def get_measurment(sht31, adc, deep_sleep, number_of_measurements=1):
    if gc.mem_free() < 102000:
        gc.collect()

    data_array = [0] * 3

    data = {
        "time": deep_sleep,
        "sht31": {
            "temp": None,
            "hum": None,
        },
        "vol": None,
    }

    for i in range(number_of_measurements):
        sht31.measure()
        battery_voltage = adc.read_u16() * 5.11 / 65535

        sleep(0.2)

        data_array[0] += float(sht31.temperature())
        data_array[1] += float(sht31.humidity())
        data_array[2] += float(battery_voltage)

        print("i number:", i, ", measurments:", data_array)

        if i + 1 == number_of_measurements:
            data["sht31"]["temp"] = round((data_array[0] / number_of_measurements), 2)
            data["sht31"]["hum"] = round((data_array[1] / number_of_measurements), 2)
            data["vol"] = round((data_array[2] / number_of_measurements), 2)

        sleep(1)

    json_data = json.dumps(data)
    print("Json data to encrypt:", json_data)
    encrypted_json_data = aes_encryption(json_data)
    package = {"sn": SERIAL_NUMBER, "data": encrypted_json_data}
    json_package = json.dumps(package)
    print("Json package to send:", json_package)
    try_transmitter(json_package)


def read_from_file(file):
    try:
        with open(file, "r") as f:
            return f.read()
    except FileNotFoundError:
        with open(file, "a") as f:
            f.write()


def write_to_file(file, data):
    with open(file, "w+") as f:
        f.write(data)


def on_receive(tr, payload, crcOk):
    tr.blink()
    payload_string = payload.decode()
    # payload_string = str(payload)
    rssi = tr.getPktRSSI()
    snr = tr.getSNR()
    print("--- Received message ---")
    print(payload_string)
    print("^^^ CrcOk={}, RSSI={}, SNR={}\n".format(crcOk, rssi, snr))

    return payload_string


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


i2c = I2C(1, sda=Pin(26), scl=Pin(27))
sht31 = SHT3x(i2c)
adc = ADC(Pin(28, mode=Pin.IN))

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
MODE = 1  # transmitter
# MODE = 2 # receiver

# implicit header (LoRa) or fixed packet length (FSK/OOK)
# FIXED = True
FIXED = False

sleep_time = int(read_from_file(SLEEP_TIME_FILE)) * 1000
print("Starting device...")
device_start()

button = Pin(23, mode=Pin.IN, pull=Pin.PULL_UP)
# an external interrupt to wake from sleep if the door opens
button.irq(trigger=Pin.IRQ_FALLING, handler=sleep_settings)

print("Ready to go")

if MODE == 1:
    # transmitter
    while True:
        current_sleep_time = int(read_from_file(SLEEP_TIME_FILE)) + 10
        get_measurment(sht31, adc, current_sleep_time, 3)
        sleep(5)
        deepsleep(sleep_time)

elif MODE == 2:
    # reseiver
    try_reseiver()
    sleep(-1)  # wait interrupt
