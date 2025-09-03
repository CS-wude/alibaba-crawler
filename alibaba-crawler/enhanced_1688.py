#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强版1688商品信息提取器
包含完整的商品信息提取和保存功能
"""

import time
import random
import json
import csv
import os
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests

class Enhanced1688Crawler:
    def __init__(self):
        self.driver = None
        self.product_data = {}
        self.setup_driver()
        self.setup_output_folders()
    
    def setup_output_folders(self):
        """创建输出文件夹"""
        folders = ['images', 'data', 'logs']
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"✅ 创建文件夹: {folder}")
    
    def setup_driver(self):
        """设置浏览器"""
        try:
            options = Options()
            options.headless = False
            
            # 反检测设置
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-extensions')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # 随机用户代理
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
            try:
                service = Service(executable_path="geckodriver.exe")
                self.driver = webdriver.Firefox(service=service, options=options)
            except TypeError:
                self.driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options)
            
            # 隐藏webdriver属性
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ 浏览器启动成功")
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            raise
    
    def wait_and_handle_captcha(self):
        """等待并处理验证码"""
        captcha_keywords = ["验证码", "captcha", "滑动验证", "点击验证", "拖动", "security"]
        
        for keyword in captcha_keywords:
            try:
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                if elements:
                    print(f"🔒 检测到验证码: {keyword}")
                    print("📋 请在浏览器中手动完成验证，验证完成后...")
                    input("按回车继续...")
                    return True
            except:
                pass
        return False
    
    def human_simulate(self):
        """模拟人类行为"""
        # 随机滚动
        for _ in range(random.randint(2, 5)):
            scroll_y = random.randint(100, 500)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_y});")
            time.sleep(random.uniform(0.5, 1.5))
        
        # 停顿
        time.sleep(random.uniform(1, 3))
    
    def extract_comprehensive_info(self, url):
        """提取完整商品信息"""
        try:
            print(f"🔍 开始提取商品信息: {url}")
            
            # 分步访问
            print("📍 步骤1: 访问1688首页...")
            self.driver.get("https://www.1688.com")
            time.sleep(random.uniform(3, 6))
            
            # 检查验证码
            self.wait_and_handle_captcha()
            
            print("📍 步骤2: 访问商品页面...")
            self.driver.get(url)
            time.sleep(random.uniform(5, 8))
            
            # 再次检查验证码
            if self.wait_and_handle_captcha():
                time.sleep(2)
            
            # 模拟人类浏览
            print("📍 步骤3: 模拟浏览行为...")
            self.human_simulate()
            
            # 提取信息
            print("📍 步骤4: 提取商品信息...")
            product_info = self.extract_all_data()
            
            # 保存页面源码
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f"logs/page_source_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            
            return product_info
            
        except Exception as e:
            print(f"❌ 提取失败: {e}")
            return None
    
    def extract_all_data(self):
        """提取所有可能的数据"""
        data = {
            'url': self.driver.current_url,
            'timestamp': datetime.now().isoformat(),
            'title': self.extract_title(),
            'price': self.extract_price(),
            'images': self.extract_images(),
            'supplier': self.extract_supplier(),
            'specifications': self.extract_specifications(),
            'description': self.extract_description(),
            'moq': self.extract_moq(),
            'contact_info': self.extract_contact_info()
        }
        
        return data
    
    def extract_title(self):
        """提取商品标题"""
        selectors = [
            'h1', '.offer-title', '.d-title', '.detail-title',
            '[class*="title"]', '[class*="name"]', '.product-name',
            'title', '[data-spm-anchor-id*="title"]'
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and len(text) > 3:
                    print(f"✅ 标题: {text[:50]}...")
                    return text
            except:
                continue
        
        # 尝试从页面标题提取
        try:
            page_title = self.driver.title
            if page_title and "1688" not in page_title:
                print(f"✅ 页面标题: {page_title}")
                return page_title
        except:
            pass
            
        print("❌ 未找到商品标题")
        return None
    
    def extract_price(self):
        """提取价格信息"""
        # 价格相关的CSS选择器
        price_selectors = [
            '.price', '.offer-price', '.d-price', '.unit-price',
            '[class*="price"]', '[data-testid*="price"]',
            '.price-range', '.price-original', '.price-now'
        ]
        
        prices = []
        
        # 尝试CSS选择器
        for selector in price_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and any(char in text for char in ['￥', '¥', '元', '.']):
                        prices.append(text)
            except:
                continue
        
        # 正则表达式提取
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        price_patterns = [
            r'￥[\d,.]+', r'¥[\d,.]+', r'\d+\.\d+元',
            r'\d+\.\d+-\d+\.\d+', r'\d+\.\d+起'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text)
            prices.extend(matches)
        
        if prices:
            # 去重并返回最相关的价格
            unique_prices = list(set(prices))
            print(f"✅ 价格: {unique_prices[:3]}")
            return unique_prices[:3]
        
        print("❌ 未找到价格信息")
        return None
    
    def extract_images(self):
        """提取商品图片"""
        images = []
        
        try:
            img_elements = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"📊 找到 {len(img_elements)} 个图片元素")
            
            for img in img_elements:
                try:
                    # 尝试不同的图片URL属性
                    img_url = None
                    for attr in ['src', 'data-src', 'data-original', 'data-lazy']:
                        url = img.get_attribute(attr)
                        if url and url.startswith('http') and any(ext in url for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            img_url = url
                            break
                    
                    if img_url:
                        alt = img.get_attribute('alt') or ''
                        width = img.get_attribute('width') or 0
                        height = img.get_attribute('height') or 0
                        
                        images.append({
                            'url': img_url,
                            'alt': alt,
                            'width': width,
                            'height': height
                        })
                        
                        if len(images) >= 10:  # 最多10张图片
                            break
                            
                except:
                    continue
            
            if images:
                print(f"✅ 提取到 {len(images)} 张图片")
                return images
                
        except Exception as e:
            print(f"❌ 图片提取失败: {e}")
        
        return []
    
    def extract_supplier(self):
        """提取供应商信息"""
        supplier_selectors = [
            '.company-name', '.supplier-name', '.shop-name',
            '[class*="company"]', '[class*="supplier"]', '[class*="shop"]'
        ]
        
        for selector in supplier_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and len(text) > 2:
                    print(f"✅ 供应商: {text}")
                    return text
            except:
                continue
        
        print("❌ 未找到供应商信息")
        return None
    
    def extract_specifications(self):
        """提取商品规格"""
        specs = {}
        
        # 尝试表格形式的规格
        try:
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    if len(cells) >= 2:
                        key = cells[0].text.strip()
                        value = cells[1].text.strip()
                        if key and value:
                            specs[key] = value
        except:
            pass
        
        if specs:
            print(f"✅ 规格参数: {len(specs)} 项")
            return specs
        
        print("❌ 未找到规格参数")
        return {}
    
    def extract_description(self):
        """提取商品描述"""
        desc_selectors = [
            '.description', '.detail-desc', '.product-desc',
            '[class*="desc"]', '[class*="detail"]'
        ]
        
        for selector in desc_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text and len(text) > 10:
                    print(f"✅ 描述: {text[:50]}...")
                    return text
            except:
                continue
        
        print("❌ 未找到商品描述")
        return None
    
    def extract_moq(self):
        """提取最小起订量"""
        moq_keywords = ["起订量", "最小", "MOQ", "起批"]
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        
        for keyword in moq_keywords:
            pattern = rf'{keyword}[：:]\s*(\d+)'
            match = re.search(pattern, page_text)
            if match:
                moq_value = match.group(1)
                print(f"✅ 起订量: {moq_value}")
                return moq_value
        
        print("❌ 未找到起订量信息")
        return None
    
    def extract_contact_info(self):
        """提取联系方式"""
        contact_info = {}
        
        # 查找电话号码
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        phone_pattern = r'1[3-9]\d{9}'
        phones = re.findall(phone_pattern, page_text)
        if phones:
            contact_info['phone'] = list(set(phones))[:3]
        
        print(f"✅ 联系信息: {len(contact_info)} 项")
        return contact_info
    
    def save_data(self, product_data, format_type='all'):
        """保存数据到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type in ['json', 'all']:
            # 保存为JSON
            json_file = f"data/product_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(product_data, f, ensure_ascii=False, indent=2)
            print(f"✅ JSON数据已保存: {json_file}")
        
        if format_type in ['csv', 'all']:
            # 保存为CSV
            csv_file = f"data/product_{timestamp}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['字段', '值'])
                for key, value in product_data.items():
                    if isinstance(value, (list, dict)):
                        value = str(value)
                    writer.writerow([key, value])
            print(f"✅ CSV数据已保存: {csv_file}")
    
    def download_images(self, images_data):
        """下载商品图片"""
        if not images_data:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for i, img_data in enumerate(images_data[:5]):  # 最多下载5张
            try:
                img_url = img_data['url']
                response = requests.get(img_url, timeout=10)
                
                if response.status_code == 200:
                    # 获取文件扩展名
                    ext = img_url.split('.')[-1].split('?')[0]
                    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                        ext = 'jpg'
                    
                    filename = f"images/product_{timestamp}_{i+1}.{ext}"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ 图片已下载: {filename}")
                    
            except Exception as e:
                print(f"❌ 图片下载失败 {i+1}: {e}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            input("\n📋 数据提取完成！按回车键关闭浏览器...")
            self.driver.quit()
            print("✅ 浏览器已关闭")

def main():
    """主函数"""
    #url = "https://detail.1688.com/offer/775610063728.html?offerId=775610063728&spm=a260k.home2025.recommendpart.18"
    #url = "https://detail.1688.com/offer/963863008803.html?spm=a26352.13672862.offerlist.9.6b095d62nOjRkt"
    url = "https://detail.1688.com/offer/816228014618.html?topicCode=202508210010000000000001696268&optName=%E7%83%AD%E7%82%B9%E5%95%86%E6%9C%BA&topicName=%E6%89%8B%E8%A1%A8%E5%AE%9D%E8%97%8F%E9%9B%86&item_id=816228014618&offerId=816228014618&object_id=816228014618&spm=a260k.29939364.recommend.0"
    
    crawler = None
    try:
        print("🚀 启动增强版1688商品信息提取器...")
        
        crawler = Enhanced1688Crawler()
        product_data = crawler.extract_comprehensive_info(url)
        
        if product_data:
            print("\n" + "="*60)
            print("📊 提取结果汇总:")
            print("="*60)
            
            for key, value in product_data.items():
                if isinstance(value, list) and value:
                    print(f"{key}: {len(value)} 项")
                elif isinstance(value, dict) and value:
                    print(f"{key}: {len(value)} 项")
                elif value:
                    display_value = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    print(f"{key}: {display_value}")
                else:
                    print(f"{key}: 未获取到")
            
            print("="*60)
            
            # 保存数据
            crawler.save_data(product_data)
            
            # 下载图片
            if product_data.get('images'):
                print("\n📸 开始下载商品图片...")
                crawler.download_images(product_data['images'])
            
            print("\n🎉 所有任务完成！")
            print("📁 输出文件位置:")
            print("  - data/ 文件夹: JSON和CSV数据文件")
            print("  - images/ 文件夹: 下载的商品图片")
            print("  - logs/ 文件夹: 页面源码备份")
            
        else:
            print("❌ 未能提取到商品信息")
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    main()
