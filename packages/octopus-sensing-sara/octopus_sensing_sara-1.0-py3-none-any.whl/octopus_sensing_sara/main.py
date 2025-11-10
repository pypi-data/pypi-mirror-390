import time
import socket
import subprocess
import multiprocessing
import argparse
from octopus_sensing_sara.perception_module.realtime_processing import realtime_perception
from octopus_sensing_sara.sensing_module.acquisition_server import sensing_server
from octopus_sensing_sara.config import Settings

def run_octopus_sensing_processing(prediction_window, sensors_names, sensing_address,
                                    sensing_port, predict_module, predict_function):

    #env = {"PYTHONPATH": ".", **os.environ}
    command = [
        "poetry", "run", "octopus-sensing-processing",
        "-t", f"{prediction_window}",
        "-d", f"{sensors_names}",
        "-e", f"{sensing_address}:{sensing_port}",
        "-m", f"{predict_module}",
        "-f", f"{predict_function}"
    ]
    subprocess.run(command)

def is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False

def main():

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("-i", "--subject_id",
                            help="The subject ID",
                            default="s1",
                            type=str)
    
    arg_parser.add_argument("-s", "--session_id",
                            help="The session ID",
                            default="s1",
                            type=str)
    args = arg_parser.parse_args()

    settings = Settings()



    sensing_module = multiprocessing.Process(target=sensing_server, args=(args.subject_id, args.session_id))
    sensing_module.start()

    print(f"⏳ Waiting for sensing server to listen on {settings.sensing_address}:{settings.sensing_port}...")
    i = 10
    #while not is_port_open(settings.sensing_address, settings.sensing_port) & i > 0:
    #    time.sleep(0.25)
    #    i -= 1
    print("✅ Sensing server is running.")
    time.sleep(5)

    processing = multiprocessing.Process(target=run_octopus_sensing_processing,
                                         args=(settings.prediction_window, settings.sensors_names, settings.processing_address,
                                               settings.processing_port, settings.predict_module, settings.predict_function))
    processing.start()

    print(f"⏳ Waiting for sensing server to listen on {settings.processing_address}:{settings.processing_port}...")
    i = 10
    #while not is_port_open(settings.processing_address, settings.processing_port) & i > 0:
    #    time.sleep(0.25)
    #    i -= 1
    time.sleep(5)
    print("✅ Processing server is running.")
    #perception_module = multiprocessing.Process(target=realtime_perception)
    #perception_module.start()


    sensing_module.join()
    #processing.join()
    #perception_module.join()


if __name__ == "__main__":
    main()