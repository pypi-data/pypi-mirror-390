import os
import shutil
import sys
import re
import art
from ..lprint import LPrint
from colorama import Fore, Style

RAINBOW = (
    Fore.LIGHTRED_EX, Fore.RED, Fore.YELLOW,
    Fore.LIGHTGREEN_EX, Fore.GREEN, Fore.CYAN,
    Fore.LIGHTBLUE_EX, Fore.BLUE, Fore.MAGENTA
)

def rainbowify(lines, colors=RAINBOW):
    return [colors[i % len(colors)] + ln for i, ln in enumerate(lines)]

def make_banner(title, content, *, tail_blocks=2, center=True, title_colors=None, content_color=None):
    w = shutil.get_terminal_size().columns
    
    # 处理标题颜色
    if title_colors:
        bodys = [title_colors[i % len(title_colors)] + ln for i, ln in enumerate(title)]
    else:
        bodys = rainbowify(title)
    
    if content:
        # 处理内容颜色
        slogan = f" {content} "
        if content_color:
            slogan = content_color + slogan + Style.RESET_ALL
        
        tail_block = " " * tail_blocks
        box_top = "╔" + "═" * (len(slogan) + 2) + "╗" + tail_block
        box_bot = "╚" + "═" * (len(slogan) + 2) + "╝" + tail_block
        box_mid = f"║ {slogan} ║" + tail_block
        
        # 构建基础内容
        lines = [
            "", *[line for line in bodys], "",
            box_top, box_mid, box_bot, ""
        ]
    else:
        # 构建基础内容（无内容模式）
        lines = [
            "", *[line for line in bodys], "",
            "═" * w, ""
        ]
    
    # 在最后统一处理对齐方式
    result_lines = []
    for line in lines:
        if isinstance(line, str):
            # 移除ANSI颜色代码计算实际长度
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            if clean_line.strip():  # 只有非空行才需要对齐
                if center:
                    aligned = line.center(w)
                else:
                    aligned = line.ljust(w)
                result_lines.append(aligned)
            else:
                result_lines.append(line)
        else:
            result_lines.append(line)
    
    return "\n".join(result_lines)

class PrintImpl(LPrint):
    
    def debug(self, *msg: str):
        self.writeLog('DEBUG', *msg)
    
    def info(self, *msg: str):
        self.writeLog('INFO', *msg)
    
    def warn(self, *msg: str):
        self.writeLog('WARN', *msg)

    def error(self, *msg: str):
        self.writeLog('ERROR', *msg)
    
    def hello(self, title:str, content:str=None, *, font: str = 'sub-zero', center: bool = True, tails: int = 2, colors: list = None, ctcolor: str = None):
        # 字体检查（修正：FONT_MAP 才是正确属性）
        if font not in art.FONT_NAMES:
            original_font = font
            font = 'big'
            self.warn(f'Font "{original_font}" not found, use default font "{font}" instead.')
        
        # 生成艺术字
        txt_title = art.text2art(title, font=font)
        
        # 生成banner
        banner = make_banner(txt_title.split('\n'), content, center=center, tail_blocks=tails, title_colors=colors, content_color=ctcolor)
        self.writeLog('INFO', banner)





