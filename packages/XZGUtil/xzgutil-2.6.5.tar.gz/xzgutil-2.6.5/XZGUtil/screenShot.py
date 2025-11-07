import os
import tkinter as tk
import pyautogui
import keyboard
from datetime import datetime
from PIL import Image, ImageTk
"""截图"""

# 配置部分
SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")  # 截图保存目录
HOTKEY = "alt+a"  # 触发截图的热键组合


def select_area():
    """启动区域选择界面并截图"""
    # 先截取完整屏幕
    full_screenshot = pyautogui.screenshot()

    # 创建顶层窗口
    root = tk.Tk()
    root.overrideredirect(True)  # 隐藏窗口装饰
    root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    root.attributes("-alpha", 0.8)  # 半透明
    root.attributes("-topmost", True)  # 置顶窗口

    # 将截图转换为Tkinter可用格式
    img = ImageTk.PhotoImage(full_screenshot)

    canvas = tk.Canvas(root, cursor="cross")
    canvas.pack(fill="both", expand=True)

    # 在画布上显示截图
    bg_image = canvas.create_image(0, 0, anchor=tk.NW, image=img)
    canvas.image = img  # 保持引用，防止被垃圾回收

    start_x, start_y = None, None
    rect = None
    window_destroyed = False  # 标记窗口是否已销毁

    def on_click(event):
        nonlocal start_x, start_y, rect, window_destroyed
        if window_destroyed:  # 窗口已销毁则直接返回
            return
        start_x = event.x
        start_y = event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

    def on_drag(event):
        nonlocal rect, window_destroyed
        if window_destroyed:  # 窗口已销毁则直接返回
            return
        current_x, current_y = event.x, event.y
        if rect:
            canvas.coords(rect, start_x, start_y, current_x, current_y)

    def on_release(event):
        nonlocal window_destroyed
        # 标记窗口即将销毁，避免后续事件触发
        window_destroyed = True
        # 先获取坐标再销毁窗口
        try:
            x1, y1 = start_x, start_y
            x2, y2 = event.x, event.y
        except (tk.TclError, TypeError):  # 捕获窗口已销毁或坐标未初始化的错误
            root.destroy()
            return

        # 销毁窗口
        root.destroy()

        # 计算截图区域
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        # 确保区域有效
        if width <= 0 or height <= 0:
            print("截图区域无效")
            return

        # 从原始截图中提取选定区域
        region = (left, top, left + width, top + height)
        cropped_screenshot = full_screenshot.crop(region)

        # 获取用户输入的文件名（返回None表示取消）
        file_name = get_user_filename()
        if file_name:  # 如果用户没有取消
            save_screenshot(cropped_screenshot, file_name)

    # 绑定鼠标事件
    canvas.bind("<ButtonPress-1>", on_click)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)

    # 绑定ESC键退出
    def on_escape(event):
        nonlocal window_destroyed
        window_destroyed = True
        root.destroy()

    root.bind("<Escape>", on_escape)

    root.mainloop()


def get_user_filename():
    """获取用户输入的文件名（不含后缀）"""
    # 创建独立的Tk窗口
    root = tk.Tk()
    root.title("输入文件名")
    root.geometry("300x150")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # 居中窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # 生成默认文件名（带时间戳，不含后缀）
    default_filename = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 文件名变量
    filename_var = tk.StringVar(value=default_filename)

    # 界面元素
    tk.Label(root, text="请输入文件名（不含后缀）:").pack(pady=10)
    entry = tk.Entry(root, textvariable=filename_var, width=30)
    entry.pack(pady=5)
    entry.focus_set()  # 自动聚焦输入框

    # 存储结果的变量
    result = [None]  # None表示取消

    def on_ok():
        name = filename_var.get().strip()
        if not name:
            name = default_filename
        result[0] = name  # 只保存文件名，不含后缀
        root.destroy()

    def on_cancel():
        root.destroy()

    # 按钮区域
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="确定", command=on_ok).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="取消", command=on_cancel).pack(side=tk.LEFT)

    # 绑定Enter键确认
    root.bind("<Return>", lambda e: on_ok())
    # 绑定ESC键取消
    root.bind("<Escape>", lambda e: on_cancel())

    root.mainloop()
    return result[0]


def save_screenshot(screenshot, file_name):
    """保存截图"""
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 确保文件名不含后缀，然后添加.png
    if file_name.lower().endswith(".png"):
        file_name = file_name[:-4]

    save_path = os.path.join(SAVE_DIR, f"{file_name}.png")

    try:
        screenshot.save(save_path)
        print(f"截图已保存至：{save_path}")
        show_success_message(f"截图已保存至:\n{save_path}")
    except Exception as e:
        print(f"截图失败: {e}")
        show_error_message(f"保存失败:\n{str(e)}")


def show_success_message(message):
    """显示成功消息"""
    root = tk.Tk()
    root.title("成功")
    root.geometry("300x150")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # 居中窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    tk.Label(root, text=message, fg="green").pack(pady=20)
    tk.Button(root, text="确定", command=root.destroy).pack(pady=10)

    # 3秒后自动关闭
    root.after(500, root.destroy)
    root.mainloop()


def show_error_message(message):
    """显示错误消息"""
    root = tk.Tk()
    root.title("错误")
    root.geometry("300x150")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # 居中窗口
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    tk.Label(root, text=message, fg="red").pack(pady=20)
    tk.Button(root, text="确定", command=root.destroy).pack(pady=10)

    root.mainloop()


def main():
    print(f"截图工具已启动，按 {HOTKEY} 组合键选择区域截图")
    print(f"截图将保存至: {SAVE_DIR}")
    keyboard.add_hotkey(HOTKEY, select_area)
    keyboard.wait()


if __name__ == "__main__":
    main()
