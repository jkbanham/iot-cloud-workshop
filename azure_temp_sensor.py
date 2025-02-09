import time
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
from w1thermsensor import W1ThermSensor, Unit  # Import temp sensor library
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
import asyncio


# Set some static variables
aziothub_con_string = "<Replace with your real connection string from your IoTHub device!>"
name = "RPI-IOT"

msg_txt = '{{"name": "{name}","temp": {temp}}}' 

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
        temp = int(sensor.get_temperature(Unit.DEGREES_F))
        
        # Turn the LED off to indicate data point captured and processed...
        GPIO.output(12, GPIO.LOW)
        time.sleep(2) # Pause for 2 seconds
        
        # Build the message with telemetry values.
        msg_txt_formatted = msg_txt.format(name=name, temp=temp)
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
