from pywebcopy import save_webpage
from time import sleep
from bs4 import BeautifulSoup as bs
import random
import os
import pandas as pd 
from datetime import date
import re
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui
import pyperclip

today = date.today()
today=str(today)

df = pd.read_csv(f'./fidi_{today}.csv')

flex_allowed = []
for i in df['Building']:
    if i == '106 Fulton Street':
        flex_allowed.append('Any')
    elif i == '71 Broadway':
        flex_allowed.append('No')
    elif i == '15 Cliff':
        flex_allowed.append('No')
    elif i == '116 John':
        flex_allowed.append('Straight Wall')
    elif i =='200 Water':
        flex_allowed.append('Straight Wall')
    elif i == '85 John':
        flex_allowed.append('Straight Wall')
    elif i == '2 Gold':
        flex_allowed.append('Straight Wall')
    elif i == '67 Wall':
        flex_allowed.append('Any')
    elif i == '15 Park Row':
        flex_allowed.append('Straight Wall')
    elif i == '90 West Street':
        flex_allowed.append('Straight Wall')
    elif i == '90 Washington Street':
        flex_allowed.append('Any')
        
    elif i == '20 Exchange':
        flex_allowed.append('Straight Wall')
    elif i == '10 Hanover':
        flex_allowed.append('Any')
    elif i == '11 Maiden Lane':
        flex_allowed.append('Any')
    elif i =='88 Fulton':
        flex_allowed.append('Any')
    elif i == '19 Dutch':
        flex_allowed.append('No')
    elif i == '8 Spruce':
        flex_allowed.append('No')
        
    elif i == '21 West':
        flex_allowed.append('No')
    elif i == '29 Cliff':
        flex_allowed.append('Straight Wall')
    elif i == '7 Dey':
        flex_allowed.append('Straight Wall')
    elif i == '70 Pine':
        flex_allowed.append('Any')
        
    elif i == '45 Wall':
        flex_allowed.append('Straight Wall')
    elif i == '2 Water':
        flex_allowed.append('No')
    elif i == '180 Water':
        flex_allowed.append('Straight Wall')
    elif i == '63 Wall':
        flex_allowed.append('Any')
    
    elif i == '254 Front':
        flex_allowed.append('No')
    elif i == '95 Wall':
        flex_allowed.append('Any')
    elif i == '20 Broad':
        flex_allowed.append('Straight Wall')
    elif i == '37 Wall':
        flex_allowed.append('Straight Wall')
    elif i == '100 John':
        flex_allowed.append('Any')
    elif i == '100 Maiden Lane':
        flex_allowed.append('Straight Wall')
    elif i == '40 Gold':
        flex_allowed.append('Straight Wall')
    elif i == '84 William':
        flex_allowed.append('No')
    elif i == '110 Greenwich':
        flex_allowed.append('No')
    elif i == '100 John':
        flex_allowed.append('Any')
    else:
        flex_allowed.append('Any')

df['flex'] = flex_allowed

df['Price']=df['Price'].str.replace(r'[\$,]', '', regex=True)

buildings = df['Building'].unique()

class DataFusion:
    def __init__(self, df):
        self.df = df
        self.combined_df = pd.DataFrame()

    def flex_1(self, building):
        flex_1_df = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == 'Studio')]
        self.combined_df = pd.concat([self.combined_df, flex_1_df.tail(3)], ignore_index=True)

    def flex_2(self, building):
        flex_2_df = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == '1 Bed')]
        flex_2 = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == 'Studio') & (self.df['flex'] == 'Any')]
        combined_df = pd.concat([flex_2_df.tail(1), flex_2.tail(1)], ignore_index=True)
        self.combined_df = pd.concat([self.combined_df, combined_df], ignore_index=True)
        flex_2 = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == 'Studio') & (self.df['flex'] == 'Straight Wall')]
        combined_df = pd.concat([flex_2_df.tail(1), flex_2.tail(1)], ignore_index=True)
        self.combined_df = pd.concat([self.combined_df, combined_df], ignore_index=True)

    def flex_3(self, building):
        flex_3_df = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == '2')]
        flex_3 = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == '1 Bed') & (self.df['flex'] == 'Any')]
        combined_df = pd.concat([flex_3_df.tail(1), flex_3.tail(1)], ignore_index=True)
        self.combined_df = pd.concat([self.combined_df, combined_df], ignore_index=True)

    def get_combined_df(self):
        return self.combined_df
    
    def reset_combined_df(self):
        self.combined_df = pd.DataFrame()
        

