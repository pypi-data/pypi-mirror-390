import os
import multiprocessing

def get_camera_path():
    files = os.listdir("/dev/v4l/by-id")
    for file in files:
        if file.find("RealSense") != -1 and file.find("index0") != -1:
                return "/dev/v4l/by-id/{0}".format(file)

    return None



#def get_audio_recorder_id():
#    import miniaudio
#    devices = miniaudio.Devices()
#    devices_info = devices.get_captures()
#    for i in range(len(devices_info)):
#        if devices_info[i]["name"].find("Webcam") != -1:
#            return i
#    return -1

def get_audio_recorder_id():
    class Child(multiprocessing.Process):
        def __init__(self, queue):
            super().__init__()
            self._queue = queue

        def run(self):
            import miniaudio
            devices = miniaudio.Devices()
            devices_info = devices.get_captures()
            for i in range(len(devices_info)):
                if devices_info[i]["name"].find("Webcam") != -1:
                    self._queue.put(i)
                    return 0
            self._queue.put(-1)
            return 1

    queue = multiprocessing.Queue()
    child = Child(queue)
    child.start()
    answer = queue.get()
    # Ensuring the child process is terminated
    child.join()
    return answer

