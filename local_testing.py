from GRIP_Files.ok_maybe_now import VisionPipeline

import cv2
from math import tan, sqrt


IMAGE_WIDTH = 320
IMAGE_HEIGHT = 240

HFOV = 65.8725303703

DEG_PER_PIXEL = HFOV / IMAGE_WIDTH

CENTER_WIDTH_PIXEL = (IMAGE_WIDTH - 1) // 2
CENTER_HEIGHT_PIXEL = (IMAGE_HEIGHT - 1) // 2


def detectCentersAndAngles(img, contours):
    new_image = img.copy()
    angle = -1

    # Draw the center of the image
    center_of_image = (CENTER_WIDTH_PIXEL, CENTER_HEIGHT_PIXEL)
    cv2.circle(
        img=new_image, center=center_of_image, radius=5, color=(255, 0, 0), thickness=-1
    )

    if len(contours) >= 2:
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

    return new_image, angle


def main():
    cap = cv2.VideoCapture("http://frcvision.local:1181/stream.mjpg")

    pipeline = VisionPipeline()

    while True:
        try:
            ret, img = cap.read()

            pipeline.process(img)
            contours = pipeline.convex_hulls_output

            img = cv2.resize(img, (320, 240), 0, 0, cv2.INTER_CUBIC)

            img, angle = detectCentersAndAngles(img, contours)

            cv2.imshow("image", img)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        except ex:
            print(ex)


if __name__ == "__main__":
    main()
