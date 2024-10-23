# car_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.parse
import re
import json

# Helper function for cleaning numbers
def clean_number(text):
    """Cleans and extracts numeric values from a text."""
    return re.sub(r'\D', '', text)  # Remove non-digit characters

# Include the districts data directly in the code
districts_data = [
    {
        "District": "Colombo",
        "Cities": ["Colombo", "Dehiwala", "Mount Lavinia", "Moratuwa", "Negombo", "Kotte", "Battaramulla"]
    },
    # Add other districts and their cities as needed
    # ...
]

# Create a dictionary mapping city names to district names
city_to_district = {}
for district_info in districts_data:
    district_name = district_info['District']
    for city_name in district_info['Cities']:
        city_to_district[city_name.lower()] = district_name  # Use lowercase for case-insensitive matching

def scrape_ikman_cars(
    district, min_price, max_price, brand, min_yom, max_yom,
    fuel_type, transmission, pages_to_scrape, output_csv=None, stop_flag=None
):
    """
    Scrapes car listings from ikman.lk based on the provided filters.
    """
    all_car_details = []  # List to store all car details

    # Construct the base search URL
    search_url = construct_ikman_search_url(district, brand, min_yom, max_yom, fuel_type, transmission)

    for page in range(1, pages_to_scrape + 1):
        # Check the stop flag before processing each page
        if stop_flag and stop_flag.is_set():
            print("Scraping ikman.lk stopped by user.")
            break

        page_url = f"{search_url}&page={page}" if page > 1 else search_url
        print(f"Scraping ikman.lk page {page}...")

        # Extract ad URLs from the current page
        ad_urls = get_ikman_ads_from_page(page_url)

        for ad_url in ad_urls:
            # Check the stop flag before processing each ad
            if stop_flag and stop_flag.is_set():
                print("Scraping ikman.lk stopped by user.")
                break

            try:
                car_details = get_ikman_ad_details(ad_url)  # Scrape individual ad details
                all_car_details.append(car_details)
                print(f"Scraped: {ad_url}")
                time.sleep(1)  # Respectful pause between requests
            except Exception as e:
                print(f"Failed to scrape {ad_url}: {e}")

        # Additional check after processing each page
        if stop_flag and stop_flag.is_set():
            print("Scraping ikman.lk stopped by user after page processing.")
            break

    # Convert the list of dictionaries to a DataFrame with the required columns
    df = pd.DataFrame(all_car_details, columns=[
        "Price", "District", "Brand", "Model",
        "Year of Manufacture", "Fuel Type",
        "Transmission", "Engine Capacity", "Mileage"
    ])

    # Save the DataFrame to a CSV file if output_csv is provided
    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"Data saved to {output_csv}")

    return df

def get_ikman_ad_details(ad_url):
    """Extracts the required details from a single ikman.lk ad page."""
    response = requests.get(ad_url)
    ad_soup = BeautifulSoup(response.content, 'html.parser')

    # Define placeholders only for the required fields
    car_info = {
        "Price": None, "District": None, "Brand": None,
        "Model": None, "Year of Manufacture": None,
        "Fuel Type": None, "Transmission": None,
        "Engine Capacity": None, "Mileage": None
    }

    # Extract price and clean it
    price_tag = ad_soup.find('div', class_='amount--3NTpl')
    car_info['Price'] = clean_number(price_tag.text) if price_tag else None

    # Extract district
    district_tag = ad_soup.find('a', class_='subtitle-location-link--1q5zA',
                                attrs={'data-testid': 'subtitle-parentlocation-link'})
    car_info['District'] = district_tag.text.strip() if district_tag else "N/A"

    # Extract ad metadata
    meta_tags = ad_soup.find_all('div', class_='full-width--XovDn')
    for meta in meta_tags:
        label_tag = meta.find('div', class_='label--3oVZK')
        value_tag = meta.find('div', class_='value--1lKHt')

        if label_tag and value_tag:
            label = label_tag.text.strip().replace(':', '')
            value = ' '.join(value_tag.stripped_strings)

            # Map label to the required keys in car_info
            if label == "Brand":
                car_info['Brand'] = value
            elif label == "Model":
                car_info['Model'] = value
            elif label == "Year of Manufacture":
                car_info['Year of Manufacture'] = value
            elif label == "Fuel type":
                car_info['Fuel Type'] = value
            elif label == "Transmission":
                car_info['Transmission'] = value
            elif label == "Engine capacity":
                car_info['Engine Capacity'] = clean_number(value)  # Clean engine capacity
            elif label == "Mileage":
                car_info['Mileage'] = clean_number(value)  # Clean mileage

    return car_info

