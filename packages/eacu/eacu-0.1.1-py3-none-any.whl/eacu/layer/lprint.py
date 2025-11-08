from onion import *


class LPrint(Onion):
    """
    抽象打印类，支撑所有的print语句、警告、报错

    特性：
    - 继承自Onion抽象类，支持洋葱架构模式
    - 提供统一的打印接口
    - 可选启用日志功能（默认开启）
    """

    __INSTANCE = None

    def __new__(cls, *args, **kwargs):
        if not cls.__INSTANCE:
            cls.__INSTANCE = super(LPrint, cls).__new__(cls)
        return cls.__INSTANCE

    # 公开API区域 - 抽象方法
    @property
    @abstractmethod
    def loggable(self):
        """是否启用日志"""
        pass

    @loggable.setter
    @abstractmethod
    def loggable(self, value: bool):
        """设置是否启用日志"""
        pass

    @property
    @abstractmethod
    def logpath(self):
        """日志文件路径"""
        pass

    @logpath.setter
    @abstractmethod
    def logpath(self, value: str):
        """设置日志文件路径"""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def debug(self, *msg: str):
        """
        打印调试信息（仅在调试模式下显示）

        :param * msg: str 调试信息

        :usage:
            # 示例用法
            printer.debug("Debug information")
        """
        pass

    @abstractmethod
    def info(self, *msg: str):
        """
        打印普通信息

        :param * msg: str 要打印的信息

        :usage:
            # 示例用法
            printer.info("Hello World")
        """
        pass

    @abstractmethod
    def warn(self, *msg: str):
        """
        打印警告信息

        :param * msg: str 警告信息  

        :usage:
            # 示例用法
            printer.warn("This is a warning")
        """
        pass

    @abstractmethod
    def error(self, *msg: str):
        """
        打印错误信息

        :param * msg: str 错误信息

        :usage:
            # 示例用法
            printer.error("This is an error")
        """
        pass

    @abstractmethod
    def hello(self, title: str, content: str = None, *, font: str = 'big', center: bool = True, tails: int = 2, colors: list = None, ctcolor: str = None):
        """
        打印欢迎信息

        :param title: str 欢迎信息标题
        :param content: str 欢迎信息内容(可选，此时只显示标题)
        :param font: str 字体样式，可选值为 'big'（默认）或:
            >> 方块/粗体类: 'block','banner3','big','doom','roman'
            >> 3D立体类: '3-d','3x5','isometric1','isometric3','larry3d'
            >> 手写/艺术风格: 'cursive','fancy1','script','grafitti','tarty1'
            >> 小型紧凑类: 'small','mini','tiny','digital','binary'
            >> 装饰边框类: 'barbwire','dancingMen','lockergnome'
            >> 趣味创意类: 'bubbles','ghost','hex','smblock','smkeyboard'
            >> 夹带私货 "sub-zero", "tarty1"
        
        :param center: bool 是否居中对齐，默认值为 True
        :param tails: int 边框后的尾巴长度(空格数)，默认值为 2。仅用于调整content
        :param colors: list 标题颜色列表，默认为None使用彩虹色
        :param ctcolor: str 内容颜色，默认为None使用默认颜色

        :note: 欢迎信息标题和内容都最好不要有换行
        :usage:
            # 示例用法
            printer.hello()
        """
        pass


if __name__ == '__main__':
    from layer.lp_impl import *

    lp = LPrint()

    lp.hello("EACU", "**************** Welcome to EACU ****************", tails=4)
