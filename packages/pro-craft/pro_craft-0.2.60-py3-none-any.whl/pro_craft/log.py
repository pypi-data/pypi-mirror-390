import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import inspect
class Log:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, console_level = logging.INFO, log_file_name="app.log"):
        self.Console_LOG_LEVEL = console_level
        self.log_file_name = log_file_name
        self.LOG_FILE_PATH = os.path.join("logs", log_file_name)
        os.makedirs(os.path.dirname(self.LOG_FILE_PATH), exist_ok=True)
        self.logger = self.get_logger()

    def get_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        if not logger.handlers:
            # --- 4. 配置 Formatter (格式化器) ---
            # 以后有一个标准化的日志要使用logger 而非标的则使用super-log
            formatter = logging.Formatter(
                "%(asctime)s $ %(created)f $ %(levelname)s $ %(funcName)s $ :%(lineno)d $ %(pathname)s $ %(message)s||"
            )
            # --- 5. 配置 Handler (处理器) ---

            # 5.1 控制台处理器 (StreamHandler)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.Console_LOG_LEVEL)  # 控制台只显示 INFO 及以上级别的日志
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # 文件系统
            ## 主日志本
            file_handler = RotatingFileHandler(  # RotatingFileHandler: 按文件大小轮转
                self.LOG_FILE_PATH,
                maxBytes=10 * 1024 * 1024,  # 10 MB # maxBytes: 单个日志文件的最大字节数 (例如 10MB)
                backupCount=10, # backupCount: 保留的旧日志文件数量
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)  # 文件中显示所有指定级别的日志
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            ## 运行日志本
            file_handler_info = RotatingFileHandler(
                self.LOG_FILE_PATH.replace('.log','_info.log'),
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler_info.setLevel(logging.INFO)  # 文件中显示所有指定级别的日志
            file_handler_info.setFormatter(formatter)
            logger.addHandler(file_handler_info)

            ## 错误日志本
            file_handler_warning = RotatingFileHandler(
                self.LOG_FILE_PATH.replace('.log','_err.log'),
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler_warning.setLevel(logging.WARNING)  # 文件中显示所有指定级别的日志
            file_handler_warning.setFormatter(formatter)
            logger.addHandler(file_handler_warning)

            ## 指定日志本 
            file_handler_super = RotatingFileHandler(
                self.LOG_FILE_PATH.replace('.log','_s.log'),
                maxBytes=5 * 1024 * 1024,  # 10 MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler_super.setLevel(logging.CRITICAL)  # 文件中显示所有指定级别的日志
            file_handler_super.setFormatter(formatter)
            logger.addHandler(file_handler_super)

            # class ConfigFilter(logging.Filter):
            #     # 初始化的方案
            #     def __init__(self, config_value, name=''):
            #         super().__init__(name)
            #         self.config_value = config_value

            #     def filter(self, record):
            #         record.config_info = self.config_value # 添加到LogRecord
            #         return True


            # class CustomFilter(logging.Filter):
            #     def filter(self, record):
            #         # 添加自定义的用户ID
            #         print(record,'recordrecordrecordrecordrecord')
            #         record.user_id = os.getenv("CURRENT_USER_ID", "anonymous")
            #         # 添加会话ID
            #         # record.session_id = "SESSION_XYZ123" # 实际应用中可能从request或全局变量获取
            #         frame = inspect.currentframe()
            #         info = inspect.getframeinfo(frame)
            #         # logger.error(f"Function name: {info.function} : {e}")
            #         record.session_id = f"Function name: {info.function}"
                    
            #         return True # 必须返回True才能继续处理该日志记录

            # # 将自定义过滤器添加到处理器或记录器
            # logger.addFilter(CustomFilter())
            # handler.addFilter(CustomFilter()) # 也可以加到handler上

            logger.info("这是一个包含自定义信息的日志")
        return logger
    