def get_cheapest_options(combined_df):
    sorted_df = combined_df.sort_values('Price')

    cheapest_studios = sorted_df[sorted_df['Bedrooms'] == 'Studio'].drop_duplicates(subset='Building').head(20)

    cheapest_1beds = sorted_df[sorted_df['Bedrooms'] == '1 Bed'].drop_duplicates(subset='Building').head(20)

    cheapest_2beds = sorted_df[sorted_df['Bedrooms'] == '2'].drop_duplicates(subset='Building').head(15)

    final_df = pd.concat([cheapest_studios, cheapest_1beds, cheapest_2beds], ignore_index=True)

    return final_df

        
data_fusion = DataFusion(df)
for i in buildings:
    data_fusion.flex_1(i)
    data_fusion.flex_2(i)
    data_fusion.flex_3(i)
combined_df = data_fusion.get_combined_df()

df_unique = combined_df.drop_duplicates()


best_to_advertise = get_cheapest_options(df_unique)

best_to_advertise.drop_duplicates(inplace=True)

path = './fidiBuildings/'
# Define the regex pattern to match "Street" and the number
pattern = r"\bStreet|\d+|\s+"
pattern2 = r"\bStreet|\d+\s+\Z"

# Create an empty list to store the extracted data
data = []

for index, row in best_to_advertise.iterrows():
    # Access the values in each column
    folder = re.sub(pattern2, "", row['Building'])
    building = row['Building']
    cross_street = re.sub(pattern, "", row['Building'])
    beds = row['Bedrooms']
    flex = row['flex']
    baths=row['Bathrooms']
    price = row['Price']
    unit = row['Unit']
    paths = os.listdir(path)
    
    # Create a dictionary to store the extracted values
    row_data = {
        'Folder': '',
        'Building': building,
        'Cross Street': cross_street,
        'Unit': unit,
        'Beds': beds,
        'Baths': baths,
        'Flex': flex,
        'Price': price
    }
    
    for i, folder_name in enumerate(paths):
        if folder in folder_name or folder[:-1] == folder_name or folder[:-2] == folder_name:
            folder_path = os.path.abspath(os.path.join(path, folder_name))
            row_data['Folder'] = folder_path
            break
    
    # Append the row data to the list
    data.append(row_data)

# Create a new DataFrame from the extracted data
new_df = pd.DataFrame(data)

# Replace empty strings with NaN
new_df.replace('', pd.NA, inplace=True)

# Drop rows with NaN values
new_df.dropna(inplace=True)

# Reset the index
new_df.reset_index(drop=True, inplace=True)
def map_flex_value(value):
    if value == 'Straight':
        return 1
    elif value == 'Any':
        return 2
    elif value == 'No':
        return 1
    else:
        return 1
def map_flex_path(row):
    if row['Beds'] == 'Studio':
        if row['num_flex'] == 1:
            return 'Flex1'
        elif row['num_flex'] == 2 and int(row['Price'])>=3500:
            return 'Flex2'
        elif row['num_flex'] == 2 and int(row['Price'])<=3500:
            return 'Flex1'
    elif row['Beds'] == '1 Bed':
        if row['num_flex'] == 1:
            return 'Flex2'
        elif row['num_flex'] == 2:
            return 'Flex3'
    elif row['Beds'] == '2':
        if row['num_flex'] == 1:
            return 'Flex3'

new_df['num_flex'] = new_df['Flex'].apply(map_flex_value)
new_df['flex_path']=new_df.apply(map_flex_path, axis=1)

import os

for index, row in new_df.iterrows():

    try:
        folder_path = row['Folder'] + '/' + row['flex_path']
        if os.path.exists(folder_path):
            # File path exists
            print(f"File path {folder_path} exists.")
        else:
            # File path does not exist
            print(f"File path {folder_path} does not exist.")
            new_df = new_df.drop(index)
    except:
        # Exception occurred, remove the row from the DataFrame
        new_df = new_df.drop(index)

