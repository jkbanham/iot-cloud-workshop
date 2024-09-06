import os
import asyncio
import random
import datetime
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

CONNECTION_STRING = "HostName=JKB-IOT.azure-devices.net;DeviceId=PYTHON-TESTER;SharedAccessKey=xNyKi/gMewQHdDyn0wNIn1cWcNOAaAuU3AIoTKUDn7M="

# Define the JSON message to send to IoT Hub.
TEMPERATURE = 74.0
HUMIDITY = 60
MSG_TXT = '{{"timestamp": "{timenow}","deviceId": "Python Tester","temperature": {temperature},"humidity": {humidity}}}'


async def run_telemetry_sample(client):
    # This sample will send temperature telemetry every second
    print("IoT Hub device sending periodic messages")

    await client.connect()

    while True:
        # Build the message with simulated telemetry values.
        temperature = TEMPERATURE + (random.random() * 15)
        humidity = HUMIDITY + (random.random() * 20)
        timenow = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        msg_txt_formatted = MSG_TXT.format(timenow=timenow, temperature=temperature, humidity=humidity)
        message = Message(msg_txt_formatted)

        # Add a custom application property to the message.
        # An IoT hub can filter on these properties without access to the message body.
        if temperature > 90:
            message.custom_properties["temperatureAlert"] = "true"
        else:
            message.custom_properties["temperatureAlert"] = "false"

        # Send the message.
        print("Sending message: {}".format(message))
        await client.send_message(message)
        print("Message successfully sent")
        await asyncio.sleep(20)

def main():
    print ("IoT Hub Quickstart #1 - Simulated device")
    print ("Press Ctrl-C to exit")

    # Instantiate the client. Use the same instance of the client for the duration of
    # your application
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    loop = asyncio.get_event_loop()
    try:
        # Run the sample in the event loop
        loop.run_until_complete(run_telemetry_sample(client))
    except KeyboardInterrupt:
        print("IoTHubClient sample stopped by user")
    finally:
        # Upon application exit, shut down the client
        print("Shutting down IoTHubClient")
        loop.run_until_complete(client.shutdown())
        loop.close()

if __name__ == '__main__':
    main()