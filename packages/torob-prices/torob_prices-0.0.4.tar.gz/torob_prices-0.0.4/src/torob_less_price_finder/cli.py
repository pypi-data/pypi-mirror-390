import requests
from bs4 import BeautifulSoup
import re
import argparse

def clean_persian_price(raw_text):

    # 1. Map Persian/Arabic digits to English digits
    persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
    english_digits_text = raw_text.translate(persian_to_english)

    cleaned_text = re.sub(r'[^\d\.\,]+', '', english_digits_text)
    
    # 3. Remove the thousands separators (٫, , , or .)
    numeric_string = cleaned_text.replace('٫', '').replace(',', '').replace('.', '')
    
    try:
        # 4. Convert to an integer
        return int(numeric_string)
    except ValueError:
        return None

def scrape_torob_prices(search_query, base_url):
    # 1. Define URL and Parameters
    query_params = {'query': search_query}

    print(f"Searching Torob for: '{search_query}'...")
    
    # 2. Fetch the HTML content
    try:
        # Use a common User-Agent to mimic a standard browser
        
        response = requests.get(base_url, params=query_params, timeout=15)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        if response:
            print(response.text)
        
        return []

    # 3. Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # 4. Find ALL price elements
    # We use the class name you identified, which appears to be stable for price containers.
    price_class = 'ProductCard_desktop_product-price-text__y20OV'
    price_elements = soup.find_all('div', class_=price_class)

    prices_list = []
    
    if not price_elements:
        print("No price elements found with the expected class name.")
        # Try a broader selector if needed, but stick with the specific class first
        return []

    # 5. Extract and Clean the Price from each element
    print(f"\nFound {len(price_elements)} potential price elements. Extracting...")

    for i, element in enumerate(price_elements, 1):
        raw_price_text = element.get_text()
        cleaned_price = clean_persian_price(raw_price_text)
        
        # Often, the product name is in a nearby sibling/parent element.
        # Let's just track the price for now.
        
        if cleaned_price is not None:
            prices_list.append({
                'index': i,
                'raw_text': raw_price_text,
                'numeric_price': cleaned_price
            })

    return prices_list

def main():
    parser = argparse.ArgumentParser(description='Scrape Torob for product prices.')
    parser.add_argument('search_term', help='The product to search for.')
    parser.add_argument('--base_url', default='https://torob.com/search/', help='The base URL for the search.')
    parser.add_argument('--min', action='store_true', help='Only display the minimum price.')
    args = parser.parse_args()

    results = scrape_torob_prices(args.search_term, args.base_url)

    if results:
        prices = [item['numeric_price'] for item in results]
        
        if prices:
            if args.min:
                print(f'\nLowest price is: {min(prices)}')
            else:
                print("\n--- Extracted Prices ---")
                for item in results:
                    print(f"Product {item['index']}: RAW='{item['raw_text']}' -> CLEANED={item['numeric_price']}")
        else:
            print("\nNo valid prices were extracted.")

if __name__ == '__main__':
    main()