import adafruit_character_lcd.character_lcd as character_lcd
import board
import digitalio
import time

if __name__ == '__main__':

    lcd_rs = digitalio.DigitalInOut(board.D23)
    lcd_en = digitalio.DigitalInOut(board.D24)
    lcd_d4 = digitalio.DigitalInOut(board.D25)
    lcd_d5 = digitalio.DigitalInOut(board.D8)
    lcd_d6 = digitalio.DigitalInOut(board.D7)
    lcd_d7 = digitalio.DigitalInOut(board.D1)

    lcd_columns = 16
    lcd_rows = 2

    lcd = character_lcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
    lcd.clear()
    msg = "Haider Baloch\n1420 Geddes Ave"
    splits = msg.split('\n')
    max_line_len = max(len(splits[0]),len(splits[1]))
    print(max_line_len)

    while True:
        print('next iter')
        lcd.message = msg

        for _ in range(max_line_len):
            time.sleep(0.5)
            lcd.move_left()
