#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化版批量1688商品信息提取器
直接读取input.txt文件中的链接，一行一个
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
from selenium.common.exceptions import NoSuchElementException
import requests

class SimpleBatch1688:
    def __init__(self):
        self.driver = None
        self.all_products_data = []
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.setup_output_folders()
        self.setup_driver()
    
    def setup_output_folders(self):
        """创建输出文件夹"""
        folders = ['images', 'data', 'logs', 'batch_results']
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
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
            options.add_argument('--window-size=1920,1080')
            
            # 随机用户代理
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
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
    
    def read_urls_from_input(self):
        """从input.txt文件读取链接"""
        filename = "input.txt"
        
        if not os.path.exists(filename):
            print(f"❌ 找不到 {filename} 文件")
            print("请创建 input.txt 文件，并在其中添加1688商品链接，每行一个")
            return []
        
        urls = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if 'detail.1688.com' in line:
                            urls.append(line)
                            print(f"✅ 第 {line_num} 行: 已读取链接")
                        elif line:  # 不为空但不是1688链接
                            print(f"❌ 第 {line_num} 行不是有效的1688链接: {line[:50]}...")
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
        
        return urls
    
    def wait_and_handle_captcha(self):
        """等待并处理验证码"""
        captcha_keywords = ["验证码", "captcha", "滑动验证", "点击验证", "拖动"]
        
        for keyword in captcha_keywords:
            try:
                elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{keyword}')]")
                if elements:
                    print(f"🔒 检测到验证码: {keyword}")
                    print("📋 请在浏览器中手动完成验证，验证完成后按回车继续...")
                    input()
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
        time.sleep(random.uniform(0.5, 2.0))
    
    def process_all_urls(self, urls):
        """处理所有URL"""
        total_urls = len(urls)
        print(f"\n🚀 开始处理 {total_urls} 个商品链接...")
        
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
                print(f"🔗 {url[:80]}...")
                print('='*60)
                
                # 处理单个商品
                product_data = self.extract_single_product(url, index)
                
                if product_data:
                    self.all_products_data.append(product_data)
                    successful_count += 1
                    print(f"✅ 第 {index} 个商品处理成功")
                    
                    # 保存单个商品数据
                    self.save_single_product(product_data, index)
                else:
                    failed_urls.append((index, url))
                    print(f"❌ 第 {index} 个商品处理失败")
                
                # 随机间隔
                if index < total_urls:
                    delay = random.uniform(3, 8)
                    print(f"⏳ 等待 {delay:.1f} 秒后处理下一个商品...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ 处理第 {index} 个商品时出错: {e}")
                failed_urls.append((index, url))
        
        # 处理结果汇总
        self.print_summary(successful_count, total_urls, failed_urls)
        
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
            product_info = {
                'index': index,
                'url': self.driver.current_url,
                'timestamp': datetime.now().isoformat(),
                'title': self.extract_title(),
                'price': self.extract_price(),
                'images': self.extract_images(),
                'supplier': self.extract_supplier(),
                'specifications': self.extract_specifications(),
                'moq': self.extract_moq()
            }
            
            return product_info
            
        except Exception as e:
            print(f"❌ 提取第 {index} 个商品失败: {e}")
            return None
    
    def extract_title(self):
        """提取商品标题"""
        selectors = [
            'h1', '.offer-title', '.d-title', '.detail-title',
            '[class*="title"]', '[class*="name"]', '.product-name'
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
        prices = []
        
        # CSS选择器提取
        price_selectors = [
            '.price', '.offer-price', '.d-price', '.unit-price',
            '[class*="price"]', '.price-range', '.price-original', '.price-now'
        ]
        
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
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            price_patterns = [
                r'￥[\d,.]+', r'¥[\d,.]+', r'\d+\.\d+元',
                r'\d+\.\d+-\d+\.\d+', r'\d+\.\d+起'
            ]
            
            for pattern in price_patterns:
                matches = re.findall(pattern, page_text)
                prices.extend(matches)
        except:
            pass
        
        if prices:
            unique_prices = list(set(prices))
            print(f"✅ 价格: {unique_prices[:3]}")
            return unique_prices[:3]
        
        print("❌ 未找到价格信息")
        return None
    
    def extract_images(self):
        """提取商品的全部图片"""
        images = []
        seen_urls = set()  # 用于去重
        
        try:
            print("🔍 开始提取商品图片...")
            
            # 1. 提取所有img标签的图片
            img_elements = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"📊 找到 {len(img_elements)} 个img元素")
            
            for img in img_elements:
                try:
                    img_url = None
                    # 尝试多种图片URL属性
                    for attr in ['src', 'data-src', 'data-original', 'data-lazy', 'data-img', 'data-url']:
                        url = img.get_attribute(attr)
                        if url and url.startswith('http'):
                            # 检查是否为图片URL
                            if any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp']):
                                img_url = url
                                break
                            # 检查阿里云图片服务的URL模式
                            elif 'alicdn.com' in url or 'img.alicdn.com' in url:
                                img_url = url
                                break
                    
                    if img_url and img_url not in seen_urls:
                        # 过滤掉明显的图标和装饰图片
                        if self.is_product_image(img_url, img):
                            images.append({
                                'url': img_url,
                                'alt': img.get_attribute('alt') or '',
                                'width': img.get_attribute('width') or '0',
                                'height': img.get_attribute('height') or '0',
                                'class': img.get_attribute('class') or '',
                                'source': 'img_tag'
                            })
                            seen_urls.add(img_url)
                            
                except Exception as e:
                    continue
            
            # 2. 从页面源码中提取图片URL（正则表达式）
            try:
                page_source = self.driver.page_source
                
                # 阿里云图片URL模式
                alicdn_patterns = [
                    r'https://[^"\'\s]*\.alicdn\.com[^"\'\s]*\.(?:jpg|jpeg|png|webp|gif)',
                    r'https://cbu[^"\'\s]*\.alicdn\.com[^"\'\s]*\.(?:jpg|jpeg|png|webp|gif)',
                    r'https://img[^"\'\s]*\.alicdn\.com[^"\'\s]*\.(?:jpg|jpeg|png|webp|gif)'
                ]
                
                for pattern in alicdn_patterns:
                    matches = re.findall(pattern, page_source, re.IGNORECASE)
                    for url in matches:
                        if url not in seen_urls and self.is_valid_product_image_url(url):
                            images.append({
                                'url': url,
                                'alt': '',
                                'width': '0',
                                'height': '0',
                                'class': '',
                                'source': 'regex_extract'
                            })
                            seen_urls.add(url)
                            
            except Exception as e:
                print(f"❌ 正则提取图片失败: {e}")
            
            # 3. 查找特定的商品图片容器
            image_containers = [
                '.offer-img', '.product-img', '.detail-img', '.gallery-img',
                '[class*="image"]', '[class*="photo"]', '[class*="pic"]',
                '.img-list', '.image-list', '.photo-list'
            ]
            
            for container_selector in image_containers:
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
                    for container in containers:
                        container_imgs = container.find_elements(By.TAG_NAME, "img")
                        for img in container_imgs:
                            img_url = self.get_best_image_url(img)
                            if img_url and img_url not in seen_urls:
                                images.append({
                                    'url': img_url,
                                    'alt': img.get_attribute('alt') or '',
                                    'width': img.get_attribute('width') or '0',
                                    'height': img.get_attribute('height') or '0',
                                    'class': img.get_attribute('class') or '',
                                    'source': f'container_{container_selector}'
                                })
                                seen_urls.add(img_url)
                except:
                    continue
            
            # 4. 滚动页面加载更多图片
            self.scroll_to_load_images()
            time.sleep(2)
            
            # 再次检查是否有新的图片加载
            new_img_elements = self.driver.find_elements(By.TAG_NAME, "img")
            for img in new_img_elements:
                try:
                    img_url = self.get_best_image_url(img)
                    if img_url and img_url not in seen_urls and self.is_product_image(img_url, img):
                        images.append({
                            'url': img_url,
                            'alt': img.get_attribute('alt') or '',
                            'width': img.get_attribute('width') or '0',
                            'height': img.get_attribute('height') or '0',
                            'class': img.get_attribute('class') or '',
                            'source': 'lazy_load'
                        })
                        seen_urls.add(img_url)
                except:
                    continue
            
            if images:
                print(f"✅ 提取到 {len(images)} 张商品图片")
                # 按图片质量排序（优先选择大尺寸图片）
                images = self.sort_images_by_quality(images)
                return images
            else:
                print("❌ 未找到商品图片")
                return []
                
        except Exception as e:
            print(f"❌ 图片提取失败: {e}")
            return []
    
    def get_best_image_url(self, img_element):
        """获取图片元素的最佳URL"""
        # 按优先级尝试不同属性
        attributes = ['data-original', 'data-src', 'data-lazy', 'src', 'data-img', 'data-url']
        
        for attr in attributes:
            try:
                url = img_element.get_attribute(attr)
                if url and url.startswith('http'):
                    # 优先选择高清图片
                    if '_b.jpg' in url or '_large' in url or '_big' in url:
                        return url
                    elif any(ext in url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                        return url
                    elif 'alicdn.com' in url:
                        return url
            except:
                continue
        return None
    
    def is_product_image(self, img_url, img_element=None):
        """判断是否为商品相关图片"""
        # 排除明显的装饰图片和图标
        exclude_patterns = [
            'icon', 'logo', 'btn', 'button', 'arrow', 'star', 'rating',
            'header', 'footer', 'nav', 'menu', 'banner', 'ad',
            'sprite', 'background', 'bg', 'decoration'
        ]
        
        # 检查URL中是否包含排除模式
        url_lower = img_url.lower()
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
        
        # 检查图片尺寸（如果可用）
        if img_element:
            try:
                width = int(img_element.get_attribute('width') or 0)
                height = int(img_element.get_attribute('height') or 0)
                
                # 排除太小的图片（可能是图标）
                if width > 0 and height > 0 and (width < 50 or height < 50):
                    return False
                    
                # 排除明显的装饰图片尺寸
                if width > 0 and height > 0 and width * height < 2500:  # 50x50以下
                    return False
            except:
                pass
        
        # 优先选择阿里云图片服务的图片
        if 'alicdn.com' in img_url:
            return True
            
        # 检查是否为常见图片格式
        if any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.webp']):
            return True
            
        return False
    
    def is_valid_product_image_url(self, url):
        """验证是否为有效的商品图片URL"""
        if not url or len(url) < 20:
            return False
            
        # 必须是HTTPS
        if not url.startswith('https://'):
            return False
            
        # 必须包含图片扩展名或阿里云域名
        url_lower = url.lower()
        if not (any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']) or 'alicdn.com' in url_lower):
            return False
            
        # 排除明显的非商品图片
        exclude_keywords = ['icon', 'logo', 'btn', 'arrow', 'star', 'sprite']
        if any(keyword in url_lower for keyword in exclude_keywords):
            return False
            
        return True
    
    def scroll_to_load_images(self):
        """滚动页面以加载懒加载的图片"""
        try:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            
            # 滚动到页面顶部
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # 分段滚动
            viewport_height = self.driver.execute_script("return window.innerHeight")
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            
            current_position = 0
            while current_position < page_height:
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(0.5)
                current_position += viewport_height
                
        except Exception as e:
            print(f"❌ 滚动加载图片失败: {e}")
    
    def sort_images_by_quality(self, images):
        """按图片质量排序"""
        def get_image_priority(img):
            url = img['url'].lower()
            priority = 0
            
            # 优先级加分项
            if '_b.jpg' in url or '_large' in url or '_big' in url:
                priority += 100
            if 'cbu01.alicdn.com' in url:
                priority += 50
            if any(dim in url for dim in ['800', '600', '400']):
                priority += 30
            if img['source'] == 'img_tag':
                priority += 20
            
            # 根据尺寸加分
            try:
                width = int(img.get('width', 0))
                height = int(img.get('height', 0))
                if width > 200 and height > 200:
                    priority += 40
                elif width > 100 and height > 100:
                    priority += 20
            except:
                pass
                
            return priority
        
        return sorted(images, key=get_image_priority, reverse=True)
    
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
    
    def extract_moq(self):
        """提取最小起订量"""
        try:
            moq_keywords = ["起订量", "最小", "MOQ", "起批"]
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            for keyword in moq_keywords:
                pattern = rf'{keyword}[：:]\s*(\d+)'
                match = re.search(pattern, page_text)
                if match:
                    moq_value = match.group(1)
                    print(f"✅ 起订量: {moq_value}")
                    return moq_value
        except:
            pass
        
        print("❌ 未找到起订量信息")
        return None
    
    def save_single_product(self, product_data, index):
        """保存单个商品数据"""
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
    
    def print_summary(self, successful_count, total_urls, failed_urls):
        """打印处理结果汇总"""
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
                print(f"  {index}. {url[:60]}...")
        
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
        """下载单个商品的所有图片"""
        if not images_data:
            print(f"❌ 商品 {product_index} 没有图片可下载")
            return
            
        print(f"📸 开始下载商品 {product_index} 的 {len(images_data)} 张图片...")
        
        downloaded_count = 0
        failed_count = 0
        
        for i, img_data in enumerate(images_data):  # 下载所有图片
            try:
                img_url = img_data['url']
                
                # 发送请求下载图片
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Referer': 'https://detail.1688.com/',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8'
                }
                
                response = requests.get(img_url, timeout=15, headers=headers)
                
                if response.status_code == 200:
                    # 获取文件扩展名
                    ext = self.get_image_extension(img_url, response)
                    
                    # 生成文件名
                    source = img_data.get('source', 'unknown')
                    filename = f"images/product_{product_index:03d}_{i+1:02d}_{source}.{ext}"
                    
                    # 保存图片
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    # 获取图片大小
                    file_size = len(response.content)
                    size_kb = file_size / 1024
                    
                    print(f"✅ 图片 {i+1}/{len(images_data)}: {filename} ({size_kb:.1f}KB)")
                    downloaded_count += 1
                    
                    # 添加小延迟避免请求过快
                    time.sleep(random.uniform(0.2, 0.5))
                    
                else:
                    print(f"❌ 图片 {i+1} 下载失败: HTTP {response.status_code}")
                    failed_count += 1
                    
            except Exception as e:
                print(f"❌ 图片 {i+1} 下载失败: {e}")
                failed_count += 1
        
        print(f"📊 商品 {product_index} 图片下载完成: 成功 {downloaded_count} 张, 失败 {failed_count} 张")
    
    def get_image_extension(self, url, response=None):
        """获取图片文件扩展名"""
        # 首先从URL获取扩展名
        url_lower = url.lower()
        for ext in ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp']:
            if f'.{ext}' in url_lower:
                return ext
        
        # 如果URL中没有扩展名，从响应头获取
        if response:
            content_type = response.headers.get('content-type', '').lower()
            if 'jpeg' in content_type or 'jpg' in content_type:
                return 'jpg'
            elif 'png' in content_type:
                return 'png'
            elif 'webp' in content_type:
                return 'webp'
            elif 'gif' in content_type:
                return 'gif'
        
        # 默认返回jpg
        return 'jpg'
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            input("\n📋 批量处理完成！按回车键关闭浏览器...")
            self.driver.quit()
            print("✅ 浏览器已关闭")

def main():
    """主函数"""
    print("🚀 简化版批量1688商品信息提取器")
    print("📁 自动读取 input.txt 文件中的链接")
    print("="*60)
    
    crawler = None
    try:
        crawler = SimpleBatch1688()
        
        # 读取链接
        urls = crawler.read_urls_from_input()
        
        if not urls:
            print("❌ 没有找到有效的链接")
            print("请在 input.txt 文件中添加1688商品链接，每行一个")
            return
        
        print(f"\n✅ 共找到 {len(urls)} 个有效链接:")
        for i, url in enumerate(urls, 1):
            print(f"  {i}. {url[:60]}...")
        
        # 确认开始处理
        confirm = input(f"\n是否开始处理这 {len(urls)} 个链接？(y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ 用户取消操作")
            return
        
        # 开始批量处理
        results = crawler.process_all_urls(urls)
        
        if results:
            # 询问是否下载图片
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
