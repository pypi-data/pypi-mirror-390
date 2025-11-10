import logging
from logging.handlers import RotatingFileHandler
import os

'''
level: 日志级别
name: 模块名称
fmt: 日志格式
log_dir: 日志文件保存目录
log_file: 日志文件名
error_file: 错误日志文件名

'''
class BaseLogger:
    
    def __init__(self, **kwargs):
        self.logger = logging.getLogger(kwargs.get('name', 'baseLogger'))
        if not self.logger.handlers:
            self.logger.setLevel(kwargs.get('level', logging.DEBUG))
            formatter = self._create_formatter(kwargs.get('fmt', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self._ensure_log_dir_exists(kwargs.get('log_dir', 'logs'))
            self._set_main_file_handler(formatter=formatter, log_dir=kwargs.get('log_dir', 'logs'), log_file=kwargs.get('log_file', 'log.log'))
            self._set_error_file_handler(formatter=formatter, log_dir=kwargs.get('log_dir', 'logs'), error_file=kwargs.get('error_file', 'error.log'))
            self._set_console_handler(formatter)


    def _ensure_log_dir_exists(self, log_dir):
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
    def _set_main_file_handler(self, formatter:logging.Formatter, log_dir, log_file):
        file_handler = RotatingFileHandler(
            filename=os.path.join(log_dir, log_file), 
            maxBytes=1024*1024*5, 
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def _set_error_file_handler(self, formatter:logging.Formatter, log_dir:str, error_file:str):
        error_file_handler = logging.FileHandler(os.path.join(log_dir, error_file))
        error_file_handler.setLevel(logging.ERROR)  # 文件只记录 ERROR 及以上级别的日志
        error_file_handler.setFormatter(formatter)
        self.logger.addHandler(error_file_handler)

    def _create_formatter(self, fmt):
        return logging.Formatter(fmt)
    
    def _set_console_handler(self, formatter:logging.Formatter):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)
