

import time
from gpiozero import Button

# GPIO PINS
BTN1 = Button(23)   # Next
BTN2 = Button(24)   # Prev
BTN3 = Button(25)   # Select


print ("Press each button. Then Ctrl-C to exit")

while True:
    if BTN1.is_pressed:
        print("NEXT Button (BTN1) is pressed")
        BTN1.wait_for_release()
    if BTN2.is_pressed:
        print("PREV Button (BTN2) is pressed")
        BTN2.wait_for_release()
    if BTN3.is_pressed:
        print("SELECT Button (BTN3) is pressed")
        BTN3.wait_for_release()

    time.sleep(0.1)

