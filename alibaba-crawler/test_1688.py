#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
1688商品信息提取测试脚本
用于测试从1688网站提取商品信息的可行性
"""

import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
import os

class Product1688Crawler:
    def __init__(self):
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """设置Firefox浏览器"""
        try:
            options = Options()
            options.headless = False  # 设为False以便观察过程
            
            # 兼容不同版本的Selenium
            try:
                service = Service(executable_path="geckodriver.exe")
                self.driver = webdriver.Firefox(service=service, options=options)
            except TypeError:
                self.driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options)
            
            print("✅ Firefox浏览器启动成功")
            
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            raise
    
    def extract_product_info(self, url):
        """提取商品信息"""
        try:
            print(f"🔍 开始访问: {url}")
            self.driver.get(url)
            time.sleep(3)  # 等待页面加载
            
            product_info = {}
            
            # 尝试提取商品标题
            title_selectors = [
                'h1.d-title',
                '.d-title',
                'h1',
                '.offer-title',
                '.product-title'
            ]
            product_info['title'] = self.extract_text_by_selectors(title_selectors, "商品标题")
            
            # 尝试提取价格信息
            price_selectors = [
                '.price-range',
                '.price-original',
                '.price-now',
                '.price',
                '[data-testid="price"]'
            ]
            product_info['price'] = self.extract_text_by_selectors(price_selectors, "价格")
            
            # 尝试提取商品图片
            image_selectors = [
                '.detail-gallery img',
                '.offer-img img',
                '.product-img img',
                'img[data-src]'
            ]
            product_info['images'] = self.extract_images(image_selectors)
            
            # 尝试提取供应商信息
            supplier_selectors = [
                '.company-name',
                '.supplier-name',
                '.shop-name'
            ]
            product_info['supplier'] = self.extract_text_by_selectors(supplier_selectors, "供应商")
            
            # 尝试提取起订量
            moq_selectors = [
                '.amount-range',
                '.min-order',
                '.moq'
            ]
            product_info['moq'] = self.extract_text_by_selectors(moq_selectors, "起订量")
            
            return product_info
            
        except Exception as e:
            print(f"❌ 提取商品信息失败: {e}")
            return None
    
    def extract_text_by_selectors(self, selectors, info_type):
        """通过多个选择器尝试提取文本"""
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text.strip()
                if text:
                    print(f"✅ 成功提取{info_type}: {text[:50]}...")
                    return text
            except NoSuchElementException:
                continue
        
        print(f"❌ 无法提取{info_type}")
        return None
    
    def extract_images(self, selectors):
        """提取商品图片URL"""
        images = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # 尝试不同的图片URL属性
                    for attr in ['src', 'data-src', 'data-original']:
                        img_url = element.get_attribute(attr)
                        if img_url and img_url.startswith('http'):
                            images.append(img_url)
                            break
                if images:
                    print(f"✅ 成功提取图片数量: {len(images)}")
                    return images[:5]  # 最多返回5张图片
            except NoSuchElementException:
                continue
        
        print("❌ 无法提取图片")
        return []
    
    def save_to_csv(self, product_info, filename="1688_result.csv"):
        """保存结果到CSV文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("标题,价格,供应商,起订量,图片数量,图片URLs\n")
                
                title = product_info.get('title', '无')
                price = product_info.get('price', '无')
                supplier = product_info.get('supplier', '无')
                moq = product_info.get('moq', '无')
                images = product_info.get('images', [])
                image_count = len(images)
                image_urls = ';'.join(images)
                
                f.write(f'"{title}","{price}","{supplier}","{moq}",{image_count},"{image_urls}"\n')
            
            print(f"✅ 结果已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("✅ 浏览器已关闭")

def main():
    """主函数"""
    # 1688商品URL
    url = "https://detail.1688.com/offer/775610063728.html?offerId=775610063728&spm=a260k.home2025.recommendpart.18"
    
    crawler = None
    try:
        print("🚀 开始1688商品信息提取测试...")
        
        crawler = Product1688Crawler()
        product_info = crawler.extract_product_info(url)
        
        if product_info:
            print("\n📊 提取结果:")
            print("="*50)
            for key, value in product_info.items():
                if isinstance(value, list):
                    print(f"{key}: {len(value)} 项")
                else:
                    print(f"{key}: {value}")
            print("="*50)
            
            # 保存结果
            crawler.save_to_csv(product_info)
            print("\n🎉 测试完成！")
        else:
            print("❌ 未能提取到商品信息")
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
    
    finally:
        if crawler:
            crawler.close()

if __name__ == "__main__":
    main()