class DataFusion:
    def __init__(self, df):
        self.df = df
        self.combined_df = pd.DataFrame()

    def flex_1(self, building):
        flex_1_df = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == 'Studio')]
        self.combined_df = pd.concat([self.combined_df, flex_1_df.tail(3)], ignore_index=True)

    def flex_2(self, building):
        flex_2_df = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == '1 Bed')]
        flex_2 = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == 'Studio') & (self.df['flex'] == 'Any')]
        combined_df = pd.concat([flex_2_df.tail(1), flex_2.tail(1)], ignore_index=True)
        self.combined_df = pd.concat([self.combined_df, combined_df], ignore_index=True)
        flex_2 = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == 'Studio') & (self.df['flex'] == 'Straight Wall')]
        combined_df = pd.concat([flex_2_df.tail(1), flex_2.tail(1)], ignore_index=True)
        self.combined_df = pd.concat([self.combined_df, combined_df], ignore_index=True)

    def flex_3(self, building):
        flex_3_df = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == '2')]
        flex_3 = self.df[(self.df['Building'] == building) & (self.df['Bedrooms'] == '1 Bed') & (self.df['flex'] == 'Any')]
        combined_df = pd.concat([flex_3_df.tail(1), flex_3.tail(1)], ignore_index=True)
        self.combined_df = pd.concat([self.combined_df, combined_df], ignore_index=True)

    def get_combined_df(self):
        return self.combined_df
    
    def reset_combined_df(self):
        self.combined_df = pd.DataFrame()
        

def get_cheapest_options(combined_df):
    sorted_df = combined_df.sort_values('Price')

    cheapest_studios = sorted_df[sorted_df['Bedrooms'] == 'Studio'].drop_duplicates(subset='Building').head(25)

    cheapest_1beds = sorted_df[sorted_df['Bedrooms'] == '1 Bed'].drop_duplicates(subset='Building').head(20)

    cheapest_2beds = sorted_df[sorted_df['Bedrooms'] == '2'].drop_duplicates(subset='Building').head(15)

    final_df = pd.concat([cheapest_studios, cheapest_1beds, cheapest_2beds], ignore_index=True)

    return final_df

        
data_fusion = DataFusion(df)
for i in buildings:
    data_fusion.flex_1(i)
    data_fusion.flex_2(i)
    data_fusion.flex_3(i)
combined_df = data_fusion.get_combined_df()

df_unique = combined_df.drop_duplicates()


best_to_advertise = get_cheapest_options(df_unique)

best_to_advertise.drop_duplicates(inplace=True)

path = './fidiBuildings/'
# Define the regex pattern to match "Street" and the number
pattern = r"\bStreet|\d+|\s+"
pattern2 = r"\bStreet|\d+\s+\Z"

# Create an empty list to store the extracted data
data = []

for index, row in best_to_advertise.iterrows():
    # Access the values in each column
    folder = re.sub(pattern2, "", row['Building'])
    building = row['Building']
    cross_street = re.sub(pattern, "", row['Building'])
    beds = row['Bedrooms']
    flex = row['flex']
    baths=row['Bathrooms']
    price = row['Price']
    unit = row['Unit']
    paths = os.listdir(path)
    
    # Create a dictionary to store the extracted values
    row_data = {
        'Folder': '',
        'Building': building,
        'Cross Street': cross_street,
        'Unit': unit,
        'Beds': beds,
        'Baths': baths,
        'Flex': flex,
        'Price': price
    }
    
    for i, folder_name in enumerate(paths):
        if folder in folder_name or folder[:-1] == folder_name or folder[:-2] == folder_name:
            folder_path = os.path.abspath(os.path.join(path, folder_name))
            row_data['Folder'] = folder_path
            break
    
    # Append the row data to the list
    data.append(row_data)

# Create a new DataFrame from the extracted data
new_df = pd.DataFrame(data)

# Replace empty strings with NaN
new_df.replace('', pd.NA, inplace=True)

# Drop rows with NaN values
new_df.dropna(inplace=True)

