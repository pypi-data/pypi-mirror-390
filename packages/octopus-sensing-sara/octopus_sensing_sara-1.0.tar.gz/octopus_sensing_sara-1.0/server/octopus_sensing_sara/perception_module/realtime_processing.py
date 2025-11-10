# This file is part of Octopus Sensing SARA <https://octopus-sensing.nastaran-saffar.me/>
# Copyright © 2022 Nastaran Saffaryazdi <nsaffar@gmail.com>
#
# Octopus Sensing SARA is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Octopus Sensing SARA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with Octopus Sensing
# SARA. If not, see <https://www.gnu.org/licenses/>.

import time
import http
import json
import threading
import msgpack
from typing import Optional
import http.client
import threading
from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import uvicorn

class ProcessingController(threading.Thread):
    '''
    It 
    1- Receives the neurophysiological result from octopus-sensing-processing
    2- Send triggers to octopus sensing
    3- Doing sentiment analysis
    4- Decision making and creating prompt
    '''
    def __init__(self, session_id: str, chunk_time: int=3) -> None:
        super().__init__()
        self._chunk_time = chunk_time
        self._processing_client = \
            http.client.HTTPConnection(f'{os.environ.get("SENSING_ADDRESS")}:{os.environ.get("SENSING_PORT", 9331)}',
                                       timeout=10)
        self._acquisition_client = \
            http.client.HTTPConnection(f'{os.environ.get("PROCESSING_ADDRESS")}:{os.environ.get("PROCESSING_PORT", 9332)}',
                                       )
        self._processing_flag: Optional[str] = None
        self._stimuli_id = 0
        self._session_id = session_id
        self._processing_result: list[dict] = []
    
    def start_processing(self, stimuli_id: Optional[int] = None):
        if stimuli_id is None:
            self._stimuli_id +=1
        self._processing_flag = "START"
            
    def get_processing_result(self, user_message: str = ""):
        result = self._processing_result
        # todo: process user message in another thread and append the processing result to this result
        def process_message(message: str):
            # Simulate processing (replace with actual logic)
            time.sleep(1)  # mimic delay
            processed = {"text_emotion": "happiness"}
            result.append(processed)
        # Start message processing in a separate thread
        threading.Thread(target=process_message, args=(user_message,), daemon=True).start()

        self._processing_flag = "STOP"
        return result

    def terminate(self):
        self._processing_flag = "TERMINATE"


    def run(self):
        while True:
            if self._processing_flag is None:
                continue
            elif self._processing_flag is "TERMINATE":
                self._processing_client.close()
                self._acquisition_client.close()
                break
            
            elif self._processing_flag is "START":
                self._acquisition_client.request("POST", "/",
                            body=msgpack.packb({'type': 'START',
                                                'experiment_id': self._session_id,
                                                'stimulus_id': self._stimuli_id}),
                            headers={'Accept': 'application/msgpack'})
                self._processing_client.request("GET", "/get_processing_result")
                response = self._processing_client.getresponse()
                new_state = response.read()
                self._processing_result.append(json.loads(new_state.decode('utf-8')))
                self._processing_result.append(1)
                self.__wait_or_stop()

            elif self._processing_flag is "STOP":
                self._acquisition_client.request("POST", "/",
                            body=msgpack.packb({'type': 'STOP',
                                                'experiment_id': self._session_id,
                                                'stimulus_id': self._stimuli_id}),
                            headers={'Accept': 'application/msgpack'})
                self._processing_result = []
                self._processing_flag = None

            
    def __wait_or_stop(self):
        start_time = time.time()
        while time.time() - start_time < self._chunk_time:
            if self._processing_flag in ["Stop", "TERMINATE"]:
                print("Flag received! Continuing early...")
                return
            time.sleep(0.1)  # Check every 100ms


def realtime_perception():
    # --- Controller setup ---
    controller = ProcessingController(session_id="exp001")
    controller.start()

    # --- FastAPI app ---
    app = FastAPI()

    # --- Request models ---
    class StartRequest(BaseModel):
        stimuli_id: int

    class ResultRequest(BaseModel):
        user_message: str

    # --- Endpoints ---
    @app.post("/start")
    async def start(req: StartRequest):
        controller.start_processing(req.stimuli_id)
        return {"status": "processing started", "stimuli_id": controller._stimuli_id}

    @app.post("/get_result")
    async def get_result(req: ResultRequest):
        result = controller.get_processing_result(req.user_message)
        return {"result": result}

    @app.post("/terminate")
    async def terminate():
        controller.terminate()
        return {"status": "terminated"}

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("FUSION_PORT", 9333)))


'''
How to use:
python real_time_processing.py

import requests

# Start processing
requests.post("http://localhost:8080/start", json={"stimuli_id": 42})

# Get result
r = requests.post("http://localhost:8080/result", json={"user_message": "Hello"})
print(r.json())

# Terminate
requests.post("http://localhost:8080/terminate")

'''