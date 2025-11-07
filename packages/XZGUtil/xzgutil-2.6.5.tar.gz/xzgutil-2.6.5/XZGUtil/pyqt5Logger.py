#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Author   : 许老三
# @Time    : 2025/4/24 下午5:06
# @Site    : 技术创新中心
# @File    : pyqt5Logger.py
# @Software: PyCharm
from PyQt5.QtWidgets import QApplication, QTextEdit, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import atexit
import sys
import time

class _FloatingLoggerImpl(QWidget):
    """实际的日志窗口实现类"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        atexit.register(self.cleanup)

    def _setup_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 180);
                border-radius: 5px;
            }
            QTextEdit {
                color: white;
                background: transparent;
                border: none;
                font: 10pt Consolas;
                padding: 5px;
            }
        """)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setHtml("")  # 初始化HTML内容

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        self.resize(400, 200)
        self._move_to_bottom_right()

    def _move_to_bottom_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            screen.right() - self.width() - 10,
            screen.bottom() - self.height() - 40
        )

    def append_log(self, message, level="info"):
        """添加日志消息"""
        color_map = {
            "info": "#006400",  # 深绿色
            "warning": "#FFFF00",  # 黄色
            "error": "#FF5A5A",  # 红色
            "debug": "#808080"   # 灰色
        }
        self.text_edit.append(
            f'<span style="color:{color_map.get(level, "white")}">'
            f'[{level.upper()}] {message}'
            f'</span>'
        )
        self.text_edit.verticalScrollBar().setValue(
            self.text_edit.verticalScrollBar().maximum()
        )
        if not self.isVisible():
            self.show()

    def cleanup(self):
        """程序退出时安全清理"""
        if QApplication.instance() is not None:
            self.close()


class LoggerSignals(QObject):
    """线程安全信号"""
    log_signal = pyqtSignal(str, str)


class FloatingLogger:
    """安全的日志工具包装类"""
    _instance = None
    _signals = None
    _app = None

    def __init__(self):
        raise RuntimeError("请使用get_instance()获取实例")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._init_qapplication()
            cls._instance = _FloatingLoggerImpl()
            cls._signals = LoggerSignals()
            cls._signals.log_signal.connect(cls._instance.append_log)
        return cls._instance

    @classmethod
    def _init_qapplication(cls):
        """安全初始化QApplication"""
        if QApplication.instance() is None:
            cls._app = QApplication(sys.argv)
            atexit.register(cls._app.quit)

    @classmethod
    def log(cls, message, level="info"):
        """线程安全的日志方法"""
        cls.get_instance()  # 确保实例已创建
        if cls._signals is not None:
            cls._signals.log_signal.emit(message, level)
        else:
            cls._instance.append_log(message, level)

    @classmethod
    def start_application(cls):
        """启动Qt应用程序事件循环"""
        if cls._app is None:
            cls._init_qapplication()
        return cls._app.exec_()


# 全局接口函数
def _log(message, level="info"):
    FloatingLogger.log(message, level)

def info(message):
    _log(message, "info")

def warning(message):
    _log(message, "warning")

def error(message):
    _log(message, "error")

def debug(message):
    _log(message, "debug")

def log(message, level="info"):
    _log(message, level)

def start_application():
    """启动Qt应用程序事件循环"""
    return FloatingLogger.start_application()


# 当模块被导入时自动初始化
FloatingLogger.get_instance()


if __name__ == '__main__':
    while True:
        # 记录一些日志
        info("应用程序启动")
        warning("这是一个警告")
        error("发生了一个错误")
        debug("调试信息")
        time.sleep(1)
        # 启动应用程序事件循环
        start_application()

