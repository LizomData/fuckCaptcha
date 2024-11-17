import os
import sys
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from flask import Flask, make_response, request
from selenium.webdriver.common.by import By
import random

app = Flask(__name__)

if os.name == 'nt':
    print("当前系统是 Windows")
    os_type=0
elif os.name == 'posix':
    print("当前系统是 Linux")
    os_type=1
else:
    print("无法识别当前操作系统")
    exit(1)

class ExeUtils:
    """exe生成相关工具类"""

    @staticmethod
    def get_resources(path):
        """
        获取实际的资源访问路径(本地||临时)
        根据打包生成的临时目录访问资源
        或者直接运行脚本获取本地访问资源
        :param path:
        :return:
        """
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, path)


# 计算耗时的装饰器
def time_it(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 调用被装饰的函数
        end_time = time.time()  # 记录结束时间
        print(f"Function '{func.__name__}' took {end_time - start_time:.6f} seconds.")
        return result

    return wrapper


class captBrowser:
    def __init__(self):

        if os_type == 0 :
            self.chrome_driver = ExeUtils.get_resources(r"assets\chrome-win64\chromedriver.exe")  # 浏览器驱动
            self.chrome_app = ExeUtils.get_resources(r"assets\chrome-win64\chrome.exe")  # 浏览器
            self.html_path = ExeUtils.get_resources(r'assets\captcha.html')
        elif os_type == 1 :
            self.chrome_driver = ExeUtils.get_resources(r"assets/chrome-linux64/chromedriver")  # 浏览器驱动
            self.chrome_app = ExeUtils.get_resources(r"assets/chrome-linux64/chrome")  # 浏览器
            self.html_path = ExeUtils.get_resources(r'assets/captcha.html')


        chrome_options = Options()
        chrome_options.add_argument('--disable-web-security')  # 启动时禁用同源策略
        if os_type == 1:
            chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速
        chrome_options.add_argument("--no-sandbox")  # 提高兼容性，避免沙箱问题

        s = Service(self.chrome_driver)
        chrome_options.binary_location = self.chrome_app  # 添加浏览器
        self.driver = webdriver.Chrome(service=s, options=chrome_options)
        self.driver.get(f"file:///{self.html_path}")
        self.count=0
        self.count_max=10



    def get_valddata(self,YMtoken):
        if self.count >= self.count_max :
            return '并发数限制'
        self.count += 1

        id = 'captcha' + str(random.randint(0, 10000000))
        self.driver.execute_script(f'createCaptcha(\'{id}\',\'{YMtoken}\')')
        element = self.driver.find_element(by=By.ID, value=id + '-ve')

        while "ready" in element.text:
            pass
        validata = element.text
        self.driver.execute_script(f'destroyCaptcha(\'{id}\')')

        self.count -= 1

        # self.driver.close()
        return validata


br = captBrowser()
@time_it
def get_vaildata(YMtoken):
    re = br.get_valddata(YMtoken)
    print(re)
    return re


@app.route('/', methods=["POST"])
def hello():
    resp = make_response()
    resp.headers["access-control-allow-origin"] = "*"
    YMtoken = request.args.get('YMtoken')
    if YMtoken is None:
        resp.response='参数错误'
        return resp
    resp.response = f'{get_vaildata(YMtoken)}'
    return resp


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1084)

