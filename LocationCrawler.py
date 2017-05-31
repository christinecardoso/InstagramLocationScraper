import argparse
from sys import platform
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from datetime import datetime
from datetime import timedelta
import dateutil.parser



# URLS
HOST = "https://www.instagram.com"
RELATIVE_URL_LOCATION = "/explore/locations/"

# SELENIUM CSS SELECTOR
CSS_LOAD_MORE = "a._8imhp._glz1g"
CSS_DATE = "a time"

# CLASS NAMES
CLOSE_BUTTON = "_3eajp"
POST = "_ovg3g"
SEE_MORE = "_jn623"
LOCATION_LINK = "a._3hq20"

# JAVASCRIPT COMMANDS
SCROLL_UP = "window.scrollTo(0, 0);"
SCROLL_DOWN = "window.scrollTo(0, document.body.scrollHeight);"

#path for the scraper profile
CHROME_PROFILE_PATH = ".\Scraper"

class LocationScraper(object):
	def __init__(self):
		options = webdriver.ChromeOptions()
		options.add_argument("user-data-dir=" + CHROME_PROFILE_PATH)

		if platform == "win32":
			self.driver = webdriver.Chrome(executable_path = "./chromedriverWIN.exe", chrome_options = options)
		elif platform == "darwin":
			self.driver = webdriver.Chrome(executable_path = "./chromedriverMAC", chrome_options=options)
		else:
			print("neither Windows nor Mac detected")

	def quit(self):
		self.driver.quit()

	def scrape(self, dirPrefix, location, dateTo, dateFrom):
		self.browseTargetPage(location)
		postList = self.scrollToDate(dateFrom)
		firstPostIndex = self.findFirstPost(dateFrom, postList)
		lastPostIndex = self.findLastPost(dateTo, postList)
		return firstPostIndex - lastPostIndex

	def browseTargetPage(self, location):
		targetURL = HOST + RELATIVE_URL_LOCATION + location
		self.driver.get(targetURL)

	#scrolls until an imager older than dateFrom is found
	def scrollToDate(self, dateFrom):
		self.driver.execute_script(SCROLL_DOWN)
		loadmore = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, CSS_LOAD_MORE)))
		loadmore.click()
		scrollMore = True
		while(True):
			postList = self.driver.find_elements_by_class_name(POST)
			postList[-1].click()
			dateElement = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, CSS_DATE)))
			date = dateutil.parser.parse(dateElement.get_attribute("datetime"), ignoretz=True)
			self.driver.find_element_by_class_name(CLOSE_BUTTON).click()
			if(date <= dateFrom):
				return postList
			self.driver.execute_script(SCROLL_DOWN)

	def findFirstPost(self, dateFrom, postList):
		for i in range(1, len(postList)): #start looking from the back
			postList[-i].click()
			dateElement = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, CSS_DATE)))
			date = dateutil.parser.parse(dateElement.get_attribute("datetime"), ignoretz=True)
			self.driver.find_element_by_class_name(CLOSE_BUTTON).click()
			if (date >= dateFrom):
				return len(postList) - i

	def findLastPost(self, dateTo, postList):
		for i in range(9, len(postList)): #first 9 posts are "Top Posts"
			postList[i].click()
			dateElement = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, CSS_DATE)))
			date = dateutil.parser.parse(dateElement.get_attribute("datetime"), ignoretz=True)
			self.driver.find_element_by_class_name(CLOSE_BUTTON).click()
			if (date <= dateTo):
				return i

	def getLocations(self, city):
		self.browseTargetPage(city)
		while(True):
			try:
				seeMore = WebDriverWait(self.driver,2).until(EC.presence_of_element_located((By.CLASS_NAME, SEE_MORE)))
			except:
				break
			self.driver.execute_script(SCROLL_DOWN)
			time.sleep(0.5)
			try:
				seeMore.click()
			except:
				pass
		locationLinks = []
		for element in self.driver.find_elements_by_css_selector(LOCATION_LINK):
			locationLinks.append(element.get_attribute("href").replace(HOST + RELATIVE_URL_LOCATION, ""))
		print(len(locationLinks))
		print(locationLinks[0])




def main():
	#   Arguments  #
	parser = argparse.ArgumentParser(description="Instagram Location Scraper")
	#parser.add_argument("-df", "--dateFrom", type=str, default="now - 1h", help="Date from which to scrape")
	parser.add_argument("-d", "--date", type=str, default="now", help="Date up till which to scrape")
	parser.add_argument("-l", "--location", type=str, default="no", help="Location Number eg. 214335386 for Englischer Garten")
	parser.add_argument("-t", "--timeWindow", type=float, default=1.0, help="Timeframe to check number of posts")
	parser.add_argument("-c", "--city", type=str, default="no", help="City to scrape location links from, eg c579270 for Munich")
	parser.add_argument("-dir", "--dirPrefix", type=str, default="./data/", help="directory to save results")
	

	args = parser.parse_args()
	#  End Argparse #

	if(args.date == "now"):
		dateTo = datetime.utcnow()
	else:
		dateTo = dateutil.parser.parse(dateTo, ignoretz=True)
	dateFrom = dateTo - timedelta(hours=args.timeWindow)

	scraper = LocationScraper()
	
	if(args.city != "no"):
		locations = scraper.getLocations(args.city)
		file = open(args.city.strip('/') + "_Locations", "w+")
		for loc in locations:
			file.write(loc)
	if(args.location != "no"):
		print("Scraping location " + args.location + " for number of pictures posted between " + str(dateFrom) + " and " + str(dateTo))
		numPosts = scraper.scrape(dirPrefix=args.dirPrefix, location=args.location, dateTo=dateTo, dateFrom=dateFrom)
		print(str(numPosts))
		

main()