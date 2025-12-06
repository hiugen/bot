import time

import re
from bs4 import BeautifulSoup
import requests
import os


rootDir = os.getcwd()
videoDir = os.path.join(rootDir, "Videos")
headers = {
    "User-Agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'''
}

base_url = "https://www.bilibili.com/"
class Bilibili:
    def __init__(self):
        self.title: str = ""

class BiliBiliRequestError(Exception):
    def __init__(self, url, statue_code):
        self.url = url
        self.statu_code = statue_code

    def __str__(self):
        return f"{self.url} 访问失败！状态码 {self.statu_code}"

class BilibiliVideo(Bilibili):
    def __init__(self, bv):
        super().__init__()
        self.bv: str= bv
        self.video_address = '' #视频路径.mp4
        self.url: str = base_url + "video/" + bv+"/"
        self.title: str = ""  #标题
        self.info: str = ""
        self.you_get: str = ""
        try:
            self.get_title_info()
        except AttributeError:
            print(" 发生 AttributeError " )

    def get_title_info(self):
        print(self.url)
        html = requests.get(self.url,headers=headers)
        if html.status_code != 200:
            print("bilibili 请求出错",html.status_code)
            raise BiliBiliRequestError(self.url, html.status_code)
        html = html.text
        soup = BeautifulSoup(html, "html.parser")
        self.title = soup.find("title").text.replace("_哔哩哔哩_bilibili", "")
        self.info = soup.find(name="span", attrs="desc-info-text").text

        invalid_chars = r'[^\w\s.-]'

        self.title = re.sub(invalid_chars, "_",self.title)
        self.video_address = os.path.join(videoDir , self.title.replace(" ", '')+".mp4")
        return 1

    def download_video(self):
        # TODO:you-get路径为相对，加cookie下高清
        os.chdir(videoDir)
        os.system("you-get -O " + self.title.replace(" ", '') +" " + self.url)
        os.chdir("..")

    def delete_video(self):
        os.remove(self.video_address)




if __name__ == "__main__":
    b=BilibiliVideo("BV1bnygBREiL")
    b.download_video()
    print(b.title,b.info)
    time.sleep(1)
    b.delete_video()

