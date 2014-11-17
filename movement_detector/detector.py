import cv2
import numpy


class FrameGrabber(object):
    def __init__(self, device=0, keep_open=False):
        self._device = device
        self._keep_open = keep_open
        self._capture = cv2.VideoCapture()
        if self._keep_open:
            self._capture.open(self._device)

    def grab_frame(self):
        if self._keep_open:
            grabbed, frame = self._capture.read()
        else:
            self._capture.open(self._device)
            grabbed, frame = self._capture.read()
            self._capture.release()
        assert grabbed
        return frame

    def close(self):
        if self._keep_open:
            self._capture.release()


def detect_motion(motion, max_deviation):
    mean, std_dev = cv2.meanStdDev(motion)
    std_dev = std_dev[0, 0]
    if std_dev > max_deviation:
        return 0, None, std_dev

    where = numpy.argwhere(motion == 255)
    number_of_changes = len(where)
    if number_of_changes:
        (min_y, min_x), (max_y, max_x) = where.min(0), where.max(0)
        return number_of_changes, (min_x, min_y, max_x, max_y), std_dev
    else:
        return number_of_changes, None, std_dev


kernel_ero = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))


def detect(capture, prev_images):
    # Capture a new frame
    new_frame = capture.grab_frame()

    # Not enough frames: no detection, just store this one
    if len(prev_images) < 2:
        return None, None, new_frame, None

    # Everything to grayscale
    prev_images = [prev_images[1], prev_images[0], new_frame]
    prev_images = [cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                   for prev_frame in prev_images]
    prev_frame, current_frame, next_frame = prev_images

    # Diff
    d1 = cv2.absdiff(prev_frame, next_frame)
    d2 = cv2.absdiff(next_frame, current_frame)
    motion = cv2.bitwise_and(d1, d2)

    # Threshold & erode
    cv2.threshold(motion, 35, 255, cv2.THRESH_BINARY, dst=motion)
    cv2.erode(motion, kernel_ero, dst=motion)

    # Find and count changes
    number_of_changes, location, std_dev = detect_motion(motion, 60)
    if number_of_changes < 5:
        location = None

    return number_of_changes, std_dev, new_frame, location


def debug():
    camera = FrameGrabber(keep_open=True)

    prev_frames = []

    while True:
        changes, deviation, image, location = detect(camera, prev_frames)
        display_image = image.copy()
        if location is not None:
            cv2.rectangle(display_image,
                          location[0:2], location[2:4],
                          (0, 0, 255), 5)
        cv2.putText(display_image,
                    "Deviation: %r" % deviation,
                    (5, 20), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255))
        cv2.putText(display_image,
                    "Changes: %r" % changes,
                    (5, 30), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255))
        cv2.imshow("camera_movement", display_image)

        prev_frames.insert(0, image)
        prev_frames = prev_frames[:2]


if __name__ == '__main__':
    debug()