# Reset the index
new_df.reset_index(drop=True, inplace=True)
def map_flex_value(value):
    if value == 'Straight':
        return 1
    elif value == 'Any':
        return 2
    elif value == 'No':
        return 1
    else:
        return 1
def map_flex_path(row):
    if row['Beds'] == 'Studio':
        if row['num_flex'] == 1:
            return 'Flex1'
        elif row['num_flex'] == 2 and int(row['Price'])>=3500:
            return 'Flex2'
        elif row['num_flex'] == 2 and int(row['Price'])<=3500:
            return 'Flex1'
    elif row['Beds'] == '1 Bed':
        if row['num_flex'] == 1:
            return 'Flex2'
        elif row['num_flex'] == 2:
            return 'Flex3'
    elif row['Beds'] == '2':
        if row['num_flex'] == 1:
            return 'Flex3'

new_df['num_flex'] = new_df['Flex'].apply(map_flex_value)
new_df['flex_path']=new_df.apply(map_flex_path, axis=1)
def map_bed_count(row):
    if row['Beds'] == 'Studio':
        if row['num_flex'] == 1:
            return 1
        elif row['num_flex'] == 2:
            return 2
    elif row['Beds'] == '1 Bed':
        if row['num_flex'] == 1:
            return 2
        elif row['num_flex'] == 2:
            return 3
    elif row['Beds'] == '2':
        if row['num_flex'] == 1:
            return 3
        if row['num_flex']==2:
            return 3
def price_edit(row):
    if str(row['bed_count'])==str(1):
        return int(row['Price'])-150
    if str(row['bed_count'])==str(2):
        return int(row['Price'])-175
    if str(row['bed_count'])==str(3):
        return int(row['Price'])-400
    

new_df['num_flex'] = new_df['Flex'].apply(map_flex_value)
new_df['flex_path']=new_df.apply(map_flex_path, axis=1)
new_df['bed_count']=new_df.apply(map_bed_count, axis=1)
new_df['bath_count']=new_df['Baths']
new_df['cleaned_unit']=new_df['Unit']
new_df['new_addy']=new_df['Building'].str.replace('Street', 'St')
new_df['price_edit']=new_df.apply(price_edit, axis=1)

import os

for index, row in new_df.iterrows():

    try:
        folder_path = row['Folder'] + '/' + row['flex_path']
        if os.path.exists(folder_path):
            # File path exists
            print(f"File path {folder_path} exists.")
        else:
            # File path does not exist
            print(f"File path {folder_path} does not exist.")
            new_df = new_df.drop(index)
    except:
        # Exception occurred, remove the row from the DataFrame
        new_df = new_df.drop(index)

