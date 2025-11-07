import logging
from elasticapm.handlers.logging import LoggingHandler

from .apm import apm

logger = logging.getLogger('elasticapm')
logger.setLevel(logging.ERROR)
logger.addHandler(LoggingHandler(client=apm))
