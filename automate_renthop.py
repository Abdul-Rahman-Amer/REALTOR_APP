from pywebcopy import save_webpage
from time import sleep
from bs4 import BeautifulSoup as bs
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

#------------------------------------------------------------    
webdriver_path = './chromedriver'

driver = webdriver.Chrome(webdriver_path) 
driver.get('https://www.renthop.com/')

links = driver.find_elements(by='css selector', value='a[href="/account/login"]')
if links:
    links[0].click()

email_input = driver.find_element(by='css selector', value='#login-1-username-input')
email_input.send_keys('amer@rosnyc.com')

submit_button = driver.find_element(by='css selector', value='#login-1-button')
submit_button.click()

time.sleep(2)

password_input = driver.find_element(by='css selector', value='#login-2-password-input')
password_input.send_keys('teamwork')


submit_button = driver.find_element(by='css selector', value='#login-2-button')
submit_button.click()

time.sleep(2)



for index, row in new_df.iterrows():
#------------------------------------------------------------    
    folder_path = row['Folder']+'/'+row['flex_path']
    
    links = driver.find_elements(by='css selector', value='a[href="/r/listings/post"]  div.agent-quicklinks-new-listing')
    if links:
        links[0].click()
   

    address_input = driver.find_element(by='css selector', value='input#address')
    driver.execute_script("arguments[0].scrollIntoView(true);", address_input)
    address_input.send_keys(f"{row['Building']} New York, NY")
    pyautogui.press('enter')


    unit_input = driver.find_element(by='css selector', value='input#unit')
    driver.execute_script("arguments[0].scrollIntoView(true);", unit_input)
    unit_input.send_keys(row['Unit'])
    time.sleep(1)

   
    display_input = driver.find_element(by='css selector', value='input#display_address')
    display_input.clear()
    driver.execute_script("arguments[0].scrollIntoView(true);", display_input)
    display_input.send_keys(row['Cross Street'])
    time.sleep(1)


    if row['Beds'] == 'Studio':
        option_text = 'Studio'
    elif row['Beds'] == '1 Bed':
        option_text = '1 Bed'
    elif row['Beds'] == '2':
        option_text = '2 Bed'

    option_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f'//div[@class="d-inline-block"]/label/div[text()="{option_text}"]'))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", option_element)


    option_element.click()

    time.sleep(1.5)

#------------------------------------------------------------
    if row['num_flex'] == 1:
        checkbox_selector = 'label[for="convertible_features_0"]'
    else:
        checkbox_selector = 'label[for="convertible_features_1"]'

    checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, checkbox_selector))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
    driver.execute_script("arguments[0].click();", checkbox)
    time.sleep(1.5)
#------------------------------------------------------------
    if row['Baths'] == '1 bath':
        option_text = '1 Bath'
    elif row['Baths'] == '2 baths':
        option_text = '2 Bath'

    option_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f'//div[@class="d-inline-block"]/label/div[text()="{option_text}"]'))
    )


    driver.execute_script("arguments[0].scrollIntoView(true);", option_element)


    option_element.click()
#------------------------------------------------------------
    
    price_input = driver.find_element(by='css selector', value='#price')
    price_input.send_keys(row['Price'])
    time.sleep(1)
#------------------------------------------------------------
    fee = driver.find_element(by='css selector', value='label[for="fee_features_1"]')
    fee.click()
    time.sleep(1)
#------------------------------------------------------------
    for filename in os.listdir(folder_path):
    
        if filename.lower().endswith('.txt'):
        
            file_path = os.path.join(folder_path, filename)

         
            with open(file_path, "r", encoding="utf-8") as txt_file:
                file_contents = txt_file.read()

         
            description = driver.find_element(by='css selector', value='#description')
            description.send_keys(file_contents)
            time.sleep(1.5)
#------------------------------------------------------------
    for i in range(6):
        element_id = f'building_features_{i}'
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'label[for="{element_id}"]'))
        )

        
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()

      
        element.click()
#------------------------------------------------------------
    for i in range(2):
        element_id = f'pet_features_{i}'
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'label[for="{element_id}"]'))
        )

       
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()

      
        element.click()


    time.sleep(1)
#------------------------------------------------------------
    upload_container = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'upload_container'))
    )



    actions = ActionChains(driver)
    actions.move_to_element(upload_container).perform()


    upload_link = driver.find_element(By.ID, "upload_browse_files")


    file_list = os.listdir(folder_path)

    time.sleep(3)  



#     folder_path = os.path.abspath(folder_path)
#------------------------------------------------------------    
    upload_link.click()
    time.sleep(6)

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
    time.sleep(25)
    
    button = driver.find_element(By.XPATH, "//button[contains(text(), 'Save + Post')]")
    button.click()

    