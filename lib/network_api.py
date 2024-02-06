import network
import utime
import machine

class NetworkConnection():
    def __init__(self, ssid, password, oled_ssd):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.ifconfig = None
        self.connection_counter = 0
        self.oled_ssd = oled_ssd
        if self.isconnected():
            self.disconnect()

    def connect(self):
        # self.wlan = network.WLAN(network.STA_IF)
        if not self.isconnected():
            self.oled_ssd.message_parser("Wifi connecting")
            print('Connecting to Wi-Fi...')            
            self.wlan.connect(self.ssid, self.password)
        
            while not self.isconnected():
                utime.sleep(1)
                self.connection_counter += 1
                self.oled_ssd.message_parser(f"{self.connection_counter}. Connecting..")
                print(f"{self.connection_counter}.Waiting for connection")
                if self.connection_counter > 10:
                    print("Software reset!")
                    self.oled_ssd.message_parser("RESET")
                    machine.reset()
        else:
            print("Wi-Fi was connected previously!")
            self.oled_ssd.message_parser("WiFi was conn.")

        self.ifconfig = self.wlan.ifconfig()
        print(f"Wi-Fi connected: {self.ssid}, {self.ifconfig}")
        self.oled_ssd.message_parser(f"IP: {self.ifconfig[0]}")
        if self.ifconfig[0] == '0.0.0.0':
            print("Connected to empty network! Disconnecting and reconnecting...")
            self.oled_ssd.message_parser("Empty net, recon")
            
            self.disconnect()
            self.connect()

        self.connection_counter = 0
        return self.ifconfig       

    def isconnected(self):
        return self.wlan.isconnected()

    def disconnect(self):
        self.oled_ssd.message_parser("Disconnecting!")
        print("Wi-Fi disconnecting!")
        self.wlan.disconnect()
        while self.isconnected():
            utime.sleep(1)
            print("Disconnecting in progress..")

        print("Wi-Fi disconnected!")
        self.oled_ssd.message_parser("Disconnected!")