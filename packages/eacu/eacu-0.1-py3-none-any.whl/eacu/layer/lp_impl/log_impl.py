import os
from art import tprint
from loguru import logger
from ..lprint import LPrint

LOGGER = logger.opt(depth=2, colors=True)

class LogImpl(LPrint):
    _loggable = True
    _logpath = None
    _loghid = None

    @property
    def loggable(self):
        """是否启用日志"""
        return self._loggable

    @loggable.setter
    def loggable(self, value: bool):
        """设置是否启用日志"""
        self._loggable = value
        if self._loggable:
            self.writeLog('INFO', '日志已启用')
        else:
            self.writeLog('INFO', '日志已禁用')

    @property
    def logpath(self):
        """日志文件路径"""
        return self._logpath

    @logpath.setter
    def logpath(self, value: str):
        """设置日志文件路径"""
        # check
        if not value.endswith('.txt'):
            self.writeLog('WARN', '日志文件路径必须以 .txt 结尾')
            return
        # check if file exists
        if not os.path.exists(os.path.dirname(value)):
            self.writeLog('WARN', f'日志文件基础路径 {os.path.dirname(value)} 不存在')
            return
        # 重置(如果不同)
        if value != self._logpath:
            # 清除内容
            with open(self._logpath, 'w') as f:
                f.write('')
                
            # 重置路径
            self._logpath = value

            # 重置日志记录器
            if self._loghid is not None:
                LOGGER.remove(self._loghid)
            self._loghid = LOGGER.add(self._logpath, rotation='500 MB', encoding='utf-8')

            self.writeLog('INFO', f'日志文件路径已重置为 {self._logpath}')
            
    def writeLog(self, level: str, *msg: str):
        """
        写入日志（仅在启用日志时生效）

        :param level: str 日志级别，如 'INFO', 'WARN', 'ERROR', 'DEBUG'
        :param * msg: str 日志内容
        :warns: 无

        :usage:
            # 示例用法
            printer.writeLog('INFO', 'This is a log entry')
        """
        if self._loggable:
            LOGGER.log(level, *msg)
        else:
            print(f"[{level}] {' '.join(msg)}")



        
