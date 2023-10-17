import os
from flask import Flask, render_template, send_from_directory, request, send_file, make_response
from urllib.parse import quote,urljoin
import urllib
import pandas as pd
import pdfkit
from io import BytesIO
import shutil
app = Flask(__name__)

executable_name = 'dummy.exe'
# Use shutil to find the full path to the executable
executable_path = shutil.which(executable_name)

if executable_path is not None:
    print(f"Absolute path to {executable_name}: {executable_path}")
else:
    print(f"{executable_name} not found in the system's PATH.")

config = pdfkit.configuration(wkhtmltopdf=executable_path)

config = pdfkit.configuration(wkhtmltopdf=executable_path)


def rename_files_in_flex3(main_folder):
    # Loop through the building folders in the main directory
    for building_folder in os.listdir(main_folder):
        building_path = os.path.join(main_folder, building_folder)
        if os.path.isdir(building_path):
            # Define the path to the "flex3" folder within the building folder
            flex3_folder_path = os.path.join(building_path, 'flex3')

            # Check if the "flex3" folder exists and is a directory
            if os.path.exists(flex3_folder_path) and os.path.isdir(flex3_folder_path):
                # List all files in the "flex3" folder
                files_in_flex3 = os.listdir(flex3_folder_path)

                # Iterate through the files and rename them if they contain white spaces
                for file_name in files_in_flex3:
                    if ' ' in file_name:
                        # Replace white spaces with underscores in the file name
                        new_file_name = file_name.replace(' ', '_')

                        # Construct the full paths for the old and new file names
                        old_file_path = os.path.join(flex3_folder_path, file_name)
                        new_file_path = os.path.join(flex3_folder_path, new_file_name)

                        # Rename the file
                        os.rename(old_file_path, new_file_path)
                        print(f'Renamed: {file_name} -> {new_file_name}')

# Specify the path to your main folder containing building folders
main_folder = 'static/fidiBuildings'
rename_files_in_flex3(main_folder)


# Define the folder path where building photos are stored
main_folder = 'static/fidiBuildings'

# Create a list to store data for each building
building_data_list = []

# Loop through the building folders in the main directory
for building_folder in os.listdir(main_folder):
    building_path = os.path.join(main_folder, building_folder)
    if os.path.isdir(building_path):
        # Check if the "flex3" subfolder exists within the building folder
        flex3_folder = os.path.join(building_path, 'flex3')
        if os.path.exists(flex3_folder) and os.path.isdir(flex3_folder):
            # Initialize data for the current building
            building_data = {
                'title': f'{building_folder.replace("_", " ")} ',

                'studio_price': 'Add studio price here',  # Replace with actual prices
                'one_bedroom_price': 'Add 1 bedroom price here',
                'two_bedroom_price': 'Add 2 bedroom price here',
                'unit_photos': []  # To store relative photo file paths
            }

            # Get a list of photo file names in the "flex3" subfolder
            photos = []
            for photo in os.listdir(flex3_folder):
                if photo.lower().endswith(('.jpeg', '.png')):
                    # Replace spaces with underscores in file names
                    sanitized_photo = photo.replace(" ", "_")
                    photos.append(sanitized_photo)

            # Construct the relative photo file paths with URL encoding
            photo_urls = []
            for photo in photos:
                # Use urllib.parse to handle URL encoding
                encoded_photo = urllib.parse.quote(photo, safe='')
                photo_path = os.path.join('fidiBuildings', urllib.parse.quote(building_folder), 'flex3', encoded_photo)
                photo_urls.append(photo_path)

            building_data['unit_photos'].extend(photo_urls)

            # Append the data for the current building to the list
            building_data_list.append(building_data)

@app.route('/')
def index():
    return render_template('index.html', building_data_list=building_data_list)

@app.route('/test')
def test():
    # TODO the context should be outside of the function I think..... but idk just to keep it clean
    all_prices = {}  # Create an empty dictionary to store prices for all buildings
    for i, building_data in enumerate(building_data_list):
        building_data['index'] = i
    # Calculate prices for all buildings and store them in the 'all_prices' dictionary
    for building_data in building_data_list:
        a = building_data['title']
        a = a.strip()
        if a == '85 John':
            a = '85 John '

        # Modify this part to calculate prices for 'a' as you did in the 'building' route
        df = pd.read_csv('Data/lowest_prices.csv')
        
        # Check if there are any rows in the DataFrame that match the condition
        if len(df[df['Building'] == a]) > 0:
            prices = {
                'flex1': df['Lowest_Studio_Price'].values[0],
                'flex2': df['Lowest_1_Bedroom_Price'].values[0],
                'flex3': df['Lowest_2_Bedroom_Price'].values[0],
            }
            all_prices[a] = prices  # Store prices in the dictionary with the building name as the key
    print(all_prices)
    return render_template('test.html', building_data_list=building_data_list, prices=all_prices)

@app.route('/building/<int:building_id>')
def building(building_id):
    if building_id >= 0 and building_id < len(building_data_list):
            building_data = building_data_list[building_id]
            a = building_data['title']
            a = a.strip()
            if a == '85 John':
                a = '85 John '
            
  
            df = pd.read_csv('Data/lowest_prices.csv')
            df = df[df['Building']==a]
            prices = {
                'flex1': df['Lowest_Studio_Price'].values[0],
                'flex2': df['Lowest_1_Bedroom_Price'].values[0],
                'flex3': df['Lowest_2_Bedroom_Price'].values[0],
            }
            
      
            return render_template('building.html', building_data=building_data, building_id=building_id, prices=prices)
    else:
        return "Building not found"
    




if __name__ == '__main__':
    app.run(debug=True)
