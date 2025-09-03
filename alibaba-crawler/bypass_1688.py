#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
1688验证码绕过尝试脚本
使用更真实的浏览器配置
"""

import time
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class AntiDetection1688:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """设置反检测的Firefox浏览器"""
        try:
            options = Options()
            options.headless = False  # 保持可见
            
            # 添加反检测设置
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # 设置用户代理
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            # 设置窗口大小
            options.add_argument('--window-size=1366,768')
            
            try:
                service = Service(executable_path="geckodriver.exe")
                self.driver = webdriver.Firefox(service=service, options=options)
            except TypeError:
                self.driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options)
            
            # 隐藏自动化特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ 反检测Firefox浏览器启动成功")
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            raise
    
    def human_like_behavior(self):
        """模拟人类行为"""
        # 随机滚动
        scroll_height = random.randint(200, 800)
        self.driver.execute_script(f"window.scrollTo(0, {scroll_height});")
        time.sleep(random.uniform(0.5, 2.0))
        
        # 随机移动鼠标（通过JavaScript）
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        self.driver.execute_script(f"""
            var event = new MouseEvent('mousemove', {{
                'view': window,
                'bubbles': true,
                'cancelable': true,
                'clientX': {x},
                'clientY': {y}
            }});
            document.dispatchEvent(event);
        """)
        time.sleep(random.uniform(0.2, 1.0))
    
    def check_captcha(self):
        """检查是否出现验证码"""
        captcha_indicators = [
            "验证码", "captcha", "滑动验证", "点击验证", "human", "robot",
            ".captcha", "#captcha", "[class*='captcha']", "[id*='captcha']"
        ]
        
        for indicator in captcha_indicators:
            try:
                if indicator.startswith('.') or indicator.startswith('#') or indicator.startswith('['):
                    # CSS选择器
                    elements = self.driver.find_elements(By.CSS_SELECTOR, indicator)
                    if elements:
                        return True, f"发现验证码元素: {indicator}"
                else:
                    # 文本搜索
                    elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{indicator}')]")
                    if elements:
                        return True, f"发现验证码文本: {indicator}"
            except:
                pass
        
        return False, "未发现验证码"
    
    def gradual_access(self, url):
        """逐步访问页面"""
        try:
            print(f"🚀 开始逐步访问: {url}")
            
            # 第1步：先访问1688首页
            print("📍 步骤1: 访问1688首页...")
            self.driver.get("https://www.1688.com")
            time.sleep(random.uniform(3, 7))
            self.human_like_behavior()
            
            # 检查是否有验证码
            has_captcha, msg = self.check_captcha()
            if has_captcha:
                print(f"⚠️ 首页出现验证码: {msg}")
                input("请手动完成验证码，然后按回车继续...")
            
            # 第2步：访问目标页面
            print("📍 步骤2: 访问目标商品页面...")
            self.driver.get(url)
            time.sleep(random.uniform(5, 10))
            
            # 再次检查验证码
            has_captcha, msg = self.check_captcha()
            if has_captcha:
                print(f"⚠️ 商品页面出现验证码: {msg}")
                input("请手动完成验证码，然后按回车继续...")
            
            # 第3步：模拟人类浏览行为
            print("📍 步骤3: 模拟人类浏览...")
            for i in range(3):
                self.human_like_behavior()
                time.sleep(random.uniform(1, 3))
            
            # 第4步：尝试提取信息
            print("📍 步骤4: 尝试提取商品信息...")
            return self.extract_product_info()
            
        except Exception as e:
            print(f"❌ 逐步访问失败: {e}")
            return None
    
    def extract_product_info(self):
        """提取商品信息（增强版）"""
        product_info = {}
        
        # 保存当前页面源码
        with open("current_page_source.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print("✅ 当前页面源码已保存")
        
        # 尝试多种标题选择器
        title_selectors = [
            'h1', '.offer-title', '.d-title', '.detail-title',
            '[class*="title"]', '[class*="name"]', '.product-name'
        ]
        
        for selector in title_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and len(text) > 5:  # 过滤太短的文本
                    product_info['title'] = text
                    print(f"✅ 找到标题: {text[:50]}...")
                    break
            except:
                continue
        
        # 尝试提取页面所有文本进行分析
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        print(f"📊 页面总文本长度: {len(body_text)}")
        
        # 查找价格相关信息
        import re
        price_patterns = [
            r'￥[\d,.]+', r'¥[\d,.]+', r'\d+\.\d+元',
            r'price["\']?\s*:\s*["\']?[\d,.]+', r'\d+\.\d+起'
        ]
        
        found_prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, body_text)
            found_prices.extend(matches)
        
        if found_prices:
            product_info['price'] = found_prices[0]
            print(f"✅ 找到价格: {found_prices[0]}")
        
        return product_info
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            input("📋 信息提取完成，请查看浏览器页面。按回车关闭浏览器...")
            self.driver.quit()
            print("✅ 浏览器已关闭")

def main():
    """主函数"""
    url = "https://detail.1688.com/offer/775610063728.html?offerId=775610063728&spm=a260k.home2025.recommendpart.18"
    
    crawler = None
    try:
        print("🔧 开始反验证码1688爬取测试...")
        
        crawler = AntiDetection1688()
        product_info = crawler.gradual_access(url)
        
        if product_info:
            print("\n📊 提取结果:")
            print("="*50)
            for key, value in product_info.items():
                print(f"{key}: {value}")
            print("="*50)
        else:
            print("❌ 未能提取到商品信息")
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    main()
