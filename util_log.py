import logging
import logging.handlers


def creater_logger(name, logfile):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.handlers.RotatingFileHandler(
        logfile,
        maxBytes=100 * 1024 * 1024,
        backupCount=10,
    )
    formatter_str = '[%(asctime)s] [%(levelname)s] [%(process)d]' + \
                    ' [%(name)s] [%(funcName)s:%(lineno)d] %(message)s'
    formatter = logging.Formatter(formatter_str)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
