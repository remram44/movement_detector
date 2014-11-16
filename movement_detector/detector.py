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
    if std_dev[0] > max_deviation:
        return 0, None, std_dev[0]

    where = numpy.argwhere(motion == 255)
    print where
    number_of_changes = len(where)
    if number_of_changes:
        (min_y, min_x), (max_y, max_x) = where.min(0), where.max(0)
        return number_of_changes, (min_x, max_x, min_y, max_y), std_dev[0]
    else:
        return number_of_changes, None, std_dev[0]


current_frame = next_frame = None


def loop(capture, init=False, debug=False):
    global current_frame, next_frame

    # Initialize on first run
    if init or current_frame is None:
        next_frame = capture.grab_frame()
        next_frame = cv2.cvtColor(next_frame, cv2.COLOR_BGR2GRAY)

        current_frame = next_frame

    # Capture a new frame
    new_frame = capture.grab_frame()
    prev_frame, current_frame, next_frame = \
        current_frame, next_frame, cv2.cvtColor(new_frame, cv2.COLOR_BGR2GRAY)
    kernel_ero = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))

    # Diff
    d1 = cv2.absdiff(prev_frame, next_frame)
    d2 = cv2.absdiff(next_frame, current_frame)
    motion = cv2.bitwise_and(d1, d2)

    # Threshold & erode
    cv2.threshold(motion, 35, 255, cv2.THRESH_BINARY, dst=motion)
    cv2.erode(motion, kernel_ero, dst=motion)

    # Find and count changes
    number_of_changes, result, std_dev = detect_motion(motion, 60)

    print("Deviation: %r" % std_dev)
    if number_of_changes >= 5:
        cv2.rectangle(new_frame,
                      (result[0], result[2]), (result[1], result[3]),
                      (0, 0, 255), 5)
        print("Changes: %r" % number_of_changes)
        print(result)
    else:
        print("No changes: %r" % number_of_changes)

    if debug:
        import matplotlib.pyplot as plt
        plt.imshow(new_frame[:, :, (2, 1, 0)])
        plt.show()


if __name__ == '__main__':
    import time

    camera = FrameGrabber(keep_open=True)

    while True:
        loop(camera, debug=True)
        time.sleep(5)
