# beauty_soup.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pyshorteners
import csv
import re
import time

start = time.time()

# algorithm needs to take in filtered searches (i.e, #guest, location) from airbnb for best results
# need to prioritize improving time 
        
def shorten_url(long_url):
    # Initialize the Shortener class with the desired URL shortening service
    s = pyshorteners.Shortener()
    # Shorten the URL
    shortened_url = s.tinyurl.short(long_url)  

    return shortened_url

options = Options()
options.headless = True
options.add_argument("--headless=new")
path = '/usr/bin/chromedriver'
options.add_argument(f"webdriver.chrome.driver={path}")

driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 5)

def scrape(url):
    driver.get(url)
    get_url = driver.current_url
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'l1ovpqvx.c1ytbx3a.dir.dir-ltr')))
    
    if get_url == url: 
        page_source = driver.page_source
        
    soup = BeautifulSoup(page_source,features='lxml')
    return soup

listing_arr = []

def placeListings(listings, links, time):
    
    for n in range(len(listings)):
        info = listings[n].contents
        location = info[0].text
        description = info[1].text
        bedrooms = info[2].text      
        dates = time
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
    
    url = input("Enter a Airbnb url: ")
    num_pages = int(input("Enter amount of pages to search: "))

    if url == None:
        print("invalid url")
        exit()

    for page in range(num_pages):
        
        if url == None:
            break
        
        curr_site = scrape(url) # assigns new page to be scraped and updates driver
        listings = curr_site.find_all('div','g1qv1ctd c1v0rf5q dir dir-ltr') # finds all listings 
        links = curr_site.find_all('a', 'l1ovpqvx bn2bl2p dir dir-ltr')
        date = curr_site.find_all('div', 'f16sug5q dir dir-ltr')[1].text
        placeListings(listings, links, date) # places listings into list
        url = driver.find_element(By.CLASS_NAME, 'l1ovpqvx.c1ytbx3a.dir.dir-ltr').get_attribute("href")
    

    def cmp_list(listing):
        return int(listing['price_per_night'][1:])

    listing_arr.sort(key=cmp_list)

    fields = ['link', 'location', 'owner/description', 'bedrooms/amenities', 'dates', 'price_per_night', 'rating/reviews']
    file = open('airbnb.csv', 'w')
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(listing_arr)

    # close webdriver
    driver.quit()

    end = time.time()

    print(end-start)
