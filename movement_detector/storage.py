import logging
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

from movement_detector import config, models


# Setup SQLAlchemy
engine = create_engine(config.DATABASE_URI)
Session = sessionmaker(bind=engine)
if not engine.dialect.has_table(engine.connect(), 'threads'):
    logging.warning("Creating tables")
    models.Base.metadata.create_all(bind=engine)
