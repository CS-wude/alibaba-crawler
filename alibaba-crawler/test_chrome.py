#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 测试Chrome WebDriver作为替代方案

try:
    print("尝试导入 selenium...")
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    print("✅ selenium 导入成功")
    
    print("创建 Chrome options...")
    options = Options()
    options.add_argument('--headless')  # 无头模式
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    print("✅ Chrome options 创建成功")
    
    # 注意：需要下载 chromedriver.exe
    print("注意：如果要使用Chrome，需要下载 chromedriver.exe")
    print("可以从 https://chromedriver.chromium.org/ 下载")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    
except Exception as e:
    print(f"❌ 运行错误: {e}")
