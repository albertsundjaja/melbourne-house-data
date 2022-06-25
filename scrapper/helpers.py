from bs4 import BeautifulSoup
from datetime import date
import time
import requests
import re


def extract_articles(soup):
    """
    the articles are separated according to their initial suburb name
    loop through all alphabet and get the HTML components
    """
    articles = []
    for num in range(0, 26):
        if soup.find(id=chr(ord('A') + num)) != None:
            for article in soup.find(id=chr(ord('A') + num)).find_all('article'):
                articles.append(article)
    return articles


def extract_property_summaries(articles):
    """
    the article contains the summary of the auction result
    the summary also contain a page url which contains the property details
    """
    properties = []
    for suburb in articles:
        suburb_name = suburb.h3.text
        print("extracting properties from suburb {}".format(suburb_name))
        for listing in suburb.find_all('ul'):
            listing_details = listing.find_all('li')
            address = listing_details[0].a.text
            page_url = listing_details[0].a['href']
            sold_price = -1
            if len(listing_details[2].find_all('span')) == 1:
                sold_price = listing_details[2].find_all('span')[0].text
            if len(listing_details[2].find_all('span')) > 1:
                sold_price = listing_details[2].find_all('span')[1].text

            sold_type = listing_details[2].find_all('span')[0].text
            property_type = listing_details[1].find_all('span')[0].text
            beds = 'UNAVAILABLE'
            try:    
                beds = listing_details[1].find_all('span')[1].text.split(' ')[0]
            except:
                beds = 'UNAVAILABLE'

            temp_property = {
                'extracted_date': int(date.today().strftime('%Y%m%d')), 
                'suburb': suburb_name,
                'address': address,
                'sold_price': sold_price,
                'sold_type': sold_type,
                'property_type': property_type,
                'beds': beds,
                'page_url': page_url
            }

            properties.append(temp_property)
    return properties


def extract_property_details(properties, headers):
    """
    try to extract the baths, carpark, land_area and sold_date from the property page
    """
    # for extracting sold date e.g. 17 Apr 2020
    date_regex = re.compile('[0-9]{1,2} [a-zA-Z]{3} [0-9]{4}')
    for prop in properties:
        url = prop['page_url']
        print("extracting details from {}".format(url))
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html5lib')
        if prop['page_url'].split('/')[3] != 'property-profile':
            # bed bath carpark land_area
            features = soup.find('div', 'listing-details__listing-summary-features')
            if (features):
                features = features.find_all(attrs={'data-testid':'property-features-text-container'})
                if len(features) > 2:
                    prop['beds'] = features[0].text.split(' ')[0]
                    prop['baths'] = features[1].text.split(' ')[0]
                    prop['carparks'] = features[2].text.split(' ')[0]
                    if len(features) > 3:
                        prop['land_area'] = features[3].text.split(' ')[0]
                    else:
                        prop['land_area'] = 'UNAVAILABLE'
                else:
                    # beds already extracted in summary and set as UNAVAILABLE if unavailable
                    prop['baths'] = 'UNAVAILABLE'
                    prop['carparks'] = 'UNAVAILABLE'
                    prop['land_area'] = 'UNAVAILABLE'
            else:
                prop['baths'] = 'UNAVAILABLE'
                prop['carparks'] = 'UNAVAILABLE'
                prop['land_area'] = 'UNAVAILABLE'

            # sold date
            sold_span = soup.find(attrs={'data-testid':'listing-details__listing-tag'})
            if sold_span != None:
                matches = date_regex.search(sold_span.text)
                if matches:
                    prop['sold_date'] = matches.group(0)
                else:
                    prop['sold_date'] = 'UNAVAILABLE'
            else:
                prop['sold_date'] = 'UNAVAILABLE'
                features_date = soup.find_all('span')
                for feature in features_date:
                        if feature.text:
                            split = feature.text.split('Listing sold by advertiser ')
                            if len(split) > 1:
                                prop['sold_date'] = split[1]

            # zip code and state
            try:
                prop['zip'] = soup.find('h1', 'listing-details__listing-summary-address').text.split(' ')[-1]
                prop['state'] = soup.find('h1', 'listing-details__listing-summary-address').text.split(' ')[-2]
            except:
                prop['zip'] = 'UNAVAILABLE'
                prop['state'] = 'UNAVAILABLE'

        # page with property-profile
        else:
            # zip and state
            if soup.find('section', 'property-details-strip') != None:
                prop['zip'] = soup.find('section', 'property-details-strip').h1.text.split(' ')[-1]
                prop['state'] = soup.find('section', 'property-details-strip').h1.text.split(' ')[-2]
            else:
                prop['zip'] = 'UNAVAILABLE'
                prop['state'] = 'UNAVAILABLE'

            # sold date is not available in property-profile page
            prop['sold_date'] = 'UNAVAILABLE'

            # land area not available in property-profile page
            prop['land_area'] = 'UNAVAILABLE'

            # bed bath carpark
            features = soup.find(attrs={'data-testid':'property-features'})
            if features:
                features = features.find_all(attrs={'data-testid':'property-features-text-container'})
                if len(features) > 2:
                        prop['beds'] = features[0].text.split(' ')[0]
                        prop['baths'] = features[1].text.split(' ')[0]
                        prop['carparks'] = features[2].text.split(' ')[0]
                        if len(features) > 3:
                            prop['land_area'] = features[3].text.split(' ')[0]
                        else:
                            prop['land_area'] = 'UNAVAILABLE'
            else:
                # beds already extracted in summary and set as UNAVAILABLE if unavailable
                prop['baths'] = 'UNAVAILABLE'
                prop['carparks'] = 'UNAVAILABLE'

        # sleep so that the website doesnt consider us as an attack attempt
        time.sleep(1)
        break
    return properties