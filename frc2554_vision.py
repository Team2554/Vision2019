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

        self.__resize_image_width = 320.0
        self.__resize_image_height = 180.0
        self.__resize_image_interpolation = cv2.INTER_CUBIC

        self.resize_image_output = None

        self.__blur_input = self.resize_image_output
        self.__blur_type = BlurType.Gaussian_Blur
        self.__blur_radius = 4.716981132075471

        self.blur_output = None

        self.__rgb_threshold_input = self.blur_output
        self.__rgb_threshold_red = [205, 255.0]
        self.__rgb_threshold_green = [205, 255.0]
        self.__rgb_threshold_blue = [205, 255.0]

        self.rgb_threshold_output = None

        self.__find_contours_input = self.rgb_threshold_output
        self.__find_contours_external_only = False

        self.find_contours_output = None

        self.__convex_hulls_contours = self.find_contours_output

        self.convex_hulls_output = None

        self.__filter_contours_contours = self.convex_hulls_output
        self.__filter_contours_min_area = 100.0
        self.__filter_contours_min_perimeter = 0.0
        self.__filter_contours_min_width = 0.0
        self.__filter_contours_max_width = 1000.0
        self.__filter_contours_min_height = 0.0
        self.__filter_contours_max_height = 1000.0
        self.__filter_contours_solidity = [0, 100]
        self.__filter_contours_max_vertices = 1000000.0
        self.__filter_contours_min_vertices = 0.0
        self.__filter_contours_min_ratio = 0.0
        self.__filter_contours_max_ratio = 1000.0

        self.filter_contours_output = None

    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step Resize_Image0:
        self.__resize_image_input = source0
        (self.resize_image_output) = self.__resize_image(
            self.__resize_image_input,
            self.__resize_image_width,
            self.__resize_image_height,
            self.__resize_image_interpolation,
        )

        # Step Blur0:
        self.__blur_input = self.resize_image_output
        (self.blur_output) = self.__blur(
            self.__blur_input, self.__blur_type, self.__blur_radius
        )

        # Step RGB_Threshold0:
        self.__rgb_threshold_input = self.blur_output
        (self.rgb_threshold_output) = self.__rgb_threshold(
            self.__rgb_threshold_input,
            self.__rgb_threshold_red,
            self.__rgb_threshold_green,
            self.__rgb_threshold_blue,
        )

        # Step Find_Contours0:
        self.__find_contours_input = self.rgb_threshold_output
        (self.find_contours_output) = self.__find_contours(
            self.__find_contours_input, self.__find_contours_external_only
        )

        # Step Convex_Hulls0:
        self.__convex_hulls_contours = self.find_contours_output
        (self.convex_hulls_output) = self.__convex_hulls(self.__convex_hulls_contours)

        # Step Filter_Contours0:
        self.__filter_contours_contours = self.convex_hulls_output
        (self.filter_contours_output) = self.__filter_contours(
            self.__filter_contours_contours,
            self.__filter_contours_min_area,
            self.__filter_contours_min_perimeter,
            self.__filter_contours_min_width,
            self.__filter_contours_max_width,
            self.__filter_contours_min_height,
            self.__filter_contours_max_height,
            self.__filter_contours_solidity,
            self.__filter_contours_max_vertices,
            self.__filter_contours_min_vertices,
            self.__filter_contours_min_ratio,
            self.__filter_contours_max_ratio,
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
    def __blur(src, type, radius):
        """Softens an image using one of several filters.
        Args:
            src: The source mat (numpy.ndarray).
            type: The blurType to perform represented as an int.
            radius: The radius for the blur as a float.
        Returns:
            A numpy.ndarray that has been blurred.
        """
        if type is BlurType.Box_Blur:
            ksize = int(2 * round(radius) + 1)
            return cv2.blur(src, (ksize, ksize))
        elif type is BlurType.Gaussian_Blur:
            ksize = int(6 * round(radius) + 1)
            return cv2.GaussianBlur(src, (ksize, ksize), round(radius))
        elif type is BlurType.Median_Filter:
            ksize = int(2 * round(radius) + 1)
            return cv2.medianBlur(src, ksize)
        else:
            return cv2.bilateralFilter(src, -1, round(radius), round(radius))

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

    @staticmethod
    def __filter_contours(
        input_contours,
        min_area,
        min_perimeter,
        min_width,
        max_width,
        min_height,
        max_height,
        solidity,
        max_vertex_count,
        min_vertex_count,
        min_ratio,
        max_ratio,
    ):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
        output = []
        for contour in input_contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w < min_width or w > max_width:
                continue
            if h < min_height or h > max_height:
                continue
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            if cv2.arcLength(contour, True) < min_perimeter:
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if solid < solidity[0] or solid > solidity[1]:
                continue
            if len(contour) < min_vertex_count or len(contour) > max_vertex_count:
                continue
            ratio = (float)(w) / h
            if ratio < min_ratio or ratio > max_ratio:
                continue
            output.append(contour)
        return output


BlurType = Enum("BlurType", "Box_Blur Gaussian_Blur Median_Filter Bilateral_Filter")

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

FOV = 78
IMG_WIDTH = 320
DEG_PER_PIXEL = FOV / IMG_WIDTH
IMG_CENTER = (IMG_WIDTH - 1) // 2

# ---------------------------------------- #
#          Begin OpenCV Processing         #
# ---------------------------------------- #


def processOpenCV(contours):
    cnts = list(sorted(contours, key=lambda x: cv2.contourArea(x)))
    cnt1 = cnts[-1]
    cnt2 = cnts[-2]

    M1 = cv2.moments(cnt1)
    M2 = cv2.moments(cnt2)

    center1 = (int(M1["m10"] / M1["m00"]), int(M1["m01"] / M1["m00"]))
    center2 = (int(M2["m10"] / M2["m00"]), int(M2["m01"] / M2["m00"]))

    midpoint = ((center1[0] + center2[0]) / 2, (center1[1] + center2[1]) / 2)

    yawAngle = (midpoint[0] - IMG_CENTER) * DEG_PER_PIXEL

    output = {
        "center1": center1,
        "center2": center2,
        "midpoint": midpoint,
        "yaw_angle": yawAngle,
    }

    return output


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
        processedData = processOpenCV(grip.filter_contours_output)
        for name, data in processedData.items():
            network_table.getEntry(name).setValue(data)

        outputStream.putFrame(frame.copy())


if __name__ == "__main__":
    main()

# ---------------------------------------- #
#             End Our Code                 #
# ---------------------------------------- #
