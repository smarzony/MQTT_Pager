from icons import heart, cat_L, cat_R, kiss_L, kiss_R
from random import randint

class Message():
    VISIBLE_CHARS = 16
    def __init__(self, message):
        self.text = message
        self.visible = message[:self.VISIBLE_CHARS]
        self.scroll_position = 0
        if message[0] == "/":
            self.special = True
        else:
            self.special = False
            if len(message)>self.VISIBLE_CHARS:
                self.scrollable = True                
            else:
                self.scrollable = False 

    def scroll(self):
        if self.scrollable:
            if self.scroll_position < len(self.text) - self.VISIBLE_CHARS + 4: 
                self.scroll_position += 1
            else:
                self.scroll_position = -4

        if self.scroll_position < 0:
            prefix = ""
            for _ in range(abs(self.scroll_position)):
                prefix += " "
            self.visible = prefix+self.text[:self.scroll_position + self.VISIBLE_CHARS]
            # print(f"visible: {self.visible}, pos: {self.scroll_position} pre: {len(prefix)}")

        elif self.scroll_position >= 0 and self.scroll_position <= self.VISIBLE_CHARS:
            self.visible = self.text[self.scroll_position:self.scroll_position + self.VISIBLE_CHARS]

        else:
            suffix = ""
            for _ in range(self.scroll_position - self.VISIBLE_CHARS):
                suffix += " "
                
            self.visible = self.text[self.scroll_position:self.scroll_position + self.VISIBLE_CHARS]+suffix
            # print(f"visible: {self.visible}, pos: {self.scroll_position} suf: {len(suffix)}")

    def __str__(self):   
        return f"Class Message\ttext: {self.text}\tspecial: {self.special}\tscrollable: {self.scrollable}\t"    

class OLED():
    def __init__(self, display, header, max_messages=3) -> None:
        self.display = display
        self.max_messages = max_messages
        self.last_messages = []
        self.header = Message(header)
        self.display.fill(0)
        self.display.show()
        self.image_on_screen = False
        print("Display initialised")

    def message_parser(self, message):
        msg = Message(message)
        print(f"Parsing message: {msg}")
        if msg.special is False:
            if len(self.last_messages) < self.max_messages:
                self.last_messages.append(msg)
            else:
                self.last_messages = self.last_messages[1:]
                self.last_messages.append(msg) 

            self.show()
        else:
            self.image_on_screen = True
            

    def messages_purge(self):
        self.last_messages = []

    def enable_header(self, enable=True):
        if enable:
            self.max_messages = 3
        else:
            self.max_messages = 4

    def show(self):
        self.display.fill(0)  # Wyczyść ekran
        if self.max_messages == 3:
            self.display.text(self.header.visible, 0, 0)            
            for index, current_message in enumerate(self.last_messages): 
                self.display.text(current_message.visible, 0, 16*(index+1))
        elif self.max_messages > 3:
            for index, current_message in enumerate(self.last_messages): 
                self.display.text(current_message.visible, 0, 16*(index))

        self.display.show()  

    def refresh(self):
        self.header.scroll()
        for msg in self.last_messages:
            msg.scroll()
            
        self.show()

    def set_header(self, header):
        self.enable_header()
        self.header = Message(header)

# def prepare_image(oled, image, location):
#     x = location[0]
#     y = location[1]
#     for byte in image:
#         #print(f"data: {byte}")
#         for i in range(8):
#             if byte & 0x80:
#                 oled.pixel(x, y, 1)
#             x += 1
#             byte <<= 1
#         x -= 8  # Powrót do początkowej pozycji X
#         y += 1              
        
# def image_to_columns(image):
#     columns = []
#     column = bytearray(16)  # Inicjalizacja kolumny

#     for i in range(16):
#         for j in range(16):
#             pixel = (image[j] >> (15 - i)) & 0x01  # Pobierz piksel z wiersza
#             column[j] = (column[j] << 1) | pixel  # Dodaj piksel do kolumny

#         if (i + 1) % 8 == 0:  # Jeśli osiągnięto szerokość 8 pikseli
#             columns.append(bytearray(column))  # Dodaj kolumnę do listy
#             column = bytearray(16)  # Zresetuj kolumnę

#     return columns 

# def oled_display(oled, msg):
#     global last_messages, header_msg
#     if msg.startswith("/"):
#         if msg.startswith("/clear"):
#             last_messages = []
#             oled.fill(0)
#             oled.show()
            
#         if msg.startswith("/header"):
#             header_msg = msg[len("/header "):]
#             if len(header_msg) > 16:
#                 header_msg = header_msg[:16]                
         
#         if msg.startswith("/serce"):
#             oled.fill(0)  # Wyczyść ekran
#             for _ in range(15):
#                 x = randint(0,120)
#                 y = randint(0,54)
#                 prepare_image(oled, heart, (x, y))

#             oled.show()
            
#         if msg.startswith("/kot"):
#             oled.fill(0)  # Wyczyść ekran
#             x = randint(0,110)
#             y = randint(0,50)         
            
#             prepare_image(oled, cat_L, (x,y))
#             prepare_image(oled, cat_R, (x+8,y))
#             oled.show()
            
#         if msg.startswith("/kiss"):
#             oled.fill(0)  # Wyczyść ekran
#             for _ in range(15):
#                 x = randint(0,110)
#                 y = randint(0,50)
#                 prepare_image(oled, kiss_L, (x,y))
#                 prepare_image(oled, kiss_R, (x+8,y))
                
#             oled.show()
            
#     else:
#         last_messages.insert(0, msg)
#         # cut message to 16 chars
#         if len(msg) > 16:
#             msg = msg[:16]
            
#         if len(last_messages) > 0:
#             if len(last_messages) > MAX_MESSAGES_ON_SCREEN:
#                 last_messages = last_messages[:MAX_MESSAGES_ON_SCREEN] 
            
#             oled.fill(0)  # Wyczyść ekran
#             oled.text(header_msg, 0, 0)            
            
#             for index, current_message in enumerate(last_messages): 
#                 oled.text(current_message, 0, 16*(index+1))
                
#             oled.show()
