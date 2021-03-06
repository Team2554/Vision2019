#!/usr/bin/env python3

# ---------------------------------------- #
#             Begin GRIP Pipeline          #
# ---------------------------------------- #


import cv2
import numpy
import math
from enum import Enum


class VisionPipeline:
    """
    An OpenCV pipeline generated by GRIP.
    """

    def __init__(self):
        """initializes all values to presets or None if need to be set
        """

        self.__rgb_threshold_red = [0.0, 58.01358234295414]
        self.__rgb_threshold_green = [139.88309352517987, 255.0]
        self.__rgb_threshold_blue = [139.88309352517987, 255.0]

        self.rgb_threshold_output = None

        self.__resize_image_input = self.rgb_threshold_output
        self.__resize_image_width = 320.0
        self.__resize_image_height = 240.0
        self.__resize_image_interpolation = cv2.INTER_CUBIC

        self.resize_image_output = None

        self.__find_contours_input = self.resize_image_output
        self.__find_contours_external_only = False

        self.find_contours_output = None

        self.__convex_hulls_contours = self.find_contours_output

        self.convex_hulls_output = None

    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step RGB_Threshold0:
        self.__rgb_threshold_input = source0
        (self.rgb_threshold_output) = self.__rgb_threshold(
            self.__rgb_threshold_input,
            self.__rgb_threshold_red,
            self.__rgb_threshold_green,
            self.__rgb_threshold_blue,
        )

        # Step Resize_Image0:
        self.__resize_image_input = self.rgb_threshold_output
        (self.resize_image_output) = self.__resize_image(
            self.__resize_image_input,
            self.__resize_image_width,
            self.__resize_image_height,
            self.__resize_image_interpolation,
        )

        # Step Find_Contours0:
        self.__find_contours_input = self.resize_image_output
        (self.find_contours_output) = self.__find_contours(
            self.__find_contours_input, self.__find_contours_external_only
        )

        # Step Convex_Hulls0:
        self.__convex_hulls_contours = self.find_contours_output
        (self.convex_hulls_output) = self.__convex_hulls(self.__convex_hulls_contours)

    @staticmethod
    def __rgb_threshold(input, red, green, blue):
        """Segment an image based on color ranges.
        Args:
            input: A BGR numpy.ndarray.
            red: A list of two numbers the are the min and max red.
            green: A list of two numbers the are the min and max green.
            blue: A list of two numbers the are the min and max blue.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2RGB)
        return cv2.inRange(
            out, (red[0], green[0], blue[0]), (red[1], green[1], blue[1])
        )

    @staticmethod
    def __resize_image(input, width, height, interpolation):
        """Scales and image to an exact size.
        Args:
            input: A numpy.ndarray.
            Width: The desired width in pixels.
            Height: The desired height in pixels.
            interpolation: Opencv enum for the type fo interpolation.
        Returns:
            A numpy.ndarray of the new size.
        """
        return cv2.resize(input, ((int)(width), (int)(height)), 0, 0, interpolation)

    @staticmethod
    def __find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if external_only:
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        im2, contours, hierarchy = cv2.findContours(input, mode=mode, method=method)
        return contours

    @staticmethod
    def __convex_hulls(input_contours):
        """Computes the convex hulls of contours.
        Args:
            input_contours: A list of numpy.ndarray that each represent a contour.
        Returns:
            A list of numpy.ndarray that each represent a contour.
        """
        output = []
        for contour in input_contours:
            output.append(cv2.convexHull(contour))
        return output


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
config_json = '{ "fps": 30, "height": 480, "pixel format": "mjpeg", "properties": [ { "name": "connect_verbose", "value": 1 }, { "name": "raw_brightness", "value": 135 }, { "name": "brightness", "value": 53 }, { "name": "raw_contrast", "value": 81 }, { "name": "contrast", "value": 32 }, { "name": "raw_saturation", "value": 132 }, { "name": "saturation", "value": 52 }, { "name": "white_balance_temperature_auto", "value": false }, { "name": "raw_gain", "value": 40 }, { "name": "gain", "value": 16 }, { "name": "power_line_frequency", "value": 2 }, { "name": "white_balance_temperature", "value": 6500 }, { "name": "raw_sharpness", "value": 20 }, { "name": "sharpness", "value": 8 }, { "name": "backlight_compensation", "value": 1 }, { "name": "exposure_auto", "value": 1 }, { "name": "raw_exposure_absolute", "value": 23 }, { "name": "exposure_absolute", "value": 1 }, { "name": "exposure_auto_priority", "value": true }, { "name": "pan_absolute", "value": 0 }, { "name": "tilt_absolute", "value": 0 }, { "name": "focus_absolute", "value": 51 }, { "name": "focus_auto", "value": true }, { "name": "zoom_absolute", "value": 1 } ], "width": 640 }'


class CameraConfig:
    pass


team = 2554
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
    camera = UsbCamera(config.name, config.path)

    server = inst.startAutomaticCapture(camera=camera, return_server=True)

    # camera.setConfigJson(json.dumps(config.config))
    camera.setConfigJson(config_json)
    camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

    return inst, camera, server


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

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240

HFOV = 65.8725303703

DEG_PER_PIXEL = HFOV / IMAGE_WIDTH

CENTER_WIDTH_PIXEL = (IMAGE_WIDTH - 1) // 2
CENTER_HEIGHT_PIXEL = (IMAGE_HEIGHT - 1) // 2

# ---------------------------------------- #
#          Begin OpenCV Processing         #
# ---------------------------------------- #


def processOpenCV(img, contours):
    new_image = img.copy()

    # The following code is Sagar's not mine
    angle = "-420 haha gotem"  # if there is no angle. Arnav please don't delete.
    center1 = (21, 69)
    center2 = (420, 666)
    center_of_centers = ("hi neeraj good job driving", "lmao please don't roast me")
    # End Sagar's attempt at humor

    target_exists = False

    # Draw the center of the image
    center_of_image = (CENTER_WIDTH_PIXEL, CENTER_HEIGHT_PIXEL)
    cv2.circle(
        img=new_image, center=center_of_image, radius=5, color=(255, 0, 0), thickness=-1
    )

    if len(contours) >= 2:
        target_exists = True

        # Sort to get the two biggest contours
        cnts = list(sorted(contours, key=cv2.contourArea))
        cnt1 = cnts[-1]
        cnt2 = cnts[-2]

        # Draw only these these two contours
        cv2.drawContours(
            image=new_image,
            contours=[cnt1, cnt2],
            contourIdx=-1,
            color=(0, 0, 255),
            thickness=3,
        )

        # Draw the centers of the two contours
        M1 = cv2.moments(cnt1)
        M2 = cv2.moments(cnt2)

        center1 = (int(M1["m10"] / M1["m00"]), int(M1["m01"] / M1["m00"]))
        center2 = (int(M2["m10"] / M2["m00"]), int(M2["m01"] / M2["m00"]))

        cv2.circle(
            img=new_image, center=center1, radius=5, color=(0, 0, 255), thickness=-1
        )
        cv2.circle(
            img=new_image, center=center2, radius=5, color=(0, 0, 255), thickness=-1
        )

        # Draw the midpoint of both of these contours
        center_of_centers = (
            int((center1[0] + center2[0]) / 2),
            int((center1[1] + center2[1]) / 2),
        )
        cv2.circle(
            img=new_image,
            center=center_of_centers,
            radius=5,
            color=(0, 0, 255),
            thickness=-1,
        )

        # Determine and write the angle from the center of the image
        # to the center of the centers
        angle = (center_of_centers[0] - CENTER_WIDTH_PIXEL) * DEG_PER_PIXEL

        cv2.putText(
            new_image,
            str(round(angle, 2)) + " deg",
            (0, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color=(0, 0, 255),
            thickness=2,
        )

        # Draw a line from the center of image to the center of centers
        cv2.line(new_image, center_of_centers, center_of_image, (255, 0, 0), 3)

    shuffleboard_data = {
        "target_exists": target_exists,
        "center1": center1,
        "center2": center2,
        "midpoint": center_of_centers,
        "yaw_angle": angle,
    }

    return new_image, shuffleboard_data


# ---------------------------------------- #
#           End OpenCV Processing          #
# ---------------------------------------- #


def main():
    global configFile

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

    print("Initialized vision stuff")

    for cameraConfig in cameraConfigs:
        # cameras.append(startCamera(cameraConfig))
        cs, cameraCapture, _ = startCamera(cameraConfig)
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
        print("Setting up NetworkTables client for team {}".format(team))
        ninst.startClientTeam(team)

    network_table = ninst.getTable("Shuffleboard").getSubTable("Vision")
    network_table.getEntry("connected").setValue(True)

    time.sleep(0.1)

    while True:
        timestamp, img = cvSink.grabFrame(img)
        frame = img

        if timestamp == 0:
            outputStream.notifyError(cvSink.getError())
            continue

        # grip.process(frame)
        # new_image, shuffleboard_data = processOpenCV(frame, grip.convex_hulls_output)

        # for name, data in shuffleboard_data.items():
        #    network_table.getEntry(name).setValue(data)

        # outputStream.putFrame(new_image)


if __name__ == "__main__":
    main()

# ---------------------------------------- #
#             End Our Code                 #
# ---------------------------------------- #
