import os  # Import the os module to support accessing locally saved credential/key files
import time  # Import the time module to enable program pauses
import datetime  # Import the datetime module to support adding timestamp details to the sensor data
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
from w1thermsensor import W1ThermSensor, Unit  # Import temp sensor library
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
import asyncio


# Set some static variables
aziothub_con_string = "<replace with real connection string from your IotHub device>"
aziothub_device = "<replace with real device ID from your IoTHub device>"

msg_txt = '{{"timestamp": "{timenow}","deviceId": "{device_id}","temp": "{temp}"}}' 

# Set the timezone as Eastern Standard
os.environ['TZ'] = 'EST+05EDT,M3.1.0,M11.1.0'
time.tzset()

# Setup the GPIO board on the Raspberry Pi...
GPIO.setwarnings(False)  # Ignore warnings
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(12, GPIO.OUT, initial=GPIO.LOW)  # Set pin 12 (GPIO 18) to be an output pin and set initial value to low (off)

async def iot_device_telemetry(client):
    print("IoT Hub device sending telemetry messages")
    await client.connect()
    sensor = W1ThermSensor()  # Create a new temp sensor object...

    while True:
        # Turn on the LED to indicate the process is starting and pause for 2 seconds
        GPIO.output(12, GPIO.HIGH)
        time.sleep(2)

        # Get the current temp and time readings...
        temp = round(sensor.get_temperature(Unit.DEGREES_F), 4)
        
        # Turn the LED off to indicate data point captured and processed...
        GPIO.output(12, GPIO.LOW)
        time.sleep(2) # Pause for 2 seconds
        
        # Build the message with telemetry values.
        timenow = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        msg_txt_formatted = msg_txt.format(timenow=timenow, device_id=device_id, temp=temp)
        message = Message(msg_txt_formatted)        
        
        # Send the message.
        print("Sending message: {}".format(message))
        await client.send_message(message)
        print("Message successfully sent")
        await asyncio.sleep(10)


def main():
    print ("IoT Hub - IoT Device Telemetry Tool")
    print ("Press Ctrl-C to exit\n")

    # Instantiate the client. 
    client = IoTHubDeviceClient.create_from_connection_string(aziothub_con_string)

    #
    loop = asyncio.get_event_loop()
    try:
        # Send telemetry messages while in the event loop
        loop.run_until_complete(iot_device_telemetry(client))
    except KeyboardInterrupt:
        print("IoTHubClient device stopped by user")
    finally:
        # Upon application exit, shut down the client and turn off the LED
        print("\nShutting down IoTHubClient")
        GPIO.output(12, GPIO.LOW)
        loop.run_until_complete(client.shutdown())
        loop.close()

if __name__ == '__main__':
    main()
