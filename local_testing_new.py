from GRIP_Files.finalfourtwenty import VisionPipeline

import cv2
from math import tan, sqrt
import numpy as np

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240

HFOV = 65.8725303703

DEG_PER_PIXEL = HFOV / IMAGE_WIDTH

CENTER_WIDTH_PIXEL = (IMAGE_WIDTH - 1) // 2
CENTER_HEIGHT_PIXEL = (IMAGE_HEIGHT - 1) // 2


def getContourAngle(contour):
    rect = cv2.minAreaRect(contour)
    angle = rect[-1]

    return angle


def angleToTarget(img, contours):
    new_image = img.copy()
    angle = -420

    imgCenter = (CENTER_WIDTH_PIXEL, CENTER_HEIGHT_PIXEL)
    cv2.circle(
        img=new_image, center=(imgCenter), radius=3, color=(255, 0, 0), thickness=-1
    )

    if len(contours) >= 2:
        contours = list(sorted(contours, key=cv2.contourArea))[::-1]
        cntAngles = [getContourAngle(i) for i in contours]

        finalCnts = []
        baseAngle = -69

        for idx, i in enumerate(cntAngles):
            if idx == 0:
                finalCnts.append(contours[idx])
                baseAngle = i
            else:
                diff = abs(abs(i) - abs(baseAngle))
                if (diff - 80) < 20:
                    finalCnts.append(contours[idx])
                    break
        if not len(finalCnts) < 2:
            finalCnts = list(sorted(finalCnts, key=cv2.contourArea))[::-1]
            cnt1 = finalCnts[0]
            cnt2 = finalCnts[1]

            M1 = cv2.moments(cnt1)
            M2 = cv2.moments(cnt2)

            center1 = (int(M1["m10"] / M1["m00"]), int(M1["m01"] / M1["m00"]))
            center2 = (int(M2["m10"] / M2["m00"]), int(M2["m01"] / M2["m00"]))

            # cv2.circle(
            #     img=new_image, center=center1, radius=3, color=(0, 0, 255), thickness=-1
            # )
            # cv2.circle(
            #     img=new_image, center=center2, radius=3, color=(0, 0, 255), thickness=-1
            # )

            # Draw the midpoint of both of these contours
            targetCenter = (
                int((center1[0] + center2[0]) / 2),
                int((center1[1] + center2[1]) / 2),
            )
            cv2.circle(
                img=new_image,
                center=targetCenter,
                radius=3,
                color=(0, 0, 255),
                thickness=-1,
            )

            angle = (targetCenter[0] - CENTER_WIDTH_PIXEL) * DEG_PER_PIXEL
            cv2.putText(
                new_image,
                str(round(angle, 2)) + " deg",
                (0, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color=(0, 255, 255),
                thickness=2,
            )

            cv2.line(new_image, targetCenter, imgCenter, (255, 0, 0), 2)
    return new_image, angle


def main():
    cap = cv2.VideoCapture("http://frcvision.local:1181/stream.mjpg")
    pipeline = VisionPipeline()

    while True:
        try:
            ret, img = cap.read()

            pipeline.process(img)
            img = cv2.resize(img, (320, 240), 0, 0, cv2.INTER_CUBIC)
            img, angle = angleToTarget(img, pipeline.filter_contours_output)
            cv2.imshow("image", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        except Exception as e:
            print("A big gae occurred: ", e)


if __name__ == "__main__":
    main()
