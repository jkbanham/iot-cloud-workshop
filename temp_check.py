import time  # Import the time module to enable program pauses
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from w1thermsensor import W1ThermSensor, Unit   # Import temp sensor library

# Setup the GPIO board on the Raspberry Pi...
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)   # Set pin 12 (GPIO 18) to be an output pin and set initial value to low (off)

sensor = W1ThermSensor()  # Initialize a sensor variable...

try:
    while True:
        # Turn on the LED to indicate things are working
        GPIO.output(12, GPIO.HIGH)
        time.sleep(3) # Pause for 3 seconds

        # Get the current temp reading...
        temp = round(sensor.get_temperature(Unit.DEGREES_F),4)
        
        # print the temp data point to the monitor screen...
        print ("Current temp reading is ", temp)

        # Turn the LED off to indicate data point captured and processed...
        GPIO.output(12, GPIO.LOW)
        time.sleep(2) # Pause for 2 seconds

except KeyboardInterrupt:
    GPIO.output(12, GPIO.LOW)  # Turn off the LED if it happens to still be lit
    print("Temp Sensor Program Stopped!") # Enable checking for ^C sequence from keyboard to stop program
