# beauty_soup.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pyshorteners
import csv
import re


def shorten_url(long_url):
    # Initialize the Shortener class with the desired URL shortening service
    s = pyshorteners.Shortener()
    # Shorten the URL
    shortened_url = s.tinyurl.short(long_url)  

    return shortened_url

# main page scraping function that retrieves page HTML
def scrape(url):
    driver.get(url)
    get_url = driver.current_url
    # VITAL: page must wait till div below is loaded as HTML will not be properly loaded otherwise
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'l1ovpqvx.c1ytbx3a.dir.dir-ltr')))
    
    if get_url == url: 
        page_source = driver.page_source
        
    soup = BeautifulSoup(page_source,features='lxml')
    return soup

listing_arr = [] # list that will store listings

def placeListings(listings, links, date):
    
    for n in range(len(listings)):
        info = listings[n].contents
        location = info[0].text
        description = info[1].text
        bedrooms = info[2].text      
        dates = date
        price_per_night = info[3].text
        link = shorten_url('https://www.airbnb.com'+links[n]['href'])

        if len(info) < 5 or info[4].text == "":
            rating = "no rating"
        else:
            rating = info[4].text
            
        price = re.search("\$\d+.?per night", price_per_night).group(0)
        if price == None:
            price_per_night = "No listed pirce"
        else:
            price_per_night = re.search("\$\d+", price).group(0)   
        
        val = {
            'link': link,
            'location': location,
            'owner/description': description,
            'bedrooms/amenities': bedrooms,
            'dates': dates,
            'price_per_night': price_per_night,
            'rating/reviews': rating
        }
        
        listing_arr.append(val)


if __name__=="__main__":
    options = Options()
    options.headless = True
    options.add_argument("--headless=new")
    path = '/usr/bin/chromedriver'
    options.add_argument(f"webdriver.chrome.driver={path}")

    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 4)
    
    url = input("Enter a Airbnb url: ")
    num_pages = int(input("Enter amount of pages to search: "))
    
    if url == None:
        print("invalid url")
        exit()

    for page in range(num_pages):
        
        if url == None:
            break
       
        # assigns new page to be scraped and updates driver
        curr_site = scrape(url) 
        # finds all listings on a page
        listings = curr_site.find_all('div','g1qv1ctd c1v0rf5q dir dir-ltr')
        # finds all listings links on a page
        links = curr_site.find_all('a', 'l1ovpqvx bn2bl2p dir dir-ltr')
        # finds all dates for listings 
        date = curr_site.find_all('div', 'f16sug5q dir dir-ltr')[1].text
        # places listings into list
        placeListings(listings, links, date)
        # updates page to be searched via scrollbar near the bottom of the page
        url = driver.find_element(By.CLASS_NAME, 'l1ovpqvx.c1ytbx3a.dir.dir-ltr').get_attribute("href")
    

    # returns price as an integer excluding $
    def cmp_list(listing):
        return int(listing['price_per_night'][1:])

    listing_arr.sort(key=cmp_list)  # sorts listings in ascending price order

    fields = ['link', 'location', 'owner/description', 'bedrooms/amenities', 'dates', 'price_per_night', 'rating/reviews']
    file = open('airbnb.csv', 'w')
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(listing_arr)

    # close webdriver
    driver.quit()