web_titles = [
    "Hidden Gem: Discover Your Dream Apartment!",
    "Unveiling Luxury: Your Perfect Apartment Awaits!",
    "Never Seen Before: Experience Apartment Bliss!",
    "Act Fast, Live Lavishly: Snatch Your Dream Apartment!",
    "Affordable Elegance: Embrace Your New Home!",
    "Apartment Enchantment: Where Dreams Become Reality!",
    "Your Oasis Awaits: Find Serenity in Your New Apartment!",
    "Uncover the Hidden Treasure: Your Ideal Apartment!",
    "Jewel in the City: Your Dream Apartment Found!",
    "Exclusive Charm: Elevate Your Living Experience!",
    "Unparalleled Luxury: Indulge in Apartment Perfection!",
    "Seize the Opportunity: Claim Your Dream Apartment!",
    "Unlock Happiness: Your Ideal Apartment Awaits!",
    "Picture-Perfect Living: Find Your Dream Apartment!",
    "Timeless Beauty: Embrace the Essence of Apartment Living!",
    "Exquisite Abode: Discover the Epitome of Luxury!",
    "Seize the Opportunity: Claim Your Dream Apartment!",
    "Unleash Your Inner Stylist: Personalize Your Dream Apartment!",
    "Architectural Delight: Your Dream Apartment Revealed!",
    "Captivating Haven: Experience Apartment Bliss!",
    "Unwind in Luxury: Discover Your Dream Apartment!",
    "Your Urban Retreat: Find Peace in Your New Apartment!",
    "Luxurious Living Redefined: Your Dream Apartment Found!",
    "Contemporary Chic: Your Dream Apartment Awaits!",
    "Experience Elegance: Live Your Best Life in Your New Apartment!",
    "Discover Serenity: Your Dream Apartment Beckons!",
    "Seize the Moment: Secure Your Dream Apartment Today!",
    "Uncover Perfection: Your Ideal Apartment Awaits!",
    "A Slice of Paradise: Your Dream Apartment Found!",
    "Live in Style: Find Your Perfect Apartment!",
    "Tranquil Living: Escape to Your Dream Apartment!",
    "Sophisticated Living: Your Ideal Apartment Awaits!",
    "Discover Urban Luxury: Your Dream Apartment Awaits!",
    "Embrace the Extraordinary: Find Your Dream Apartment!",
    "Unmatched Comfort: Your Perfect Apartment Awaits!",
    "Contemporary Living at its Finest: Your Dream Apartment!",
    "Your Personal Sanctuary: Discover Your Ideal Apartment!",
    "Enchanting Living Spaces: Find Your Dream Apartment!",
    "Where Luxury Meets Affordability: Your Ideal Apartment Awaits!",
    "Indulge in Apartment Bliss: Your Dream Home Found!",
    "Time to Shine: Discover Your Dream Apartment!",
    "Unravel Unparalleled Comfort: Your Perfect Apartment Awaits!",
    "Luxe Living: Your Dream Apartment Beckons!",
    "Elevated Living Experience: Discover Your Ideal Apartment!",
    "Embrace the Extraordinary: Your Dream Apartment Awaits!",
    "Where Style Meets Convenience: Find Your Dream Apartment!",
    "Live Life Grand: Discover Your Ideal Apartment!",
    "Unveil the Splendor: Your Dream Apartment Awaits!"
]

#------------------------------------------------------------    
webdriver_path = './chromedriver'

driver = webdriver.Chrome(webdriver_path) 
driver.get('https://www.roslisting.com/admin2/index.cfm?page=login&res=-5&errorMsg=AllFailed')
driver.switch_to.frame("mainFrame")
time.sleep(3)
email_input = driver.find_element(By.NAME, 'email')
email_input.send_keys('amer@rosnyc.com')

# Find the password input field by name
password_input = driver.find_element(By.NAME, 'password')
password_input.send_keys('13L0ck22!')
time.sleep(1)

submit_button = driver.find_element(By.XPATH, '//input[@type="submit"]')
submit_button.click()

#------------------------------------------------------------------------

