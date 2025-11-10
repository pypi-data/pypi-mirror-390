from octopus_sensing.devices import CameraStreaming as OriginalCameraStreaming
from octopus_sensing.devices import AudioStreaming
from octopus_sensing.devices import BrainFlowOpenBCIStreaming
from octopus_sensing.devices import Shimmer3Streaming
from octopus_sensing_sara.sensing_module.get_devices_id import get_camera_path, get_audio_recorder_id
from octopus_sensing.devices import TestDeviceStreaming

class CameraStreaming(OriginalCameraStreaming):
    def _get_realtime_data(self, duration):
        print("new realtime data")
        return super()._get_realtime_data(5)

def define_sensors(output_path):

    #audio_recorder_id = get_audio_recorder_id()
    #if audio_recorder_id == -1:
    #    print("No audio recorder")
    #    raise Exception("No audio recorder")
    
    #print("audio recorder id", audio_recorder_id)
    #audio = AudioStreaming(audio_recorder_id, name="Audio", output_path=output_path)   
    
    main_camera = get_camera_path()
    print(main_camera)
    #camera = \
    #    CameraStreaming(name="camera",
    #                    output_path=output_path,
    #                    #camera_path="/dev/v4l/by-id/usb-Intel_R__RealSense_TM__Depth_Camera_415_Intel_R__RealSense_TM__Depth_Camera_415_837313021651-video-index0",
    #                    camera_path=main_camera,
    #                    image_width=640,
    #                    image_height=480)

    
    fake_device = TestDeviceStreaming(125, name="test_device", output_path=output_path)

    return [fake_device]
