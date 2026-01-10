import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.chrome import ChromeType
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def generate_and_download_audio(input_text):
    """
    自动化访问https://shuodedao.li/网站，输入文本生成音频并下载
    
    参数:
    input_text (str): 要转换为音频的文本内容
    
    返回:
    str: 下载的音频文件路径
    """
    # 设置下载路径为当前文件夹的audio_downloads子文件夹
    current_dir = os.path.dirname(os.path.abspath(__file__))
    download_dir = os.path.join(current_dir, "audio_downloads")
    
    # 如果子文件夹不存在，则创建它
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # 配置Chrome浏览器选项（适用于WSL环境）
    chrome_options = webdriver.ChromeOptions()
    
    # 添加WSL环境所需的无头模式和其他配置
    chrome_options.add_argument('--headless=new')  # 新无头模式（Chrome 96+推荐）
    chrome_options.add_argument('--no-sandbox')  # 禁用沙盒模式，WSL必需
    chrome_options.add_argument('--disable-dev-shm-usage')  # 解决/dev/shm分区不足问题
    chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
    chrome_options.add_argument('--remote-debugging-port=9222')  # 启用远程调试端口
    chrome_options.add_argument('--window-size=1920x1080')  # 设置窗口大小
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')  # 设置User-Agent
    
    # 配置下载选项
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,  # 在无头模式下可能需要禁用安全浏览
        "profile.default_content_setting_values.automatic_downloads": 1,  # 允许自动下载
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1  # 允许所有自动下载
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # 解决ChromeDriver与Chrome版本不匹配的问题
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    # 初始化WebDriver（自动管理ChromeDriver）
    try:
        # 尝试使用默认ChromeDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    except Exception as e:
        print(f"默认ChromeDriver初始化失败: {e}")
        print("尝试使用Chromium选项...")
        # 尝试使用Chromium
        chrome_options.binary_location = "/usr/bin/chromium-browser"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version="latest", chrome_type=ChromeType.CHROMIUM).install()), options=chrome_options)
    
    try:
        # 访问目标网站
        driver.get("https://shuodedao.li/")
        driver.maximize_window()  # 最大化窗口
        
        # 等待页面完全加载
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, 'div'))
        )
        
        # 查找文本输入框，使用更可靠的定位方式
        # 尝试查找textarea元素
        try:
            input_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.TAG_NAME, 'textarea'))
            )
        except:
            # 如果找不到textarea，尝试使用原始XPath但确保元素可交互
            input_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/section/main/div/div[3]/div[1]/div[1]/div/div[2]/form/div[1]/div[2]'))
            )
        
        # 清空输入框并输入文本
        driver.execute_script("arguments[0].value = '';", input_element)
        input_element.send_keys(input_text)
        
        # 查找生成按钮，使用更可靠的定位方式
        try:
            generate_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "生成")]'))
            )
        except:
            generate_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/section/main/div/div[3]/div[1]/div[1]/div/div[2]/form/div[4]/div[2]/button'))
            )
        
        # 确保按钮在视口中可见
        driver.execute_script("arguments[0].scrollIntoView(true);", generate_button)
        time.sleep(0.5)
        generate_button.click()
        
        # 等待音频生成完成
        time.sleep(5)  # 增加等待时间确保音频生成完成
        
        # 查找下载按钮，使用更可靠的定位方式
        try:
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "下载")][1]'))
            )
        except:
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[2]/section/main/div/div[3]/div[1]/div[3]/div/div[2]/div[5]/button[1]'))
            )
        
        # 确保按钮在视口中可见
        driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
        time.sleep(0.5)
        download_button.click()
        
        # 等待下载完成（根据网络情况调整时间）
        time.sleep(5)
        
        # 获取最新下载的文件
        files = [os.path.join(download_dir, f) for f in os.listdir(download_dir) 
                 if os.path.isfile(os.path.join(download_dir, f))]
        if not files:
            return None
        
        # 按修改时间排序，获取最新文件
        files.sort(key=os.path.getmtime, reverse=True)
        latest_file = files[0]
        
        return latest_file
        
    except Exception as e:
        print(f"发生错误: {e}")
        return None
    finally:
        
        # 关闭浏览器
        driver.quit()

# 示例用法
if __name__ == "__main__":
    test_text = "米浴说的道理"
    audio_path = generate_and_download_audio(test_text)
    print(f"生成的音频文件路径: {audio_path}")