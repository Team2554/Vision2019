#!/usr/bin/env python3

# ---------------------------------------- #
#             Begin GRIP Pipeline          #
# ---------------------------------------- #

# Sagar put the GRIP pipeline code here
class VisionPipeline:
    pass


# ---------------------------------------- #
#             End GRIP Pipeline            #
# ---------------------------------------- #

# ---------------------------------------- #
#             Begin FRC Template           #
# ---------------------------------------- #

# ----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
# ----------------------------------------------------------------------------

import json
import time
import sys

from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer
from networktables import NetworkTablesInstance

#   JSON format:
#   {
#       "team": <team number>,
#       "ntmode": <"client" or "server", "client" if unspecified>
#       "cameras": [
#           {
#               "name": <camera name>
#               "path": <path, e.g. "/dev/video0">
#               "pixel format": <"MJPEG", "YUYV", etc>   // optional
#               "width": <video mode width>              // optional
#               "height": <video mode height>            // optional
#               "fps": <video mode fps>                  // optional
#               "brightness": <percentage brightness>    // optional
#               "white balance": <"auto", "hold", value> // optional
#               "exposure": <"auto", "hold", value>      // optional
#               "properties": [                          // optional
#                   {
#                       "name": <property name>
#                       "value": <property value>
#                   }
#               ],
#               "stream": {                              // optional
#                   "properties": [
#                       {
#                           "name": <stream property name>
#                           "value": <stream property value>
#                       }
#                   ]
#               }
#           }
#       ]
#   }

configFile = "/boot/frc.json"


class CameraConfig:
    pass


team = None
server = False
cameraConfigs = []

"""Report parse error."""


def parseError(str):
    print("config error in '" + configFile + "': " + str, file=sys.stderr)


"""Read single camera configuration."""


def readCameraConfig(config):
    cam = CameraConfig()

    # name
    try:
        cam.name = config["name"]
    except KeyError:
        parseError("could not read camera name")
        return False

    # path
    try:
        cam.path = config["path"]
    except KeyError:
        parseError("camera '{}': could not read path".format(cam.name))
        return False

    # stream properties
    cam.streamConfig = config.get("stream")

    cam.config = config

    cameraConfigs.append(cam)
    return True


"""Read configuration file."""


def readConfig():
    global team
    global server

    # parse file
    try:
        with open(configFile, "rt") as f:
            j = json.load(f)
    except OSError as err:
        print("could not open '{}': {}".format(configFile, err), file=sys.stderr)
        return False

    # top level must be an object
    if not isinstance(j, dict):
        parseError("must be JSON object")
        return False

    # team number
    try:
        team = j["team"]
    except KeyError:
        parseError("could not read team number")
        return False

    # ntmode (optional)
    if "ntmode" in j:
        str = j["ntmode"]
        if str.lower() == "client":
            server = False
        elif str.lower() == "server":
            server = True
        else:
            parseError("could not understand ntmode value '{}'".format(str))

    # cameras
    try:
        cameras = j["cameras"]
    except KeyError:
        parseError("could not read cameras")
        return False
    for camera in cameras:
        if not readCameraConfig(camera):
            return False

    return True


"""Start running the camera."""


def startCamera(config):
    print("Starting camera '{}' on {}".format(config.name, config.path))
    inst = CameraServer.getInstance()
    camera = inst.startAutomaticCapture(name=config.name, path=config.path)
    camera.setConfigJson(json.dumps(config.config))

    return inst, camera
    # camera = UsbCamera(config.name, config.path)
    # server = inst.startAutomaticCapture(camera=camera, return_server=True)

    # camera.setConfigJson(json.dumps(config.config))
    # camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

    # if config.streamConfig is not None:
    #     server.setConfigJson(json.dumps(config.streamConfig))

    # return camera


# ---------------------------------------- #
#             End FRC Template             #
# ---------------------------------------- #

# ---------------------------------------- #
#             Begin Our Code               #
# ---------------------------------------- #

import cv2
import numpy as np
import sys
import time


# ---------------------------------------- #
#          Begin OpenCV Processing         #
# ---------------------------------------- #


def processOpenCV(arguments, frame):
    pass


# ---------------------------------------- #
#           End OpenCV Processing          #
# ---------------------------------------- #


def main():
    if len(sys.argv) >= 2:
        configFile = sys.argv[1]

    if not readConfig():
        print("Unable to read config file!")
        sys.exit(1)

    # start cameras
    cameras = []
    streams = []

    image_width = 640
    image_height = 480

    grip = VisionPipeline()

    for cameraConfig in cameraConfigs:
        # cameras.append(startCamera(cameraConfig))
        cs, cameraCapture = startCamera(cameraConfig)
        streams.append(cs)
        cameras.append(cameraCapture)

    # First camera is server
    cameraServer = streams[0]

    # Set up a CV Sink to capture video
    cvSink = cameraServer.getVideo()

    # CvSource
    outputStream = cameraServer.putVideo("stream", image_width, image_height)

    img = np.zeros(shape=(image_height, image_width, 3), dtype=np.uint8)

    # Networktables
    ninst = NetworkTablesInstance.getDefault()
    if server:
        print("Setting up NetworkTables server")
        ninst.startServer()
    else:
        print("Setting up NetworkTables client")
        ninst.startClient()

    network_table = ninst.getTable("Shuffleboard").getSubTable("Vision")
    network_table.getEntry("connected").setValue(True)

    time.sleep(0.1)

    while True:
        timestamp, img = cvSink.grabFrame(img)
        frame = img

        if timestamp == 0:
            outputStream.notifyError(cvSink.getError())
            continue

        grip.process(frame)
        processed = processOpenCV([grip.filter_contours_output], frame)

        outputStream.putFrame(processed)


if __name__ == "__main__":
    main()

# ---------------------------------------- #
#             End Our Code                 #
# ---------------------------------------- #
