#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量1688商品信息提取器
支持一次性处理多条商品链接
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

class Batch1688Crawler:
    def __init__(self):
        self.driver = None
        self.all_products_data = []
        self.setup_driver()
        self.setup_output_folders()
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def setup_output_folders(self):
        """创建输出文件夹"""
        folders = ['images', 'data', 'logs', 'batch_results']
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
        for _ in range(random.randint(2, 4)):
            scroll_y = random.randint(100, 400)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_y});")
            time.sleep(random.uniform(0.3, 1.0))
        
        # 停顿
        time.sleep(random.uniform(0.5, 2.0))
    
    def process_multiple_urls(self, urls):
        """批量处理多个URL"""
        total_urls = len(urls)
        print(f"🚀 开始批量处理 {total_urls} 个商品链接...")
        
        # 首次访问1688首页
        print("📍 初始化: 访问1688首页...")
        self.driver.get("https://www.1688.com")
        time.sleep(random.uniform(3, 6))
        self.wait_and_handle_captcha()
        
        successful_count = 0
        failed_urls = []
        
        for index, url in enumerate(urls, 1):
            try:
                print(f"\n{'='*60}")
                print(f"📊 进度: {index}/{total_urls} - 处理第 {index} 个商品")
                print(f"🔗 URL: {url}")
                print('='*60)
                
                # 处理单个商品
                product_data = self.extract_single_product(url, index)
                
                if product_data:
                    self.all_products_data.append(product_data)
                    successful_count += 1
                    print(f"✅ 第 {index} 个商品处理成功")
                    
                    # 保存单个商品数据（备份）
                    self.save_single_product(product_data, index)
                else:
                    failed_urls.append((index, url))
                    print(f"❌ 第 {index} 个商品处理失败")
                
                # 随机间隔，避免被检测
                if index < total_urls:
                    delay = random.uniform(3, 8)
                    print(f"⏳ 等待 {delay:.1f} 秒后处理下一个商品...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ 处理第 {index} 个商品时出错: {e}")
                failed_urls.append((index, url))
        
        # 处理结果汇总
        self.print_batch_summary(successful_count, total_urls, failed_urls)
        
        # 保存批量结果
        if self.all_products_data:
            self.save_batch_results()
        
        return self.all_products_data
    
    def extract_single_product(self, url, index):
        """提取单个商品信息"""
        try:
            print(f"🔍 访问商品页面...")
            self.driver.get(url)
            time.sleep(random.uniform(4, 7))
            
            # 检查验证码
            if self.wait_and_handle_captcha():
                time.sleep(2)
            
            # 模拟人类浏览
            self.human_simulate()
            
            # 提取信息
            product_info = self.extract_all_data(index)
            
            return product_info
            
        except Exception as e:
            print(f"❌ 提取第 {index} 个商品失败: {e}")
            return None
    
    def extract_all_data(self, index):
        """提取所有可能的数据"""
        data = {
            'index': index,
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
            
            for img in img_elements:
                try:
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
                        
                        if len(images) >= 8:  # 最多8张图片
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
        
        page_text = self.driver.find_element(By.TAG_NAME, "body").text
        phone_pattern = r'1[3-9]\d{9}'
        phones = re.findall(phone_pattern, page_text)
        if phones:
            contact_info['phone'] = list(set(phones))[:3]
        
        if contact_info:
            print(f"✅ 联系信息: {len(contact_info)} 项")
        return contact_info
    
    def save_single_product(self, product_data, index):
        """保存单个商品数据（备份）"""
        try:
            filename = f"data/product_{self.session_timestamp}_{index:03d}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(product_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存单个商品数据失败: {e}")
    
    def save_batch_results(self):
        """保存批量处理结果"""
        try:
            # 保存完整JSON数据
            json_file = f"batch_results/batch_{self.session_timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_products_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 批量JSON数据已保存: {json_file}")
            
            # 保存汇总CSV
            csv_file = f"batch_results/batch_summary_{self.session_timestamp}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['序号', 'URL', '商品标题', '价格', '供应商', '图片数量', '规格数量'])
                
                for product in self.all_products_data:
                    writer.writerow([
                        product.get('index', ''),
                        product.get('url', ''),
                        product.get('title', ''),
                        str(product.get('price', [])[:2]) if product.get('price') else '',
                        product.get('supplier', ''),
                        len(product.get('images', [])),
                        len(product.get('specifications', {}))
                    ])
            print(f"✅ 批量CSV汇总已保存: {csv_file}")
            
        except Exception as e:
            print(f"❌ 保存批量结果失败: {e}")
    
    def print_batch_summary(self, successful_count, total_urls, failed_urls):
        """打印批量处理结果汇总"""
        print(f"\n" + "="*80)
        print("📊 批量处理结果汇总")
        print("="*80)
        print(f"总链接数: {total_urls}")
        print(f"成功处理: {successful_count}")
        print(f"处理失败: {len(failed_urls)}")
        print(f"成功率: {(successful_count/total_urls)*100:.1f}%")
        
        if failed_urls:
            print(f"\n❌ 失败的链接:")
            for index, url in failed_urls:
                print(f"  {index}. {url}")
        
        print("="*80)
    
    def download_all_images(self):
        """下载所有商品图片"""
        if not self.all_products_data:
            return
        
        print(f"\n📸 开始下载所有商品图片...")
        
        for product in self.all_products_data:
            if product.get('images'):
                index = product.get('index', 0)
                self.download_product_images(product['images'], index)
    
    def download_product_images(self, images_data, product_index):
        """下载单个商品的图片"""
        for i, img_data in enumerate(images_data[:3]):  # 每个商品最多下载3张
            try:
                img_url = img_data['url']
                response = requests.get(img_url, timeout=10)
                
                if response.status_code == 200:
                    ext = img_url.split('.')[-1].split('?')[0]
                    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                        ext = 'jpg'
                    
                    filename = f"images/batch_{self.session_timestamp}_product_{product_index:03d}_{i+1}.{ext}"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"✅ 图片已下载: {filename}")
                    
            except Exception as e:
                print(f"❌ 商品 {product_index} 图片 {i+1} 下载失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            input("\n📋 批量处理完成！按回车键关闭浏览器...")
            self.driver.quit()
            print("✅ 浏览器已关闭")

def get_urls_from_user():
    """从用户输入获取URL列表"""
    print("🔗 请输入商品链接（每行一个，输入完成后按回车+Ctrl+D结束）:")
    print("或者直接粘贴多行链接：")
    print("-" * 60)
    
    urls = []
    try:
        while True:
            line = input().strip()
            if line:
                if line.startswith('http') and '1688.com' in line:
                    urls.append(line)
                    print(f"✅ 已添加第 {len(urls)} 个链接")
                else:
                    print("❌ 请输入有效的1688商品链接")
    except EOFError:
        pass
    
    return urls

def get_urls_from_file():
    """从input.txt文件读取URL列表"""
    filename = "input.txt"
    
    # 如果文件不存在，创建示例文件
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("https://detail.1688.com/offer/775610063728.html?offerId=775610063728&spm=a260k.home2025.recommendpart.18\n")
            f.write("# 请在上方添加更多1688商品链接，每行一个\n")
            f.write("# 以 # 开头的行会被忽略\n")
        print(f"✅ 已创建示例文件: {filename}")
        print("请编辑该文件添加更多链接，然后重新运行程序")
        return []
    
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if 'detail.1688.com' in line:
                        urls.append(line)
                        print(f"✅ 第 {line_num} 行: 已添加链接")
                    else:
                        print(f"❌ 第 {line_num} 行不是有效的1688链接: {line[:50]}...")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
    
    return urls

def main():
    """主函数"""
    print("🚀 批量1688商品信息提取器")
    print("="*50)
    
    # 选择输入方式
    print("请选择链接输入方式:")
    print("1. 手动输入链接")
    print("2. 从文件读取链接 (input.txt)")
    
    while True:
        choice = input("请输入选择 (1 或 2): ").strip()
        if choice in ['1', '2']:
            break
        print("❌ 请输入 1 或 2")
    
    # 获取URL列表
    if choice == '1':
        urls = get_urls_from_user()
    else:
        urls = get_urls_from_file()
    
    if not urls:
        print("❌ 没有找到有效的链接，程序退出")
        return
    
    print(f"\n✅ 共找到 {len(urls)} 个有效链接")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url[:60]}...")
    
    # 确认开始处理
    confirm = input(f"\n是否开始处理这 {len(urls)} 个链接？(y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 用户取消操作")
        return
    
    # 开始批量处理
    crawler = None
    try:
        crawler = Batch1688Crawler()
        results = crawler.process_multiple_urls(urls)
        
        if results:
            # 下载图片
            download_images = input("\n是否下载所有商品图片？(y/n): ").strip().lower()
            if download_images == 'y':
                crawler.download_all_images()
            
            print(f"\n🎉 批量处理完成！")
            print(f"📁 输出文件位置:")
            print(f"  - batch_results/ 文件夹: 批量处理结果")
            print(f"  - data/ 文件夹: 单个商品JSON文件")
            print(f"  - images/ 文件夹: 商品图片")
        else:
            print("❌ 没有成功处理任何商品")
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    main()
