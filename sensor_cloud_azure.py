import asyncio
import datetime
import time
import RPi.GPIO as GPIO    # Import Raspberry Pi GPIO library
from w1thermsensor import W1ThermSensor, Unit   # Import temp sensor library
from azure.iot.device.aio import IoTHubDeviceClient # Import the Azure IoT modules
from azure.iot.device import Message
from colorama import Fore, Back, Style # Use this to change text color on screen output message 

# Setup the GPIO board on the Raspberry Pi...
GPIO.setwarnings(False)    # Ignore warning for now
GPIO.setmode(GPIO.BOARD)   # Use physical pin numbering
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)   # Set pin 12 (GPIO 18) to be an output pin and set initial value to low (off)

# Define the connection string and device id for connecting to the Azure IoTHub service...
#connection_string = "HostName=JKB-IOT.azure-devices.net;DeviceId=PYTHON-TESTER;SharedAccessKey=****"
connection_string = "HostName=JKB-IOT.azure-devices.net;DeviceId=WT-OFFICE-PI;SharedAccessKey=Uaql6YwfjT2H2OG0jVUY372DDTogVdCYpNO6wZImh8I="
device_id = "WT-OFFICE-PI"

#Define max temp setting above which an alert should be generated and sent...
max_temp = 80

# Define the JSON message to send to IoT Hub.
msg_txt = '{{"timestamp": "{timenow}","deviceId": "{device_id}","temperature": {temperature}}}'


async def iot_device_telemetry(client):  # This is an async function so that...
    print("IoT Hub device sending telemetry messages")

    await client.connect()

    sensor = W1ThermSensor()  # Initialize a sensor variable...

    while True:
        # Turn on the LED to indicate things are working
        GPIO.output(12, GPIO.HIGH)
        time.sleep(3) # Pause for 3 seconds

        # Get the current temp reading...
        temp = round(sensor.get_temperature(Unit.DEGREES_F),4)
        
        # Turn the LED off to indicate data point captured and processed...
        GPIO.output(12, GPIO.LOW)
        time.sleep(2) # Pause for 2 seconds
        
        # Build the message with telemetry values.
        timenow = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        msg_txt_formatted = msg_txt.format(timenow=timenow, device_id=device_id, temperature=temp)
        message = Message(msg_txt_formatted)

        # Add a custom application property to the message.
        # An IoT hub can filter on these properties without access to the message body.
        if temp > max_temp:
            print ("Current temp reading is ", Fore.RED + str(temp))
            print("Temp alert flag added to telemetry message due to high temp value")
            print(Style.RESET_ALL)
            message.custom_properties["temperatureAlert"] = "true"
        else:
            print ("Current temp reading is ", Fore.GREEN + str(temp))
            print(Style.RESET_ALL)
            message.custom_properties["temperatureAlert"] = "false"

        # Send the message.
        print("Sending message: {}".format(message))
        await client.send_message(message)
        print("Message successfully sent")
        await asyncio.sleep(10)

def main():
    print ("IoT Hub - Device Telemetry Tracking Tool")
    print ("Press Ctrl-C to exit")

    # Instantiate the client. 
    client = IoTHubDeviceClient.create_from_connection_string(connection_string)

    #
    loop = asyncio.get_event_loop()
    try:
        # Send telemetry messages while in the event loop
        loop.run_until_complete(iot_device_telemetry(client))
    except KeyboardInterrupt:
        print("IoTHubClient stopped by user")
    finally:
        # Upon application exit, shut down the client and turn off the LED
        print("Shutting down IoTHubClient")
        GPIO.output(12, GPIO.LOW)
        loop.run_until_complete(client.shutdown())
        loop.close()

if __name__ == '__main__':
    main()
