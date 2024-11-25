import os  # Import the os module to support accessing locally saved credential/key files
import time  # Import the time module to enable program pauses
import datetime  # Import the datetime module to support adding timestamp details to the sensor data
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
from w1thermsensor import W1ThermSensor, Unit  # Import temp sensor library
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message


# Set some static variables
aziothub_con_string = "<replace with real string>"
MSG_TXT = '{{"timestamp": "{timenow}","deviceId": "RPI IOT SENSOR","temperature": {temp}}}' 

# Set the timezone as Eastern Standard
os.environ['TZ'] = 'EST+05EDT,M3.1.0,M11.1.0'
time.tzset()

# Setup the GPIO board on the Raspberry Pi...
GPIO.setwarnings(False)  # Ignore warnings
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)  # Set pin 12 (GPIO 18) to be an output pin and set initial value to low (off)

# Instantiate the objects to be used
client = IoTHubDeviceClient.create_from_connection_string(aziothub_con_string)
sensor = W1ThermSensor()  # Create a new temp sensor object...

# Print initial start message with timestamp to the monitor screen
print("Sensor data being sent from RPI to Azure IoT Hub - Press CTRL-C to exit...\n")
print("Program Run Time: Current Local Time: ", time.strftime('%X %x %Z'))

# Main code is in a try/except block to support the ability to stop it from the keyboard with ^C
try:
    while True:
        # Turn on the LED to indicate the process is starting and pause for 2 seconds
        GPIO.output(12, GPIO.HIGH)
        time.sleep(2)

        # Get the current temp and time readings...
        temp = round(sensor.get_temperature(Unit.DEGREES_F), 4)
        timenow = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # Store the collected temp and timestamp into a dictionary
        data = {"time": timenow, "temp": temp}

        msg_txt_formatted = MSG_TXT.format(timenow=timenow, temp=temp)
        message = Message(msg_txt_formatted)
        client.send_message(message)

        # Print the collected data point to the monitor screen...
        screen_message = "time: " + timenow + "  temp: " + str(temp)
        print(screen_message)

        # Turn the LED off as a visual indicator that a data point was captured and published.  Then pause for 3 seconds
        GPIO.output(12, GPIO.LOW)
        time.sleep(5)

except KeyboardInterrupt:
    print("Temp Sensor Program Stopped!")

