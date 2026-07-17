import logging
from wvs.core.logger import get_logger

def test_log_level_filtering(capsys):
    logger = get_logger("test_logger", level=logging.WARNING)
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    captured = capsys.readouterr()
    
    assert "Debug message" not in captured.out
    assert "Info message" not in captured.out
    assert "Warning message" in captured.out
    assert "Error message" in captured.out
