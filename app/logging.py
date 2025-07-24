import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    log_level = logging.DEBUG if app.debug else logging.INFO

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Stream logs to console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)
    app.logger.addHandler(stream_handler)

    # Optional: Log to file with rotation
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(log_level)
    app.logger.info('Logging is set up.')