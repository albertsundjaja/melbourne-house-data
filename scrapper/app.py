from bs4 import BeautifulSoup
import requests
import helpers

# headers for our request
headers = {
    'authority': 'www.domain.com.au',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'dnt': '1',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
}

# url of the auction result
url = 'https://www.domain.com.au/auction-results/melbourne/'

def run(event, context):
    response = requests.get(url, headers=headers)

    # parse HTML result with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html5lib')

    # get all articles (listing HTML component)
    articles = helpers.extract_articles(soup)

    # extract the properties
    properties = helpers.extract_property_summaries(articles)

    # extract details of baths, carpark, land_area, sold_date    
    properties = helpers.extract_property_details(properties, headers)
    print(properties[0])
