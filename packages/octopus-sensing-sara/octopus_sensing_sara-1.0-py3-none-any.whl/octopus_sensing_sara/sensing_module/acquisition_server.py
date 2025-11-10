import os
import logging
import time
import tornado.web
from pathlib import Path

from octopus_sensing.device_message_endpoint import DeviceMessageHTTPEndpoint

from octopus_sensing.device_coordinator import DeviceCoordinator
from octopus_sensing.realtime_data_endpoint import RealtimeDataEndpoint
from dotenv import load_dotenv
from octopus_sensing_sara.config import Settings
#from sensing_module.sensors import define_sensors


class HealthCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Ok")


class AccessTokenHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Ok")

def sensing_server(subject_id, session_id):
    logging.basicConfig(level=logging.INFO)

    output_path = f"output/p{str(subject_id).zfill(2)}-{session_id}"
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=False)
    
    device_coordinator = DeviceCoordinator()
    settings = Settings()

    define_sensors_module = __import__(settings.sensors_module, globals(), locals(), [settings.sensors_function])
    define_sensors = getattr(define_sensors_module, settings.sensors_function)
    device_coordinator.add_devices(define_sensors(output_path))
 
    time.sleep(5)
    healthy = device_coordinator.health_check()
    if healthy is False:
        raise Exception("Please check all devices and start the program again.")
    else:
        print("System is healthy.")

    # It receives Markers from anywhere in network, on port 9331
    message_endpoint = DeviceMessageHTTPEndpoint(device_coordinator, port=int(settings.sensing_port))
    message_endpoint.start()
    print(f"📡 Sensing server is listening on port {int(settings.sensing_port)}")

    # streaming endpoint for realtime data processing
    realtime_data_endpoint = RealtimeDataEndpoint(device_coordinator, port=int(settings.data_endpoint_port))
    realtime_data_endpoint.start()
    print("🚀 Realtime data endpoint started.")
