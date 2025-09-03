import time
import logging

# Selenium import
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from base64 import b64encode


class SeleniumHelper:

	proxy_type = None
	proxy_host = None
	proxy_port = None
	driver = None
	TIMEOUT = None
	WAIT = None
	DELAY = None

	db = None

	def __init__(self, driver_path, proxy, headless):
		# Create Firefox options (simplified for compatibility)
		options = Options()
		options.headless = headless
		
		# Try to create driver with different Selenium API versions
		try:
			# Method 1: New Selenium 4.x API with Service
			service = Service(executable_path=driver_path)
			self.driver = webdriver.Firefox(service=service, options=options)
		except TypeError:
			# Method 2: Old Selenium 3.x API with executable_path
			self.driver = webdriver.Firefox(executable_path=driver_path, options=options)
		except Exception as e:
			print(f"Error creating Firefox driver: {e}")
			# Method 3: Fallback without options
			try:
				self.driver = webdriver.Firefox(executable_path=driver_path)
			except:
				raise Exception(f"Failed to create Firefox driver. Please check geckodriver.exe and Firefox installation.")
		
		if self.TIMEOUT:
			self.driver.set_page_load_timeout(self.TIMEOUT)

	def __del__(self):
		if self.driver:
			self.close()

	def src(self):
		return self.driver.page_source

	def loadPage(self, page):
		try:
			self.driver.get(page)
			time.sleep(self.DELAY)
		except Exception as e:
			raise Exception("Can't load page {} - {}".format(page, e))

	def loadAndWait(self, url, selector, wait=None):
		wait = self.WAIT if wait is None else wait
		self.loadPage(url)
		return self.waitShowElement(selector, wait)

	def waitShowElement(self, selector, wait=None):
		try:
			wait = self.WAIT if wait is None else wait
			wait = WebDriverWait(self.driver, wait)
			return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
		except Exception as e:
			raise Exception("Error loading element: {}".format(e))

	def waitShowElementByXPath(self, xpath, wait=None):
		try:
			wait = self.WAIT if wait is None else wait
			wait = WebDriverWait(self.driver, wait)
			return wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
		except Exception as e:
			raise Exception("Error loading element: {}".format(e))

	def getElementFrom(self, fromObject, selector):
		try:
			return fromObject.find_element(By.CSS_SELECTOR, selector)
		except NoSuchElementException:
			return None

	def getElementsFrom(self, fromObject, selector):
		try:
			return fromObject.find_elements(By.CSS_SELECTOR, selector)
		except NoSuchElementException:
			return None

	def getElement(self, selector):
		return self.getElementFrom(self.driver, selector)

	def getElements(self, selector):
		return self.getElementsFrom(self.driver, selector)

	def getElementFromValue(self, fromObject, selector):
		element = self.getElementFrom(fromObject, selector)
		return self.getValue(element)

	def getElementValue(self, selector):
		element = self.getElement(selector)
		if element:
			return self.getValue(element)
		return None

	def waitAndGetElementValue(self, selector):
		if not self.waitShowElement(selector):
			return None
		return self.getElementValue(selector)

	def getValue(self, element):
		if element:
			return element.text
		return None

	def getAttribute(self, element, attribute):
		if element:
			return element.get_attribute(attribute)
		return None

	def changeAttribute(self, element, attr, value):
		self.driver.execute_script("arguments[0].setAttribute('{}','{}')".format(attr, value), element)

	def getElementAttribute(self, selector, attribute):
		element = self.getElement(selector)
		if element:
			return self.getAttribute(element, attribute)
		return None

	def click(self, element):
		self.moveToElement(element)
		actions = webdriver.ActionChains(self.driver)
		actions.move_to_element(element)
		actions.click(element)
		actions.perform()

	def moveToElement(self, element):
		self.driver.execute_script("return arguments[0].scrollIntoView();", element)
		actions = webdriver.ActionChains(self.driver)
		actions.move_to_element(element)
		actions.perform()

	def scrollDown(self):
		self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

	def close(self):
		self.driver.quit()