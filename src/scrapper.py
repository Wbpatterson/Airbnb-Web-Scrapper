from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from constants import*
import pyshorteners
import csv
import re

def shorten_url(long_url) -> str:
    # Initialize the Shortener class with the desired URL shortening service
    s = pyshorteners.Shortener()
    # Shorten the URL
    shortened_url = s.tinyurl.short(long_url)  

    return shortened_url

def create_csv(fields, name="airbnb.csv") -> None:
    # Open the file with 'utf-8' encoding to support Unicode characters
    with open(name, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(listings)

# main page scraping function that retrieves page HTML
def scrape_page(url) -> BeautifulSoup:
    driver.get(url)
    get_url = driver.current_url
    
    # VITAL: page must wait till the element below is loaded as HTML will not properly load otherwise
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, LISTINGS_CONTAINER_CLASS)))
    
    if get_url == url: 
        page_source = driver.page_source
        
    soup = BeautifulSoup(page_source, features='lxml')
    return soup

def store_listings(page_listings, page_links) -> None:
    
    for n in range(len(page_listings)):
        listing = page_listings[n].contents
        location = listing[0].text
        description = listing[1].text
        bedrooms = listing[2].text      
        dates = date
        price_per_night = listing[3].text
        link = shorten_url('https://www.airbnb.com' + page_links[n]['href'])
        
        rating = "no rating" if len(listing) < 5 or listing[4].text == "" else listing[4].text
        
        price = re.search(r"\$\d+.?per night", price_per_night).group(0)
        price_per_night = "No listed price" if price == None else re.search(r"\$\d+", price).group(0)
        
        listings.append({
            'link': link,
            'location': location,
            'owner/description': description,
            'bedrooms/amenities': bedrooms,
            'dates': dates,
            'price_per_night': price_per_night,
            'rating/reviews': rating
        })


if __name__=="__main__":
    options = Options()
    options.headless = True
    options.add_argument("--headless=new")
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('log-level=3')

    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 4)
    
    listings = [] 
    url = input("Enter a Airbnb url: ")
    pages_to_search = int(input("Enter number of pages to search: "))
    
    if url == None:
        print("invalid url")
        exit()

    # assigns new page to be scraped and updates driver with new url
    current_page = scrape_page(url) 
    date = current_page.find_all('button', LISTING_DATE_CLASS)[1].text
    
    for _ in range(pages_to_search):
        page_listings = current_page.find_all('div', LISTING_DIV_CLASS)
        page_links = current_page.find_all('a', LISTING_LINK_CLASS)
        store_listings(page_listings, page_links)
        
        # updates page to be searched via scrollbar arrow (>) near the bottom of the page
        url = driver.find_element(By.CLASS_NAME, SCROLLBAR_ARROW_CLASS).get_attribute("href")
        current_page = scrape_page(url) 
        
        if url == None:
            break
    
    listings.sort(key=lambda listing: int(listing['price_per_night'][1:]))  # sorts listings in ascending price order
    fields = ['link', 'location', 'owner/description', 'bedrooms/amenities', 'dates', 'price_per_night', 'rating/reviews']
    create_csv(fields)
    
    driver.quit()

