import logging
import os
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler


@dataclass()
class IdentifierDistributionConfiguration:

    FLIGHT_STATE: bool = True  # 5.1
    FLIGHT_CONTROLS: bool = True  # 5.2
    AIRCRAFT_ENGINE: bool = True  # 5.3
    POWER_TRANSMISSION: bool = True  # 5.4
    HYDRAULIC_SYSTEMS: bool = True  # 5.5
    ELECTRIC_SYSTEM: bool = True  # 5.6
    NAVIGATION_SYSTEM: bool = True  # 5.7
    LANDING_GEAR: bool = True  # 5.8
    MISCELLANEOUS: bool = True  # 5.9
    #  RESERVED: bool = False  # 5.10 NOT YET SUPPORTED


identifier_distribution_configuration = IdentifierDistributionConfiguration()


class Logging:
    def __init__(self, log_dir="logs", exist_ok=True, **kwargs):
        self.format = '%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
        self.date_format = '%Y-%m-%d %H:%M:%S'
        os.makedirs(log_dir, exist_ok=exist_ok)

    def create_handler(self, log_file, max_bytes=1_000_000, backup_count=3):
        formatter = logging.Formatter(
            fmt=self.format, datefmt=self.date_format)
        handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count)
        handler.setFormatter(formatter)
        return handler

    @staticmethod
    def create_logger(name, level=logging.INFO):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        return logger

    def create_and_setup_logger(self, name, log_file, level=logging.INFO, max_bytes=1_000_000, backup_count=3):
        """Setup the logger with rotating file handler using native python's logging module."""

        handler = self.create_handler(log_file, max_bytes, backup_count)
        logger = self.create_logger(name, level)
        logger.addHandler(handler)
        # Add a message to denote the initialize parameters of the log file
        logger.debug(
            f'Initialized \
            {name} on {log_file}, \
            max_bytes={max_bytes}, \
            backup_count={backup_count}, \
            with level {get_level_from_int(level)}')
        return logger


log_obj = Logging()


def get_level_from_config(log_level_name=logging.INFO) -> int:
    match log_level_name:
        case 'debug':
            return logging.DEBUG
        case 'info':
            return logging.INFO
        case 'warning':
            return logging.WARNING
        case 'error':
            return logging.ERROR
        case 'critical':
            return logging.CRITICAL
        case _:
            return logging.NOTSET


def get_level_from_int(level: int) -> str:
    match level:
        case 10:
            return 'debug'
        case 20:
            return 'info'
        case 30:
            return 'warning'
        case 40:
            return 'error'
        case 50:
            return 'critical'
        case _:
            return 'notset'


canaerospace_logger = log_obj.create_and_setup_logger(
    "CANAerospace", "logs/canaerospace.log", level=logging.DEBUG)
