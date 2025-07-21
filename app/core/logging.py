import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    """Setup logging configuration for the application"""
    # Create the logs directory if it does not exist
    os.makedirs("logs", exist_ok=True)
    
    # Formatter for logs
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s:%(lineno)d: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        "logs/vod-service.log", 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Root logger
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    
    # Disable some noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("motor").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def get_logger(name: str = None):
    """Get logger instance"""
    return logging.getLogger(name or __name__)