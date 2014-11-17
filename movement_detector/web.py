import cv2
from flask import Flask, render_template, send_file
from flask.globals import request
import io
import os
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import abort

from movement_detector import config, models
from movement_detector.storage import Session


app = Flask('movement_detector')
app.config.update(config.__dict__)


@app.route('/')
def index():
    """Landing page: show if movement is happening.
    """
    sqlsession = Session()
    try:
        latest_detection = (sqlsession.query(models.Detection)
                                      .order_by(models.Detection.id.desc())
                                      .first())
    except NoResultFound:
        movement = False
    else:
        movement = latest_detection.changes > 5

    return render_template('index.html',
                           movement=movement)


@app.route('/history')
def history():
    """History page: show movement graphs.
    """
    todo


@app.route('/detection')
def show_detection():
    """Image page: show the image from the webcam, with detected motion.
    """
    sqlsession = Session()
    try:
        if 'id' in request.args:
            detection_id = int(request.args.get('id'))
            detection = (sqlsession.query(models.Detection)
                                   .filter(models.Detection.id == detection_id)
                                   .one())
        else:
            detection = (sqlsession.query(models.Detection)
                                   .order_by(models.Detection.id.desc())
                                   .first())
    except NoResultFound:
        return render_template('detection.html'), 404
    else:
        return render_template('detection.html',
                               detection=detection)


@app.route('/images/<int:detection_id>')
def generate_image(detection_id):
    """Image page: show the image from the webcam, with detected motion.
    """
    sqlsession = Session()
    try:
        detection = (sqlsession.query(models.Detection)
                               .filter(models.Detection.id == detection_id)
                               .one())
    except NoResultFound:
        abort(404)
    else:
        image = cv2.imread(os.path.join(config.IMAGE_DIRECTORY,
                                        detection.image))
        if detection.location is not None:
            location = tuple(int(c) for c in detection.location.split(';'))
            cv2.rectangle(image,
                          location[0:2], location[2:4],
                          (0, 0, 255), 5)
        ret, imagedata = cv2.imencode('.png', image)
        assert ret
        return send_file(io.BytesIO(imagedata), 'image/png')


if __name__ == '__main__':
    app.run(debug=True)
