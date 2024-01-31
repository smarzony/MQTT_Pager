import network
import utime
from machine import Pin, I2C, Pin
import json
from lib.umqtt_simple import MQTTClient
from lib.ssd1306 import SSD1306_I2C
from lib.oled_api import OLED
from lib.queue import Queue

messages_q = Queue()

f = open('config.json')
config_data = json.load(f)
f.close()

wifi_ssid = config_data['ssid']
wifi_password = config_data['psswd']
mqtt_broker = config_data['broker']
mqtt_topic_read = config_data['topic']+config_data['suffix_read']
mqtt_topic_write = config_data['topic']+config_data['suffix_write']
mqtt_client_id = "pico_client"
mqtt_timeout = 10  # Przykładowy timeout - możesz dostosować
message_yes = config_data["message_yes"]
message_no = config_data["message_no"]
message_haps = config_data["message_haps"]

# Callback do obsługi przychodzących wiadomości MQTT
def mqtt_callback(topic, msg):
    print("Message in topic {}: {}".format(topic.decode(), msg.decode())) 
    messages_q.put(msg.decode())

class NetworkConnection():
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        # self.wlan = network.WLAN(network.STA_IF)
        if not self.isconnected():
            print('Connecting to Wi-Fi...')
            self.wlan.active(True)
            self.wlan.connect(self.ssid, self.password)
        
            while not self.isconnected():
                utime.sleep(1)
                print("Waiting for connection")
                pass

        print(f"Wi-Fi connected: {self.ssid}, {self.wlan.ifconfig()}")

    def isconnected(self):
        return self.wlan.isconnected()

    def disconnect(self):
        print("Wi-Fi disconnecting!")
        # self.wlan.disconnect()
        self.wlan.active(False)
        utime.sleep(1)

def main():
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
    utime.sleep_ms(100)
    oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)
    oled_ssd = OLED(oled, "header msg")
    network_connection = NetworkConnection(wifi_ssid, wifi_password)
    network_connection.disconnect()
    network_connection.connect()

    button_yes = Pin(28, Pin.IN, Pin.PULL_UP)
    button_no = Pin(27, Pin.IN, Pin.PULL_UP)
    button_haps = Pin(26, Pin.IN, Pin.PULL_UP)

    oled.fill(0)  # Wyczyść ekran
    oled.text("Wifi OK", 0, 0)        

    # Inicjalizacja klienta MQTT
    client = MQTTClient(mqtt_client_id, mqtt_broker)
    client.set_callback(mqtt_callback)
    client.connect()
    oled.text("MQTT OK", 0, 16)

    # Subskrypcja tematu MQTT
    client.subscribe(mqtt_topic_read)
    
    oled.text(f"Sub: {mqtt_topic_read}", 0, 32)
    oled.text(f"Pub: {mqtt_topic_write}", 0, 48)        
    oled.show()

    last_refresh_time = utime.ticks_ms()
    last_wlan_status_time = utime.ticks_ms()
    while True:
        now = utime.ticks_ms()
        if now - last_refresh_time > 250:
            last_refresh_time = utime.ticks_ms()
            client.check_msg()
            oled_ssd.refresh()

        if now - last_wlan_status_time > 5000:
            last_wlan_status_time = utime.ticks_ms()
            # status = check_wifi_connection()
            status = network_connection.isconnected()
            if not status:
                oled.fill(0)  # Wyczyść ekran
                oled.text("Wifi fail!", 0, 0) 
                oled.show() 
                network_connection.disconnect()
                network_connection.connect()

        if not messages_q.empty():
            msg = messages_q.get()
            print('element: ', msg)
            oled_ssd.message_parser(msg)
            print("message parsed")

        if not button_yes.value():
            print("button_yes")
            utime.sleep_ms(100)
            client.publish(mqtt_topic_write, message_yes)

        if not button_no.value():
            print("button_no")
            utime.sleep_ms(100)
            client.publish(mqtt_topic_write, message_no)

        if not button_haps.value():
            print("button_haps")
            utime.sleep_ms(100)
            client.publish(mqtt_topic_write, message_haps)

        utime.sleep_ms(100)

main()