''' Set default logging handler to avoid "No handler found" warnings. '''
import logging
from logging import NullHandler

from .watcher import Watcher

logging.getLogger(__name__).addHandler(NullHandler())