for index, row in new_df[34:].iterrows():
    driver.get('https://www.roslisting.com/admin2/listing_quickAdd.cfm')
    folder_path = row['Folder']+'/'+row['flex_path']

    listing_input = driver.find_element(By.ID, 'inputAddress')

    listing_input.send_keys(row['Building'])
    pyautogui.press('enter')
    pyautogui.press('enter')
    try:
        link = driver.find_element(By.XPATH, f"//strong[contains(text(), '{row['Building']}')]/ancestor::a")
        link.click()
    except:
        try:
            link = driver.find_element(By.XPATH, f"//strong[contains(text(), '{row['new_addy']}')]/ancestor::a")
            link.click()
        except:
            test = row['Building'].lower()
            link = driver.find_element(By.XPATH, f"//strong[contains(text(), '{test}')]/ancestor::a")
            link.click()
            
        
        
    status = driver.find_element(By.NAME, 'Status')
    status.click()


    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    time.sleep(.5)
    pyautogui.press('enter')
    time.sleep(.5)

    # status = driver.find_element(By.ID, 'category')
    # status.click()

    # pyautogui.press('down')
    # pyautogui.press('down')
    # time.sleep(.5)
    # pyautogui.press('enter')
    # time.sleep(.5)


    unit = driver.find_element(By.ID, 'Apt')
    unit.send_keys(row['cleaned_unit'])

    # hide_addy = driver.find_element(By.ID, 'hideAddress')
    # hide_addy.click()

    beds = driver.find_element(By.ID, 'beds')
    beds.clear()
    beds.send_keys(row['bed_count'])

    baths= driver.find_element(By.ID, 'bath')
    baths.clear()
    baths.send_keys(row['bath_count'])


    price = driver.find_element(By.ID, 'Price')
    price.send_keys(row['price_edit'])

    web_title = driver.find_element(By.ID, 'showAddressAs')
    web_title.send_keys(random.choice(web_titles))

    to_website = driver.find_element(By.ID, 'website')
    to_website.click()

    to_Ad = driver.find_element(By.ID, 'Ad')
    to_Ad.click()

    floors42 = driver.find_element(By.ID, 'market4')
    floors42.click()
    zumper = driver.find_element(By.ID, 'market25')
    zumper.click()
    time.sleep(2)
    
    for filename in os.listdir(folder_path):
    
        if filename.lower().endswith('.txt'):
        
            file_path = os.path.join(folder_path, filename)

         
            with open(file_path, "r", encoding="utf-8") as txt_file:
                file_contents = txt_file.read()

         
            desc = driver.find_element(By.NAME, 'Features1')
            desc.send_keys(file_contents)
            time.sleep(1.5)

    


    #checkboxes
    og_details = driver.find_element(By.ID, 'OriginalDetails')
    og_details.click()
    dining = driver.find_element(By.ID, 'DiningRoom')
    dining.click()
    kitch = driver.find_element(By.ID, 'EatInKitchen')
    kitch.click()
    wood = driver.find_element(By.ID, 'Hardwood')
    wood.click()
    light = driver.find_element(By.ID, 'Light')
    light.click()
    bath = driver.find_element(By.ID, 'MarbleBath')
    bath.click()
    appliances = driver.find_element(By.ID, 'StainlessSteelAppliances')
    appliances.click()
    walls = driver.find_element(By.ID, 'WallsOK')
    walls.click()
    dishwasher = driver.find_element(By.ID, 'Dishwasher')
    dishwasher.click()
    ceilings = driver.find_element(By.ID, 'HighCeilings')
    ceilings.click()
    microwave = driver.find_element(By.ID, 'Microwave')
    microwave.click()
    OK = driver.find_element(By.ID, 'OpenKitchen')
    OK.click()
    renovated = driver.find_element(By.ID, 'Renovated')
    renovated.click()
    river = driver.find_element(By.ID, 'RiverView')
    river.click()
    city = driver.find_element(By.ID, 'CityView')
    city.click()
    openn = driver.find_element(By.ID, 'OpenView')
    openn.click()
    east = driver.find_element(By.ID, 'exposureEast')
    east.click()
    time.sleep(1)

    condition = driver.find_element(By.ID, 'condition')
    condition.click()
    pyautogui.press('down')
    pyautogui.press('enter')

    pets = driver.find_element(By.ID, 'pets')
    pets.click()
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('down')
    pyautogui.press('enter')

    photo = driver.find_element(By.ID, 'photoButton')
    photo.click()

#     upload = driver.find_element(By.ID, 'uploader_browse')
#     upload.click()
    
    
    upload_container = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'uploader_browse'))
    )



    actions = ActionChains(driver)
    actions.move_to_element(upload_container).perform()
    upload_container.click()


    pyautogui.hotkey("command", "shift", "g")
    time.sleep(2)
    pyperclip.copy(folder_path)
    pyautogui.hotkey("command", "v") 
    time.sleep(5)
    pyautogui.press("enter") 
    time.sleep(3) 
    pyautogui.press("right")
    time.sleep(2)
    pyautogui.hotkey("command", "a") 
    time.sleep(1)
    time.sleep(2)
    pyautogui.press("enter")
    time.sleep(6)
    upload_it = driver.find_element(By.ID, 'uploader_start')
    upload_it.click()

    time.sleep(4)

    gas = driver.find_element(By.ID, 'Gas')
    gas.click()
    electricity = driver.find_element(By.ID, 'Electricity')
    electricity.click()
    heat = driver.find_element(By.ID, 'Heat')
    heat.click()
    water = driver.find_element(By.ID, 'water')
    water.click()
    time.sleep(6)
    submit = driver.find_element(By.ID, 'floatingSubmitBtn')
    submit.click()

    time.sleep(12)
    button_element = driver.find_element(By.CLASS_NAME, "confirm")

    button_element.click()