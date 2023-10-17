import pandas as pd
import re 
import time
import clipboard
import pyautogui
import datetime

today=datetime.datetime.today()
today = str(datetime.datetime.date(today))

fidi = {
    '90 Washington':'https://streeteasy.com/for-rent/nyc/building:109',
    '100 John': 'https://streeteasy.com/for-rent/nyc/building:362',
    '37 Wall': 'https://streeteasy.com/for-rent/nyc/building:150',
    '75 West': 'https://streeteasy.com/for-rent/nyc/building:282',
    '116 John': 'https://streeteasy.com/for-rent/nyc/building:356',
    '85 John ': 'https://streeteasy.com/for-rent/nyc/building:416',
    '11 Maiden': 'https://streeteasy.com/for-rent/nyc/building:324',
    '63 Wall': 'https://streeteasy.com/for-rent/nyc/building:153',
    '67 Wall': 'https://streeteasy.com/for-rent/nyc/building:154',
    '90 West': 'https://streeteasy.com/for-rent/nyc/building:285',
    '15 Park Row': 'https://streeteasy.com/for-rent/nyc/building:497',
    '100 Maiden Lane': 'https://streeteasy.com/for-rent/nyc/building:232',
    '95 Wall': 'https://streeteasy.com/for-rent/nyc/building:198',
    '10 Hanover': 'https://streeteasy.com/for-rent/nyc/building:192',
    '2 Gold': 'https://streeteasy.com/for-rent/nyc/building:352',
    '45 Wall': 'https://streeteasy.com/for-rent/nyc/building:151',
    '71 Broadway': 'https://streeteasy.com/for-rent/nyc/building:129',
    '84 William': 'https://streeteasy.com/for-rent/nyc/building:340',
    '180 Water': 'https://streeteasy.com/for-rent/nyc/building:365',
    '20 Broad': 'https://streeteasy.com/for-rent/nyc/building:137',
    '20 Exchnage': 'https://streeteasy.com/for-rent/nyc/building:155',
    '21 West': 'https://streeteasy.com/for-rent/nyc/building:60',
    '70 Pine': 'https://streeteasy.com/for-rent/nyc/building:225',
    '29 Cliff': 'https://streeteasy.com/for-rent/nyc/building:406',
#     '40 Gold':  'https://streeteasy.com/building/40-gold-street-new_york',
    '254 Front': 'https://streeteasy.com/for-rent/nyc/building:605',
    '15 Cliff': 'https://streeteasy.com/for-rent/nyc/building:409',
    '33 Gold': 'https://streeteasy.com/for-rent/nyc/building:424',
    '108 Fulton': 'https://streeteasy.com/for-rent/nyc/building:429',
    '110 Greenwhich': 'https://streeteasy.com/for-rent/nyc/building:272',
    '8 Spruce': 'https://streeteasy.com/for-rent/nyc/building:582',
    '19 Dutch': 'https://streeteasy.com/for-rent/nyc/building:438',
    '7 Dey': 'https://streeteasy.com/for-rent/nyc/building:6637473',
    '2 Water': 'https://streeteasy.com/for-rent/nyc/building:25', 
    '200 Water': 'https://streeteasy.com/for-rent/nyc/building:392',
    '1 West':'https://streeteasy.com/for-rent/nyc/building:61'
}

def extract_with_first_method(text):
    listings = re.split(r'\n\d+\s', text)
    results = []

    for listing in listings[1:]:  # Skip the first empty element
        listing_dict = {}

        # Extract the listing title and price
        title_price_match = re.match(r'(.+)\n\$(\d+(?:,\d+)?)\s', listing)
        if title_price_match:
            listing_dict['Title'] = title_price_match.group(1).strip()
            listing_dict['Price'] = int(title_price_match.group(2).replace(',', ''))

        # Extract other details using regular expressions
        other_details = re.findall(r'(Studio|\d+\sBed)\s(.+?)\sBath', listing)
        if other_details:
            beds, bath = other_details[0]
            listing_dict['Bedrooms'] = beds
            listing_dict['Bathrooms'] = bath

        if all(key in listing_dict for key in ['Title', 'Price', 'Bedrooms', 'Bathrooms']):
            results.append(listing_dict)

    return results
def extract_with_second_method(text):
    sections = re.split(r'\n(?=\d+\s[A-Za-z0-9\s#]+)', text)
    results = []

    # Define regular expressions to extract specific details
    patterns = {
        'unit': re.compile(r'(\d+\s[A-Za-z0-9\s#]+)'),
        'price': re.compile(r'(\$[\d,]+(?:\.\d{2})?)'),
        'beds': re.compile(r'(\d+(?:\.\d+)?)\sBeds'),
        'baths': re.compile(r'(\d+(?:\.\d+)?)\sBath'),
    }

    for section in sections:
        listing_dict = {}
        for key, pattern in patterns.items():
            match = pattern.search(section)
            if match:
                listing_dict[key] = match.group(1).strip()

        if all(key in listing_dict for key in ['unit', 'price', 'beds', 'baths']):
            results.append({
                'Title': listing_dict['unit'],
                'Price': listing_dict['price'],
                'Bedrooms': listing_dict['beds'],
                'Bathrooms': listing_dict['baths'],
            })

    return results

