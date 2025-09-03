#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
1688页面结构调试脚本
用于分析1688网站的实际HTML结构
"""

import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class Debug1688:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """设置Firefox浏览器"""
        try:
            options = Options()
            options.headless = False  # 保持可见以便观察
            
            try:
                service = Service(executable_path="geckodriver.exe")
                self.driver = webdriver.Firefox(service=service, options=options)
            except TypeError:
                self.driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options)
            
            print("✅ Firefox浏览器启动成功")
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            raise
    
    def analyze_page(self, url):
        """分析页面结构"""
        try:
            print(f"🔍 开始访问: {url}")
            self.driver.get(url)
            
            # 等待页面完全加载
            print("⏳ 等待页面加载...")
            time.sleep(10)  # 增加等待时间
            
            # 获取页面标题
            page_title = self.driver.title
            print(f"📄 页面标题: {page_title}")
            
            # 保存页面源码到文件
            with open("1688_page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print("✅ 页面源码已保存到: 1688_page_source.html")
            
            # 尝试查找常见的页面元素
            self.find_common_elements()
            
            # 等待用户手动检查页面
            input("👀 请在浏览器中手动检查页面元素，然后按回车继续...")
            
        except Exception as e:
            print(f"❌ 分析页面失败: {e}")
    
    def find_common_elements(self):
        """查找常见的页面元素"""
        print("\n🔍 搜索常见元素...")
        
        # 搜索包含关键词的元素
        keywords = {
            "标题": ["title", "名称", "产品", "商品"],
            "价格": ["price", "价格", "￥", "元", "price"],
            "图片": ["img", "image", "pic", "photo"],
            "供应商": ["supplier", "公司", "店铺", "厂家"],
        }
        
        for info_type, words in keywords.items():
            print(f"\n--- 搜索 {info_type} ---")
            found_elements = []
            
            for word in words:
                # 搜索包含关键词的元素
                try:
                    # 通过文本内容搜索
                    elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{word}')]")
                    for elem in elements[:3]:  # 最多显示3个
                        try:
                            text = elem.text.strip()
                            tag = elem.tag_name
                            class_name = elem.get_attribute("class")
                            if text:
                                found_elements.append(f"  📍 {tag}.{class_name}: {text[:30]}...")
                        except:
                            pass
                    
                    # 通过class名搜索
                    elements = self.driver.find_elements(By.CSS_SELECTOR, f"[class*='{word}']")
                    for elem in elements[:2]:  # 最多显示2个
                        try:
                            text = elem.text.strip()
                            tag = elem.tag_name
                            class_name = elem.get_attribute("class")
                            if text:
                                found_elements.append(f"  🎯 {tag}.{class_name}: {text[:30]}...")
                        except:
                            pass
                            
                except Exception:
                    pass
            
            # 显示找到的元素
            if found_elements:
                for elem in found_elements[:5]:  # 最多显示5个
                    print(elem)
            else:
                print(f"  ❌ 未找到 {info_type} 相关元素")
    
    def extract_all_images(self):
        """提取所有图片元素"""
        print("\n🖼️ 提取所有图片...")
        try:
            images = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"📊 找到 {len(images)} 个图片元素")
            
            for i, img in enumerate(images[:10]):  # 最多显示10个
                try:
                    src = img.get_attribute("src") or img.get_attribute("data-src")
                    alt = img.get_attribute("alt")
                    class_name = img.get_attribute("class")
                    print(f"  {i+1}. class='{class_name}' alt='{alt}' src='{src[:50]}...'")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ 提取图片失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✅ 浏览器已关闭")

def main():
    """主函数"""
    url = "https://detail.1688.com/offer/775610063728.html?offerId=775610063728&spm=a260k.home2025.recommendpart.18"
    
    debug = None
    try:
        print("🔧 开始1688页面结构调试...")
        
        debug = Debug1688()
        debug.analyze_page(url)
        debug.extract_all_images()
        
        print("\n📋 调试完成！请检查生成的文件:")
        print("  - 1688_page_source.html (页面源码)")
        print("\n🔍 下一步建议:")
        print("  1. 打开页面源码文件，搜索商品信息")
        print("  2. 找到正确的CSS选择器")
        print("  3. 更新test_1688.py中的选择器")
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
    
    finally:
        if debug:
            debug.close()

if __name__ == "__main__":
    main()