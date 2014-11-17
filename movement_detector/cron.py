import cv2
from datetime import datetime, timedelta
import logging
import os

from movement_detector import config, detector, models
from movement_detector.storage import Session


logger = logging.getLogger('movement_detector.cron')


def main():
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.INFO)

    sqlsession = Session()
    now = datetime.utcnow()
    logger.info("Detector running, current date: %s", now)

    # Find two previous frames in the last 20 minutes, for comparison
    from_time = now - timedelta(minutes=20)
    prev_frames = (sqlsession.query(models.Detection)
                             .filter(models.Detection.date > from_time)
                             .order_by(models.Detection.id.desc())
                             .limit(2)
                             .all())
    logger.info("Found %d previous frames for comparison",
                len(prev_frames))
    prev_frames = [cv2.imread(os.path.join(config.IMAGE_DIRECTORY,
                                           detection.image))
                   for detection in prev_frames]

    logger.info("Running detector")
    capture = detector.FrameGrabber(config.CAPTURE_DEVICE)
    changes, deviation, image, location = detector.detect(capture, prev_frames)
    capture.close()

    if changes is None:
        logger.warning("Detector didn't run, storing image")
    else:
        logger.info("Detector reports changes=%r, deviation=%r",
                    changes, deviation)

    imagefile = '%s.png' % now.strftime("%Y-%m-%d_%H-%M-%S")
    cv2.imwrite(os.path.join(config.IMAGE_DIRECTORY, imagefile),
                image)
    logger.info("Wrote %s", imagefile)
    if location is not None:
        location = ';'.join('%d' % l for l in location)
    detection = models.Detection(date=now,
                                 deviation=deviation,
                                 changes=changes,
                                 image=imagefile,
                                 location=location)
    sqlsession.add(detection)
    sqlsession.commit()
    logger.info("Saved detection #%d", detection.id)


if __name__ == '__main__':
    main()
