import os
import subprocess
import pyautogui
import pyperclip
import time
import shutil
import fitz


class MathematicaEvaluator:
    def __init__(self, temp_dir="./temp/"):
        # pyautogui.FAILSAFE = False
        self.temp_dir = temp_dir
        self._initialize_temp_dir()
        os.system('"C:\\Program Files\\Wolfram Research\\Mathematica\\13.3\\Mathematica.exe"')

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
        temp_file = "temp.pdf"
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

        # 按下 ctrl+shift+s，准备导出 pdf
        pyautogui.hotkey("ctrl", "shift", "s")

        # 输入文件名
        self._input(temp_file)

        # 鼠标移走（规避弹出的保存窗口）
        pyautogui.moveTo(100, 0)

        # 按下 tab 键，按 9 下 下箭头 (PDF 导出)
        pyautogui.press("tab")
        pyautogui.press("down", presses=9)

        # 按下两回车键
        pyautogui.press("enter", presses=2, interval=0.1)

        # 等待文件大小不为 0（完成 html 导出），10 秒超时
        temp_pdf_path = os.path.join(self.temp_dir, temp_file)
        start_time = time.time()
        while not os.path.exists(temp_pdf_path) or os.path.getsize(temp_pdf_path) == 0:
            temp_time = time.time() - start_time
            if temp_time > 5:
                return None
            time.sleep(0.1)

        time.sleep(2)  # 不能删

        # 保存并退出
        pyautogui.hotkey("ctrl", "s")
        time.sleep(0.5)
        pyautogui.hotkey("alt", "f4")
        # time.sleep(1)

        if os.path.exists(temp_pdf_path):
            return pdf2pngs(temp_pdf_path)
        else:
            return None


def pdf2pngs(pdf_file: str) -> list[str]:
    dir = os.path.dirname(pdf_file)
    doc = fitz.open(pdf_file)
    pngs = []
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        png_path = f'{dir}/page-{page.number}.png'
        pix.save(png_path)
        pngs.append(png_path)
    return pngs


if __name__ == "__main__":
    evaluator = MathematicaEvaluator()

    pngs = evaluator.evaluate("1+1")
    subprocess.run(["start", pngs[0]], shell=True)

    time.sleep(5)

    pngs = evaluator.evaluate("pi")
    subprocess.run(["start", pngs[0]], shell=True)
