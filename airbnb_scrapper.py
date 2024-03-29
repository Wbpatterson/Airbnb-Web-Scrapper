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

import time

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
        listing = listings[n].contents
        location = listing[0].text
        description = listing[1].text
        bedrooms = listing[2].text      
        dates = date
        price_per_night = listing[3].text
        link = shorten_url('https://www.airbnb.com'+links[n]['href'])

        if len(listing) < 5 or listing[4].text == "":
            rating = "no rating"
        else:
            rating = listing[4].text
            
        price = re.search(r"\$\d+.?per night", price_per_night).group(0)

        
        if price == None:
            price_per_night = "No listed pirce"
        else:
            price_per_night = re.search(r"\$\d+", price).group(0)   
        
        info = {
            'link': link,
            'location': location,
            'owner/description': description,
            'bedrooms/amenities': bedrooms,
            'dates': dates,
            'price_per_night': price_per_night,
            'rating/reviews': rating
        }
        
        listing_arr.append(info)


if __name__=="__main__":
    start = time.time()
    options = Options()
    options.headless = True
    options.add_argument("--headless=new")
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('log-level=3')

    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 4)
    
    url = input("Enter a Airbnb url: ")
    num_pages = int(input("Enter number of pages to search: "))
    
    if url == None:
        print("invalid url")
        exit()

    for page in range(num_pages):
        
        if url == None:
            break
       
        # assigns new page to be scraped and updates driver with new url
        curr_site = scrape(url) 
        # finds all listings on a page
        listings = curr_site.find_all('div','g1qv1ctd atm_u80d3j_1lqfgyr atm_c8_o7aogt atm_g3_8jkm7i c1v0rf5q atm_9s_11p5wf0 atm_cx_d64hb6 atm_dz_7esijk atm_e0_1lo05zz dir dir-ltr')
        # finds all listings links on a page
        links = curr_site.find_all('a', 'rfexzly atm_9s_1ulexfb atm_7l_1j28jx2 atm_e2_1osqo2v dir dir-ltr')
        # finds all dates for listings 
        date = curr_site.find('div', 'f16sug5q atm_c8_13mdc1q atm_g3_qslrf5 atm_cs_qo5vgd atm_l8_1mni9fk atm_sq_1l2sidv atm_vv_1q9ccgz atm_ks_15vqwwr atm_am_ggq5uc atm_jb_1xtcb10 dir dir-ltr').text
        # places listings into list
        placeListings(listings, links, date)
        # updates page to be searched via scrollbar near the bottom of the page
        url = driver.find_element(By.CLASS_NAME, 'l1ovpqvx.c1ytbx3a.dir.dir-ltr').get_attribute("href")
    

    # returns price as an integer excluding $
    def cmp_list(listing):
        return int(listing['price_per_night'][1:])

    listing_arr.sort(key=cmp_list)  # sorts listings in ascending price order

    fields = ['link', 'location', 'owner/description', 'bedrooms/amenities', 'dates', 'price_per_night', 'rating/reviews']
   # Open the file with 'utf-8' encoding to support Unicode characters
    with open('airbnb.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(listing_arr)
    
    end = time.time()
    print(end - start)
    # close webdriver
    driver.quit()

