import adafruit_character_lcd.character_lcd as character_lcd
import board
import digitalio

class LCD():
    '''
    lcd 16x2 display class

    Wiring:
        rs: gpio 23
        en: gpio 24
        d4: gpio 25
        d5: gpio 8
        d6: gpio 7
        d7: gpio 1
    '''

    def __init__(self):
        # pins lcd is wired to
        lcd_rs = digitalio.DigitalInOut(board.D23)
        lcd_en = digitalio.DigitalInOut(board.D24)
        lcd_d4 = digitalio.DigitalInOut(board.D25)
        lcd_d5 = digitalio.DigitalInOut(board.D8)
        lcd_d6 = digitalio.DigitalInOut(board.D7)
        lcd_d7 = digitalio.DigitalInOut(board.D1)

        lcd_columns = 16
        lcd_rows = 2

        self.lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
        self.lcd.clear()

    def display(self, message: str):
        # TODO: if message line is longer than 16 make sure to move_left()
        # and loop
        # if message is longer than 3 lines then make sure to shift up somehow? 
        # or remove new lines
        self.lcd.clear()
        self.lcd.message = message

    def release(self):
        self.lcd.clear()
    