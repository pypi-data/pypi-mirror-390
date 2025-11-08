import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

class Logger:
    _instances = {}
    
    def __init__(self, logs_path: str, name: str = 'RPA_Logger', level: str = 'INFO'):
        self.logs_path = logs_path
        self.name = name
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel(level=level)
        
        # Formato padrão
        formatter = logging.Formatter(
            '%(module)s [%(levelname)s] [%(asctime)s]: %(message)s'
        )

        # File Handler com rotação
        log_file = Path(logs_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # Adicionar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    @classmethod
    def get_logger(cls, logs_path: str, name: str = 'RPA_Logger', level: str = 'INFO') -> logging.Logger:
        _instance = cls._instances.get(logs_path, None)
        if not _instance:
            cls._instances[logs_path] = cls(logs_path, name, level)
            
        return cls._instances.get(logs_path).logger