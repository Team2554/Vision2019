import cv2

# FIXME: arbitrary video loop
class App:
    """Represents main application class"""

    def __init__(self):
        """Initialize cameras"""

        self._cameras = []

        for i in range(4):
            self._cameras.append(cv2.VideoCapture(i))

    def run(self):
        """Run the application code"""

        while True:
            pass


if __name__ == "__main__":
    App().run()