def get_ikman_ads_from_page(url):
    """Extracts ad URLs from an ikman.lk page."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    ad_cards = soup.find_all('a', class_='card-link--3ssYv')

    ad_urls = []
    for ad in ad_cards:
        href = ad.get('href')
        if href and "boost-ad" not in href:
            ad_urls.append(f"https://ikman.lk{href}")

    return ad_urls

def construct_ikman_search_url(district, brand, min_yom, max_yom, fuel_type, transmission):
    """Constructs the ikman.lk search URL based on the provided filters."""
    base_url = f"https://ikman.lk/en/ads/{urllib.parse.quote(district)}/cars"
    search_params = []

    if brand:
        search_params.append(f"tree.brand={urllib.parse.quote(brand)}")
    if min_yom:
        search_params.append(f"numeric.model_year.minimum={min_yom}")
    if max_yom:
        search_params.append(f"numeric.model_year.maximum={max_yom}")
    if fuel_type:
        search_params.append(f"enum.fuel_type={urllib.parse.quote(fuel_type)}")
    if transmission:
        search_params.append(f"enum.transmission={urllib.parse.quote(transmission)}")

    if search_params:
        base_url += "?" + "&".join(search_params)

    return base_url

def scrape_riyasewana_cars(
    district, min_price, max_price, brand, min_yom,
    max_yom, fuel_type, transmission, pages_to_scrape, output_csv=None, stop_flag=None
):
    """
    Scrapes car listings from riyasewana.com based on the provided filters.
    """
    # Add '-district' suffix to the district input
    district += "-district"

    # Base URL without the '?page=' parameter
    base_url = (
        f"https://riyasewana.com/search/cars/{brand}/{district}/{min_yom}-{max_yom}/"
        f"{fuel_type}/{transmission}/price-{min_price}-{max_price}"
    )
    data_list = []
    for page in range(1, pages_to_scrape + 1):
        # Check the stop flag before processing each page
        if stop_flag and stop_flag.is_set():
            print("Scraping riyasewana.com stopped by user.")
            break

        if page == 1:
            url = base_url
        else:
            url = f"{base_url}?page={page}"
        print(f"Scraping riyasewana.com page {page}: {url}")
        scrape_riyasewana_page(url, data_list, stop_flag)
        time.sleep(1)

        # Additional check after processing each page
        if stop_flag and stop_flag.is_set():
            print("Scraping riyasewana.com stopped by user after page processing.")
            break

    # Create DataFrame with only the required fields
    df = pd.DataFrame(data_list, columns=[
        'Price',
        'District',
        'Brand',
        'Model',
        'Year of Manufacture',
        'Fuel Type',
        'Transmission',
        'Engine Capacity',
        'Mileage'
    ])

    # Save to CSV if output_csv is provided
    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"Data saved to {output_csv}.")

    return df

def scrape_riyasewana_page(url, data_list, stop_flag=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve page {url}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('li', class_='item round')

    for listing in listings:
        # Check the stop flag before processing each listing
        if stop_flag and stop_flag.is_set():
            print("Scraping riyasewana.com stopped by user.")
            break

        try:
            h2_tag = listing.find('h2', class_='more')
            car_url = h2_tag.find('a')['href']
            full_car_url = f"https://riyasewana.com{car_url}" if not car_url.startswith('http') else car_url

            # Print the URL being scraped
            print(f"Scraped: {full_car_url}")

            # Extract city and price from listing overview
            boxtext_div = listing.find('div', class_='boxtext')
            boxintxt_divs = boxtext_div.find_all('div', class_='boxintxt')

            city = price = 'N/A'
            for div in boxintxt_divs:
                text = div.get_text(strip=True)
                if 'b' in div.get('class', []):
                    price = text.replace('Rs.', '').replace(',', '').strip()
                elif 's' in div.get('class', []):
                    pass  # skip date posted
                else:
                    if city == 'N/A':
                        city = text

            car_data = scrape_riyasewana_individual_listing(full_car_url, stop_flag)
            if car_data:
                # Lookup the district using the city name
                district_name = city_to_district.get(city.lower(), 'Unknown')
                car_data['District'] = district_name

                # If 'Price' is 'N/A', get from listing overview
                if car_data['Price'] == 'N/A':
                    car_data['Price'] = price
                data_list.append(car_data)
            time.sleep(1)
        except Exception as e:
            print(f"Error extracting data for a listing: {e}")

def scrape_riyasewana_individual_listing(url, stop_flag=None):
    # Check the stop flag before making the request
    if stop_flag and stop_flag.is_set():
        print("Scraping riyasewana.com individual listing stopped by user.")
        return None

    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve listing page {url}")
        return None
    soup = BeautifulSoup(response.content, 'html.parser')

    car_data = {}
    try:
        # Vehicle Details Table
        table = soup.find('table', class_='moret')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                # Check the stop flag during parsing
                if stop_flag and stop_flag.is_set():
                    print("Scraping riyasewana.com individual listing stopped by user.")
                    return None

                cols = row.find_all('td')
                if len(cols) >= 4:
                    label1 = cols[0].get_text(strip=True)
                    value1 = cols[1].get_text(strip=True)
                    label2 = cols[2].get_text(strip=True)
                    value2 = cols[3].get_text(strip=True)
                    car_data[label1] = value1
                    car_data[label2] = value2
                elif len(cols) >= 2:
                    label = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    car_data[label] = value

        # Map extracted data to required fields
        mapped_data = {
            'Price': car_data.get('Price', 'N/A').replace('Rs.', '').replace(',', '').strip(),
            'District': 'N/A',  # Will be updated in scrape_riyasewana_page function
            'Brand': car_data.get('Make', 'N/A'),
            'Model': car_data.get('Model', 'N/A'),
            'Year of Manufacture': car_data.get('YOM', 'N/A'),
            'Fuel Type': car_data.get('Fuel Type', 'N/A'),
            'Transmission': car_data.get('Gear', 'N/A'),
            'Engine Capacity': car_data.get('Engine (cc)', 'N/A').replace('cc', '').strip(),
            'Mileage': car_data.get('Mileage (km)', 'N/A').replace(',', '').replace('km', '').strip(),
        }

        return mapped_data
    except Exception as e:
        print(f"Error extracting data from listing page {url}: {e}")
        return None