master_df = []

for building_name, link in fidi.items():
    current_page = 1

    while True:
        if current_page == 1:
            page_url = link  # Use the base link for the first iteration
        else:
            page_url = f"{link}?page={current_page}"  # Append ?page=X for subsequent iterations

        time.sleep(1.5)
        pyautogui.hotkey('command', 't')  # Open a new tab
        time.sleep(1.5)
        pyautogui.hotkey('command', 'l')
        pyautogui.hotkey('command', 'l')
        pyautogui.press('backspace')
        time.sleep(1)
        # Simulate typing the URL and pressing Enter
        pyautogui.write(page_url)
        pyautogui.press('enter')
        time.sleep(4)
        pyautogui.hotkey('command', 'a')
        pyautogui.hotkey('command', 'c')# Wait for the page to load

        clipboard_content = clipboard.paste()
        text = clipboard_content

        listing_data = extract_with_first_method(text)
        df = pd.DataFrame(listing_data)


        # Extract the second method results
        second_method_results = extract_with_second_method(text)
        second_df = pd.DataFrame(second_method_results)

        # Concatenate both DataFrames
        merged_df = pd.concat([df, second_df], ignore_index=True)
        merged_df
        
        if merged_df.empty:
            # If the DataFrame is empty, it means there are no more pages, so break the loop
            pyautogui.hotkey('command', 'w')
            break
        try:
            title = df['Title'].iloc[0]
            # Define a regular expression pattern to capture "Washington Street"
            pattern = r'([^#]+)'

            # Use re.search to find the pattern in the string
            match = re.search(pattern, title)

            match = match.group(1)

            filtered_df = merged_df[merged_df['Title'].apply(lambda title: match in title)]

            filtered_df
        except:
            break
        

        filtered_df['building'] = building_name  # Assign the building name to the "building" column
        master_df.append(filtered_df)
        
        pyautogui.hotkey('command', 'w')
        
        

        current_page += 1

final_df = pd.concat(master_df, ignore_index=True)
final_df['Title'] = final_df['Title'].str.replace(r'^.*?#', '', regex=True)
final_df.rename(columns={'Title': 'Unit'}, inplace=True)
final_df.rename(columns={'building': 'Building'}, inplace=True)
final_df = final_df[['Building', 'Unit', 'Price', 'Bedrooms', 'Bathrooms']]
final_df.to_csv(f'./data/fidi_{today}.csv')

df=final_df

# Clean the Price column by removing dollar signs and commas
df['Price'] = df['Price'].str.replace('[$,]', '', regex=True).astype(float)

# Create a function to find the lowest price for each unique building and unit type
def find_lowest_prices(df):
    lowest_prices = df.groupby(['Building', 'Bedrooms']).agg({'Price': 'min'}).reset_index()
    return lowest_prices

# Find the lowest prices
lowest_prices = find_lowest_prices(df)

# Filter and extract the lowest prices for studio, 1-bedroom, and 2-bedroom units
lowest_studio = lowest_prices[lowest_prices['Bedrooms'] == 'Studio']
lowest_1_bedroom = lowest_prices[lowest_prices['Bedrooms'] == '1 Bed']
lowest_2_bedroom = lowest_prices[lowest_prices['Bedrooms'] == '2']

# Clean the Price column by removing dollar signs and commas
df['Price'] = df['Price'].replace('[$,]', '', regex=True).astype(float)

# Create a function to find the lowest price for each unique building and unit type
def find_lowest_prices(df):
    lowest_prices = df.groupby(['Building', 'Bedrooms']).agg({'Price': 'min'}).reset_index()
    return lowest_prices

# Find the lowest prices
lowest_prices = find_lowest_prices(df)

# Create a pivot table to reshape the data for all lowest prices
pivot_lowest_prices = lowest_prices.pivot(index='Building', columns='Bedrooms', values='Price').reset_index()

# Rename the columns for clarity
pivot_lowest_prices.columns.name = None  # Remove the column name
pivot_lowest_prices.rename(columns={'Studio': 'Lowest_Studio_Price', '1 Bed': 'Lowest_1_Bedroom_Price', '2': 'Lowest_2_Bedroom_Price'}, inplace=True)

# Fill any missing values with NaN (if a building doesn't have a certain unit type)
pivot_lowest_prices.fillna('', inplace=True)

pivot_lowest_prices[['Building', 'Lowest_1_Bedroom_Price', 'Lowest_2_Bedroom_Price', 'Lowest_Studio_Price']]

pivot_lowest_prices.to_csv('./data/lowest_prices.csv')