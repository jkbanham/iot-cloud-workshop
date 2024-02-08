import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
import time # Import the time module to enable program pauses

# Setup the GPIO board on the Raspberry Pi...
GPIO.setwarnings(False)    # Ignore warnings
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)   # Set pin 12 (GPIO 18) to be an output pin and set initial value to low (off)

try:
    while True:
        # Turn on the LED
        GPIO.output(12, GPIO.HIGH)
        time.sleep(3) # Pause for 3 seconds...

        # Turn off the LED 
        GPIO.output(12, GPIO.LOW)
        time.sleep(2) # Pause for 2 seconds

except KeyboardInterrupt:
    print("LED Blink Program Stopped!")  # Enable checking for ^C sequence from keyboard to stop program

