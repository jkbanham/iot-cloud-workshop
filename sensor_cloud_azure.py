import asyncio
import datetime
import time
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from w1thermsensor import W1ThermSensor, Unit   # Import temp sensor library
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

# Setup the GPIO board on the Raspberry Pi...
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)   # Set pin 12 (GPIO 18) to be an output pin and set initial value to low (off)

# Define the connection string and device id for connecting to the Azure IoTHub service...
#CONNECTION_STRING = "HostName=JKB-IOT.azure-devices.net;DeviceId=PYTHON-TESTER;SharedAccessKey=****"
CONNECTION_STRING = "HostName=JKB-IOT.azure-devices.net;DeviceId=HOME-OFFICE-PI4;SharedAccessKey=****"
device_id = "Home-RPI4"

#Define max temp setting above which an alert should be generated and sent...
max_temp = 80

# Define the JSON message to send to IoT Hub.
MSG_TXT = '{{"timestamp": "{timenow}","deviceId": {device_id},"temperature": {temperature}}}'


async def run_telemetry_sample(client):
    print("IoT Hub device sending telemetry messages")

    await client.connect()

    sensor = W1ThermSensor()  # Initialize a sensor variable...

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
        
        # Build the message with telemetry values.
        timenow = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        msg_txt_formatted = MSG_TXT.format(timenow=timenow, device_id=device_id, temperature=temp)
        message = Message(msg_txt_formatted)

        # Add a custom application property to the message.
        # An IoT hub can filter on these properties without access to the message body.
        if temp > max_temp:
            print("Temp alert flag added to telemetry message due to high value")
            message.custom_properties["temperatureAlert"] = "true"
        else:
            message.custom_properties["temperatureAlert"] = "false"

        # Send the message.
        print("Sending message: {}".format(message))
        await client.send_message(message)
        print("Message successfully sent")
        await asyncio.sleep(20)

def main():
    print ("IoT Hub - Device Telemetry Tracking Tool")
    print ("Press Ctrl-C to exit")

    # Instantiate the client. 
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    loop = asyncio.get_event_loop()
    try:
        # Run the sample in the event loop
        loop.run_until_complete(run_telemetry_sample(client))
    except KeyboardInterrupt:
        print("IoTHubClient stopped by user")
    finally:
        # Upon application exit, shut down the client
        print("Shutting down IoTHubClient")
        loop.run_until_complete(client.shutdown())
        loop.close()

if __name__ == '__main__':
    main()
