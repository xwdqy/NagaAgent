import logging
import colorlog

formatter = colorlog.ColoredFormatter(
    "[%(asctime)s]%(log_color)s%(levelname)s: %(message)s",
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    },
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler = colorlog.StreamHandler()
handler.setFormatter(formatter)

logger = colorlog.getLogger("colored_logger")
logger.addHandler(handler)
logger.setLevel(logging.INFO)