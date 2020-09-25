from bs4 import BeautifulSoup as bs
import requests
import pymongo
from splinter import Browser
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
import time
import json


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser("chrome", **executable_path, headless=False)


def scrape_info():
    browser = init_browser()

    # Visit mars sites
    url = url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")

    # Collect Headline
    headlines = soup.find('li', class_="slide")
    title = headlines.find('div', class_="content_title").a.text.strip()
    news_p = headlines.find('div', class_="article_teaser_body").text
    # Next Site collect main image
    image_url= "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(image_url)
    browser.click_link_by_partial_text('FULL IMAGE')
    browser.click_link_by_partial_text('more info')

    html2 = browser.html
    soup = bs(html2, 'html.parser')
    url= soup.find('figure',class_='lede').a['href']
    featured_image_url = "https://www.jpl.nasa.gov"+url

    # Go to next site, create a table of mars data
    mars_url="https://space-facts.com/mars/"
    browser.visit(mars_url)
    df=pd.read_html(mars_url)[0]
    mars_table=df.to_html()
    # Go to next site, collect hemishpere data
    
    hem_url= "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hem_url)
    header = browser.find_by_css(".description")
    hemisphere_image_urls =[]
    for i in range(len(header)):
        hemisphere={}
        description = browser.find_by_css(".description")
        add=description[i].find_by_tag("h3").text
        browser.links.find_by_partial_text(add).click()
        hemisphere['title']=add
        sample=browser.find_by_text('Sample').first['href']
        hemisphere['img_url']=sample
        hemisphere_image_urls.append(hemisphere)
        browser.back()


    # Store data in a dictionary
    MarsDB={
    'newsTitle':title,
    'newsP':news_p,
    'featureImage':featured_image_url,
    'dataTable':mars_table,
    'hemispheres':hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return MarsDB