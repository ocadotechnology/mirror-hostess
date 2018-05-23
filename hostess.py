#!/usr/bin/env python
import time
import logging
import logging.config
from logging import StreamHandler
import os
import sys

import hostess
from kubernetes import config
from kubernetes.config import ConfigException
from kubernetes.client import configuration

LOGGER = logging.getLogger(__name__)

class RFC3339Formatter(logging.Formatter):
    ''' https://docs.python.org/3.5/howto/logging-cookbook.html#formatting-times-using-utc-gmt-via-configuration 
        https://github.com/python/cpython/blob/6f0eb93183519024cb360162bdd81b9faec97ba6/Lib/logging/__init__.py#L426 '''
    converter = time.gmtime
    default_time_format = '%Y-%m-%dT%H:%M:%S'
    default_msec_format = '%s.%03dZ' # hacky adding of timezone to end of string 

def main():
    level_str = os.getenv('LOG_LEVEL', 'WARNING').upper()
    format_str = os.getenv('LOG_FORMAT', '%(asctime)s [%(levelname)s] %(message)s')
    console = logging.StreamHandler()
    console.setFormatter(RFC3339Formatter(format_str))
    LOGGER.addHandler(console)
    sleep_time = os.environ.get("SECONDS_BETWEEN_STREAMS", '30')
    sleep_time = int(sleep_time)
    try:
        logging.basicConfig(level=logging.getLevelName(level_str))
    except ValueError as err:
        LOGGER.error(err)
        sys.exit(1)

    try:
        config.load_kube_config()
    except (FileNotFoundError, ConfigException) as err:
        LOGGER.debug("Not able to use Kubeconfig: %s", err)
        try:
            config.load_incluster_config()
        except (FileNotFoundError, ConfigException) as err:
            LOGGER.error("Not able to use in-cluster config: %s", err)
            sys.exit(1)
        
    try:
        while True:
            hostess.Watcher(env=os.environ, config=configuration).execute()
            LOGGER.info("API closed connection, sleeping for %i seconds", sleep_time)
            time.sleep(sleep_time)
    except RuntimeError as err:
        LOGGER.exception(err)
        sys.exit(1)

if __name__ == '__main__':
    main()
