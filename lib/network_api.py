import network
import utime
import machine

class NetworkConnection():
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.ifconfig = None
        self.connection_counter = 0
        if self.isconnected():
            self.disconnect()

    def connect(self):
        # self.wlan = network.WLAN(network.STA_IF)
        if not self.isconnected():
            print('Connecting to Wi-Fi...')            
            self.wlan.connect(self.ssid, self.password)
        
            while not self.isconnected():
                utime.sleep(1)
                self.connection_counter += 1
                print(f"{self.connection_counter}.Waiting for connection")
                if self.connection_counter > 10:
                    print("Software reset!")
                    machine.reset()
        else:
            print("Wi-Fi was connected previously!")

        self.ifconfig = self.wlan.ifconfig()
        print(f"Wi-Fi connected: {self.ssid}, {self.ifconfig}")
        if self.ifconfig[0] == '0.0.0.0':
            print("Connected to empty network! Disconnecting and reconnecting...")
            self.disconnect()
            self.connect()    

        self.connection_counter = 0
        return self.ifconfig       

    def isconnected(self):
        return self.wlan.isconnected()

    def disconnect(self):
        print("Wi-Fi disconnecting!")
        self.wlan.disconnect()
        while self.isconnected():
            utime.sleep(1)
            print("Disconnecting in progress..")

        print("Wi-Fi disconnected!")