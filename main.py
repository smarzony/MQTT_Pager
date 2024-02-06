import utime
from machine import Pin, I2C, Pin, Timer, reset
import json
from lib.umqtt_simple import MQTTClient
from lib.ssd1306 import SSD1306_I2C
from lib.oled_api import OLED
from lib.queue import Queue
from lib.network_api import NetworkConnection

messages_q = Queue()

f = open('config.json')
config_data = json.load(f)
f.close()

TEST_MODE = True

if TEST_MODE:
    wifi_ssid = config_data['ssid_test']
    wifi_password = config_data['psswd_test']
else:
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

def main():
    button_yes = Pin(28, Pin.IN, Pin.PULL_UP)
    button_no = Pin(27, Pin.IN, Pin.PULL_UP)
    button_haps = Pin(26, Pin.IN, Pin.PULL_UP)
    i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
    utime.sleep_ms(100)
    oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)
    oled_ssd = OLED(oled, "header msg")

    oled_ssd.enable_header(False)
    # oled_ssd.message_parser("Wi-Fi connecting...")    

    network_connection = NetworkConnection(wifi_ssid, wifi_password, oled_ssd)
    ifconfig = network_connection.connect()
    oled_ssd.message_parser(f"Wi-Fi {wifi_ssid}")

    # Inicjalizacja klienta MQTT
    oled_ssd.message_parser(f"MQTT init")
    client = MQTTClient(mqtt_client_id, mqtt_broker)
    client.set_callback(mqtt_callback)
    mqtt_fail_counter = 0
    while True:
        try:
            client.connect()
            break
        except ECONNABORTED:
            mqtt_fail_counter += 1
            if mqtt_fail_counter > 10:
                oled_ssd.message_parser("RESET")
                utime.sleep(1)
                reset()

            print("MQTT failed to connect!")
            oled_ssd.message_parser(f"{mqtt_fail_counter}. MQTT retry")
            utime.sleep(1)

        except Exception as e:
            with open("log.txt", "a") as my_file:
                my_file.write(f"error: {e}\n")

    oled_ssd.message_parser(f"b: {mqtt_broker}")
    client.subscribe(mqtt_topic_read) 
    oled_ssd.message_parser(f"Sub: {mqtt_topic_read}")
    oled_ssd.message_parser(f"Pub: {mqtt_topic_write}")  
    utime.sleep(1)

    oled_ssd.enable_header()
    oled_ssd.set_header("Waiting for messages...")
    oled_ssd.messages_purge()
    oled_ssd.show()

    print("Main loop starting...")
    last_refresh_time = utime.ticks_ms()
    last_wlan_status_time = utime.ticks_ms()  
    first_message_received = False  
    while True:
        now = utime.ticks_ms()
        if now - last_refresh_time > 250:
            last_refresh_time = utime.ticks_ms()
            client.check_msg()
            oled_ssd.refresh()

        if now - last_wlan_status_time > 5000:
            last_wlan_status_time = utime.ticks_ms()
            status = network_connection.isconnected()
            if not status:
                oled_ssd.set_header("Wifi disconnected!")
                oled_ssd.refresh()
                network_connection.connect()
                oled_ssd.set_header(f"Wifi {wifi_ssid}")
            else:                
                print("Wi-Fi still connected!")                

        if not messages_q.empty():
            if not first_message_received:
                oled_ssd.enable_header(False)
                
            msg = messages_q.get()
            print('element: ', msg)
            oled_ssd.message_parser(msg)
            print("message parsed")

        if not button_yes.value():
            print("button_yes")
            utime.sleep_ms(100)
            client.publish(mqtt_topic_write, message_yes)
            oled_ssd.set_header(f"Sent {message_yes}")

        if not button_no.value():
            print("button_no")
            utime.sleep_ms(100)
            client.publish(mqtt_topic_write, message_no)
            oled_ssd.set_header(f"Sent {message_no}")

        if not button_haps.value():
            print("button_haps")
            utime.sleep_ms(100)
            client.publish(mqtt_topic_write, message_haps)
            oled_ssd.set_header(f"Sent {message_haps}")

        utime.sleep_ms(100)

main()
