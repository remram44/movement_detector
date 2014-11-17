from flask import Flask, render_template
from flask.globals import request
from sqlalchemy.orm.exc import NoResultFound

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
                                      .one())
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


@app.route('/image')
def show_image():
    """Image page: show the image from the webcam, with detected motion.
    """
    sqlsession = Session()
    try:
        if 'date' in request.form:
            date = request.form.get('date')
            detection = (sqlsession.query(models.Detection)
                                   .filter(models.Detection.date == date)
                                   .one())
        else:
            detection = (sqlsession.query(models.Detection)
                                   .order_by(models.Detection.id.desc())
                                   .one())
    except NoResultFound:
        return render_template('image.html'), 404
    else:
        return render_template('image.html',
                               detection=detection)


if __name__ == '__main__':
    app.run(debug=True)
