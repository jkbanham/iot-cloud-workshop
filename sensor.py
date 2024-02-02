import os
import time
import datetime
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from w1thermsensor import W1ThermSensor, Unit   # Import temp sensor library
from google.cloud import pubsub_v1
import json

# Set GCP variables for connection
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/PycharmProjects/SensorTest/jkb-iot-project-5575900f169f.json"
#project_id= "jkb-iot-project"
#topic_name = 'iot-sensor'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/home/pi/sensor_test/iot-class-410121-29be3e3bc63c.json"
project_id= "iot-class-410121"
topic_name = 'iot-sensor'

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

os.environ['TZ'] = 'EST+05EDT,M3.1.0,M11.1.0'
time.tzset()

# Setup the GPIO board on the Raspberry Pi...
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)   # Set pin 12 (GPIO 18) to be an output pin and set initial value to low (off)

sensor = W1ThermSensor()  # Initialize a sensor variable...

print("Sensor data being sent from RPI to GCP - Press CTRL-C to exit...\n")
print("Program Run Time: Current Local Time: ",time.strftime('%X %x %Z'))

try:
    while True:
        # Turn on the LED to indicate things are working
        GPIO.output(12, GPIO.HIGH)
        time.sleep(3)

        # Get the current temp and time readings...
        temp = round(sensor.get_temperature(Unit.DEGREES_F),4)
        timenow = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        data = {"time": timenow, "temp": temp}
        
        # print the collected data point to the monitor screen...
        screen_message = "time: " + timenow + "  temp: " + str(temp)
        print (screen_message)
        #print("Data message sent to Pub/Sub: ", data)

        # Post the data to the GCP Pub/Sub topic...
        publisher.publish(topic_path, data=(json.dumps(data)).encode("utf-8"))  # data must be a bytestring.
        # Publish failures shall be handled in the callback function.
        #future.add_done_callback(get_callback(future, data))

        # Turn the LED off to indicate data point captured and processed...
        GPIO.output(12, GPIO.LOW)
        time.sleep(5)

except KeyboardInterrupt:
    print("Temp Sensor Program Stopped!")

