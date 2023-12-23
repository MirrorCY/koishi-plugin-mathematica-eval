import os
import subprocess
import pyautogui
import pyperclip
import time
import shutil


class MathematicaEvaluator:
    def __init__(self, temp_dir="./temp/"):
        # pyautogui.FAILSAFE = False
        self.temp_dir = temp_dir
        self._initialize_temp_dir()

    def _initialize_temp_dir(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)

    def _locate(self, img, timeout, confidence=0.8):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return pyautogui.locateCenterOnScreen(img, confidence=confidence)
            except:
                pass
        return None

    def _input(self, text):
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v", interval=0.1)

    def evaluate(self, code, timeout=10, step=False):
        # 初始化临时目录
        self._initialize_temp_dir()
        temp_file = "temp.html"
        temp_nb = os.path.join(self.temp_dir, "temp.nb")
        with open(temp_nb, "w") as f:
            f.write("Notebook[{}]")

        # 打开 Mathematica
        subprocess.run(["start", temp_nb], shell=True)
        time.sleep(1)  # TODO: 检测 Mathematica 打开，现在需要保证后台启动以获得最快的打开速度

        # 输入命令
        pyautogui.write("==")  # 这玩意还不能粘贴，贴进去的没用，好在 = 不受全角字符影响
        time.sleep(0.5)
        self._input(code)

        # [开始运行].webp
        pyautogui.press("enter")

        # 定位到 step by step 按钮
        step_center = self._locate("step.png", timeout)

        # 点击按钮
        if step_center is not None and step:
            pyautogui.click(step_center)

            # 鼠标移走，避免遮挡
            pyautogui.moveTo(100, 0)

            # 等待直到 hide 出现
            self._locate("hide.png", 10, confidence=0.6)

        # 按下 ctrl+shift+s，准备导出 html
        pyautogui.hotkey("ctrl", "shift", "s")

        # 输入文件名
        self._input(temp_file)

        # 等待 1 秒
        time.sleep(1)

        # 鼠标移走（规避弹出的保存窗口）
        pyautogui.moveTo(100, 0)

        # 按下 tab 键，按 11 下 下箭头，每次间隔 0.1 秒（选择 HTML 方式保存）
        pyautogui.press("tab")
        pyautogui.press("down", presses=11)

        # 按下两回车键
        pyautogui.press("enter", presses=2, interval=0.1)
        time.sleep(1)

        # 等待文件大小不为 0（完成 html 导出），10 秒超时
        temp_html_path = os.path.join(self.temp_dir, temp_file)
        start_time = time.time()
        while (
            not os.path.exists(temp_html_path) or os.path.getsize(temp_html_path) == 0
        ):
            temp_time = time.time() - start_time
            if temp_time > 30:
                return None
            time.sleep(0.1)

        time.sleep(2)  # 不能删

        # 保存并退出
        pyautogui.hotkey("ctrl", "s")
        time.sleep(0.5)
        pyautogui.hotkey("alt", "f4")
        # time.sleep(1)

        # 返回 HTML 下的 temp_1.gif 文件
        gif_file = os.path.join(self.temp_dir, "HTMLFiles/temp_1.gif")
        if os.path.exists(gif_file):
            return copy_gif(gif_file)
        else:
            return None


# 复制 gif 文件到上传目录
def copy_gif(gif_file, upload_dir="./upload/"):
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    gif_name = str(time.time()) + ".gif"
    gif_path = os.path.join(upload_dir, gif_name)
    shutil.copy(gif_file, gif_path)
    return gif_path


if __name__ == "__main__":
    evaluator = MathematicaEvaluator()

    gif = evaluator.evaluate("pi")
    if gif:
        subprocess.run(["start", gif], shell=True)
        time.sleep(5)

    gif = evaluator.evaluate("1+1")
    if gif:
        subprocess.run(["start", gif], shell=True)
