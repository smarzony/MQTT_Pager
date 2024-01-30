import time
import network
from umqtt_simple import MQTTClient
import utime
from machine import Pin, I2C
from lib.ssd1306 import SSD1306_I2C
import framebuf
from icons import heart, cat_L, cat_R, kiss_L, kiss_R
from random import randint

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
utime.sleep_ms(100)
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Konfiguracja połączenia Wi-Fi
wifi_ssid = "smarzony"
wifi_password = "metalisallwhatineed"

# Konfiguracja MQTT
mqtt_broker = "broker.emqx.io"  # Zastąp to adresem URL brokera MQTT
mqtt_topic = "Quociok/"  # Zastąp to nazwą tematu MQTT
mqtt_client_id = "pico_client"  # Wybierz unikalną nazwę klienta MQTT

# Czas oczekiwania na wiadomość MQTT (w sekundach)
mqtt_timeout = 10  # Przykładowy timeout - możesz dostosować

header_msg = "Quociok Message:"
last_messages = []
MAX_MESSAGES_ON_SCREEN = 3

def prepare_image(oled, image, location):
    x = location[0]
    y = location[1]
    for byte in image:
        #print(f"data: {byte}")
        for i in range(8):
            if byte & 0x80:
                oled.pixel(x, y, 1)
            x += 1
            byte <<= 1
        x -= 8  # Powrót do początkowej pozycji X
        y += 1
        
  
def prepare_image2(oled, image, location):
    x = location[0]
    y = location
    for row_index, row_data in enumerate(image):
        for col_index in range(16):
            pixel = (row_data >> (15 - col_index)) & 0x01
            oled.pixel(x + col_index, y + row_index, pixel)        
        
def image_to_columns(image):
    columns = []
    column = bytearray(16)  # Inicjalizacja kolumny

    for i in range(16):
        for j in range(16):
            pixel = (image[j] >> (15 - i)) & 0x01  # Pobierz piksel z wiersza
            column[j] = (column[j] << 1) | pixel  # Dodaj piksel do kolumny

        if (i + 1) % 8 == 0:  # Jeśli osiągnięto szerokość 8 pikseli
            columns.append(bytearray(column))  # Dodaj kolumnę do listy
            column = bytearray(16)  # Zresetuj kolumnę

    return columns 

# Callback do obsługi przychodzących wiadomości MQTT
def mqtt_callback(topic, msg):
    print("Odebrano wiadomość od {}: {}".format(topic, msg))
    global last_message_time, last_messages, header_msg
    last_message_time = utime.ticks_ms()    
    
    if msg.startswith("/"):
        if msg.startswith("/clear"):
            last_messages = []
            oled.fill(0)
            oled.show()
            
        if msg.startswith("/header"):
            header_msg = msg[len("/header "):]
            if len(header_msg) > 16:
                header_msg = header_msg[:16]                
         
        if msg.startswith("/serce"):
            oled.fill(0)  # Wyczyść ekran
            for _ in range(15):
                x = randint(0,120)
                y = randint(0,54)
                prepare_image(oled, heart, (x, y))

            oled.show()
            
        if msg.startswith("/kot"):
            oled.fill(0)  # Wyczyść ekran
            x = randint(0,110)
            y = randint(0,50)         
            
            prepare_image(oled, cat_L, (x,y))
            prepare_image(oled, cat_R, (x+8,y))
            oled.show()
            
        if msg.startswith("/kiss"):
            oled.fill(0)  # Wyczyść ekran
            for _ in range(15):
                x = randint(0,110)
                y = randint(0,50)
                prepare_image(oled, kiss_L, (x,y))
                prepare_image(oled, kiss_R, (x+8,y))
                
            oled.show()
            
    else:
        last_messages.insert(0, msg)
        # cut message to 16 chars
        if len(msg) > 16:
            msg = msg[:16]
            
        if len(last_messages) > 0:
            if len(last_messages) > MAX_MESSAGES_ON_SCREEN:
                last_messages = last_messages[:MAX_MESSAGES_ON_SCREEN] 
            
            oled.fill(0)  # Wyczyść ekran
            oled.text(header_msg, 0, 0)
            
            
            for index, current_message in enumerate(last_messages): 
                oled.text(current_message, 0, 16*(index+1))
                
            oled.show()

# Funkcja do łączenia się z siecią Wi-Fi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Łączenie z siecią Wi-Fi...")
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            pass
    print("Połączono z siecią Wi-Fi:", wlan.ifconfig())

try:
    connect_to_wifi()  # Połącz się z siecią Wi-Fi
    oled.fill(0)  # Wyczyść ekran
    oled.text("Wifi OK", 0, 0)

    

    # Inicjalizacja klienta MQTT
    client = MQTTClient(mqtt_client_id, mqtt_broker)
    client.set_callback(mqtt_callback)
    client.connect()
    oled.text("MQTT OK", 0, 16)

    # Subskrypcja tematu MQTT
    client.subscribe(mqtt_topic)
    
    oled.text("Waiting for", 0, 32)
    oled.text("messages", 0, 48)
    
    oled.show()

    while True:
        client.wait_msg()  # Oczekuj na przychodzące wiadomości MQTT

except KeyboardInterrupt:
    pass