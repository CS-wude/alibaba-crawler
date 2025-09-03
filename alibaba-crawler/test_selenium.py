#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 简化的测试文件，检查Selenium是否能正常工作

try:
    print("导入 selenium...")
    from selenium import webdriver
    print("✅ selenium 导入成功")
    
    print("导入 selenium options...")
    from selenium.webdriver.firefox.options import Options
    print("✅ Firefox options 导入成功")
    
    print("导入 selenium service...")
    from selenium.webdriver.firefox.service import Service
    print("✅ Firefox service 导入成功")
    
    print("创建 Firefox options...")
    options = Options()
    options.headless = True
    print("✅ Firefox options 创建成功")
    
    print("创建 Firefox service...")
    service = Service(executable_path="geckodriver.exe")
    print("✅ Firefox service 创建成功")
    
    print("尝试创建 Firefox driver...")
    try:
        # 新版本 Selenium (4.x) 使用 service 参数
        driver = webdriver.Firefox(service=service, options=options)
    except TypeError:
        # 旧版本 Selenium (3.x) 使用 executable_path 参数
        driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options)
    print("✅ Firefox driver 创建成功")
    
    print("测试访问页面...")
    driver.get("https://www.google.com")
    print("✅ 页面访问成功")
    
    print("关闭浏览器...")
    driver.quit()
    print("✅ 浏览器关闭成功")
    
    print("\n🎉 所有测试通过！Selenium 配置正确。")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请检查依赖包安装")
    
except Exception as e:
    print(f"❌ 运行错误: {e}")
    print("请检查 geckodriver.exe 和 Firefox 是否正确安装")
