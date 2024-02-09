import os # Import the os module to support accessing locally saved credential/key files
import time # Import the time module to enable program pauses
import datetime # Import the datetime module to support adding timestamp details to the snesor data
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from w1thermsensor import W1ThermSensor, Unit # Import temp sensor library
from google.cloud import pubsub_v1 #Import the pubsub module to support publsihing data into GCP cloud
import json #Import the json module to simplify publsihing sensor data in a json format

# Set some static GCP connection variables
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/iot-cloud-workshop/<REPLACE WITH YOUR KEY FILE NAME>.json"
project_id= "<REPLACE WITH YOUR RPOJECT ID>"  # The project id will look like this: iot-class-nnnnnn
topic_name = 'iot-sensor'

# Create a new pubsub object that will let us use the GCP PubSub API to publish our sensor data
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

# Set the timezone as Eastern Standard
os.environ['TZ'] = 'EST+05EDT,M3.1.0,M11.1.0'
time.tzset()

# Setup the GPIO board on the Raspberry Pi...
GPIO.setwarnings(False)    # Ignore warnings
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)   # Set pin 12 (GPIO 18) to be an output pin and set initial value to low (off)

sensor = W1ThermSensor()  # Create a new sensor object...

# Print initial start message with timestamp to the monitor screen
print("Sensor data being sent from RPI to GCP - Press CTRL-C to exit...\n")
print("Program Run Time: Current Local Time: ",time.strftime('%X %x %Z'))

# Main code is in a try/exccept block to support the ability to stop it from the keyboard with ^C
try:
    while True:
        # Turn on the LED to indicate the process is starting and pause for 2 seconds
        GPIO.output(12, GPIO.HIGH)
        time.sleep(2)

        # Get the current temp and time readings...
        temp = round(sensor.get_temperature(Unit.DEGREES_F),4)
        timenow = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        # Store the collected temp and timestamp into a dictionary
        data = {"time": timenow, "temp": temp}
        
        # Print the collected data point to the monitor screen...
        screen_message = "time: " + timenow + "  temp: " + str(temp)
        print (screen_message)

        # COnvert the data dictionary into json format, encode it as a bytestring and publish it to the GCP Pub/Sub topic
        publisher.publish(topic_path, data=(json.dumps(data)).encode("utf-8"))

        # Turn the LED off as a visual indicator that a data point was captured and published.  Then pause for 3 seconds
        GPIO.output(12, GPIO.LOW)
        time.sleep(3)

except KeyboardInterrupt:
    print("Temp Sensor Program Stopped!")

