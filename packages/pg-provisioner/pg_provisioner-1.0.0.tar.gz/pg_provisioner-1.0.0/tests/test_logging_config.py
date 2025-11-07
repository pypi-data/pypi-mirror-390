import logging
from logging_config import get_logger, set_global_log_level

def test_get_logger_and_log_levels(tmp_path):
    logger = get_logger("pgtest", level="DEBUG", log_to_file=True)
    logger.debug("debug msg")
    assert isinstance(logger, logging.Logger)
    set_global_log_level("INFO")
    assert logger.level == logging.INFO
