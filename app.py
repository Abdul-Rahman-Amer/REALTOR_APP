import os
from flask import Flask, render_template, send_from_directory, request, send_file, make_response, redirect
from urllib.parse import quote,urljoin
import urllib
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for,jsonify
import pandas as pd
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import shutil

app = Flask(__name__)

def is_image(filename):
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.tiff'}
    ext = os.path.splitext(filename)[-1].lower()
    return ext in image_extensions

app.jinja_env.globals.update(is_image=is_image)

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
            subfolders = [subfolder for subfolder in os.listdir(building_path) if os.path.isdir(os.path.join(building_path, subfolder))]
            subfolder_paths = [os.path.join(building_path, subfolder) for subfolder in subfolders]
            building_data = {
                'title': f'{building_folder.replace("_", " ")} ',

                'studio_price': 'Add studio price here',  # Replace with actual prices
                'one_bedroom_price': 'Add 1 bedroom price here',
                'two_bedroom_price': 'Add 2 bedroom price here',
                'unit_photos': [],
                  'subfolders':subfolders,
                   'subfolder_paths':subfolder_paths # To store relative photo file paths
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



@app.route('/my_buildings')
def index():
    folder_path = 'static/fidiBuildings'
    subfolders = [os.path.abspath(os.path.join(folder_path, f)) for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
    
    # Create a list to store data for each building
    building_data_list = []

    # Loop through the building folders in the main directory
    for building_folder in os.listdir(main_folder):
        building_path = os.path.join(main_folder, building_folder)
        if os.path.isdir(building_path):
            # Initialize data for the current building
            subfolders = [subfolder for subfolder in os.listdir(building_path) if os.path.isdir(os.path.join(building_path, subfolder))]
            subfolder_paths = [os.path.join(building_path, subfolder) for subfolder in subfolders]
            building_data = {
                'title': f'{building_folder.replace("_", " ")} ',
                'studio_price': 'Add studio price here',  # Replace with actual prices
                'one_bedroom_price': 'Add 1 bedroom price here',
                'two_bedroom_price': 'Add 2 bedroom price here',
                'unit_photos': [],
                'subfolders': subfolders,
                'subfolder_paths': subfolder_paths  # To store relative photo file paths
            }

            try:
                # Check if the "flex3" subfolder exists within the building folder
                flex3_folder = os.path.join(building_path, 'flex3')
                if os.path.exists(flex3_folder) and os.path.isdir(flex3_folder):
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
            except Exception as e:
                print(f"Error processing 'flex3' folder for building {building_folder}: {str(e)}")

            # Append the data for the current building to the list
            building_data_list.append(building_data)


   

    return render_template('index.html', building_data_list=building_data_list)

@app.route('/test')
def test():
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
    
# Define the CSV file path
csv_file_path = 'clients/clients.csv'

# Function to read CSV data
def read_csv_data():
    if os.path.exists(csv_file_path):
        return pd.read_csv(csv_file_path)
    return None
def read_employee_data():
    if os.path.exists('employees/employees.csv'):
        return pd.read_csv('employees/employees.csv')
    return None

# Read the CSV file initially
csv_data = read_csv_data()


@app.route('/')
def home():
    global csv_data
    csv_data = read_csv_data()  # Reload CSV data when the home page is accessed
    return render_template('home.html', csv_data=csv_data)

@app.route('/manage_finances')
def manage_finances():
    csv_data = pd.read_csv('manage_finances/manage_finances.csv')
    return render_template('manage_finances.html', csv_data=csv_data)

@app.route('/add_costs', methods=['GET', 'POST'])
def add_costs():
    if request.method == 'POST':
        current_date = datetime.now().strftime('%Y-%m-%d')
        # Get data from the form
        date = current_date
        cost_of_goods = float(request.form['cost_of_goods']) if request.form['cost_of_goods'] else 0
        rent = float(request.form['rent']) if request.form['rent'] else 0
        utilities = float(request.form['utilities']) if request.form['utilities'] else 0
        repairs_maintenance = float(request.form['repairs_maintenance']) if request.form['repairs_maintenance'] else 0
        supplies_inventory = float(request.form['supplies_inventory']) if request.form['supplies_inventory'] else 0
        marketing_advertising = float(request.form['marketing_advertising']) if request.form['marketing_advertising'] else 0
        insurance_premiums = float(request.form['insurance_premiums']) if request.form['insurance_premiums'] else 0
        taxes = float(request.form['taxes']) if request.form['taxes'] else 0
        bank_fees = float(request.form['bank_fees']) if request.form['bank_fees'] else 0
        travel_entertainment = float(request.form['travel_entertainment']) if request.form['travel_entertainment'] else 0
        software_subscriptions = float(request.form['software_subscriptions']) if request.form['software_subscriptions'] else 0
        miscellaneous = float(request.form['miscellaneous']) if request.form['miscellaneous'] else 0
        legal_professional_fees = float(request.form['legal_professional_fees']) if request.form['legal_professional_fees'] else 0
        employee_benefits = float(request.form['employee_benefits']) if request.form['employee_benefits'] else 0
        business_meals = float(request.form['business_meals']) if request.form['business_meals'] else 0
        office_expenses = float(request.form['office_expenses']) if request.form['office_expenses'] else 0
        
        # Load the existing DataFrame from the CSV file
        df = pd.read_csv('manage_finances/manage_finances.csv')
        
        # Check if the current date exists in the DataFrame
        if current_date in df['date'].values:
            # Update the row for the current date
            df.loc[df['date'] == current_date, 'cost of goods'] += cost_of_goods
            df.loc[df['date'] == current_date, 'rent'] += rent
            df.loc[df['date'] == current_date, 'utilities'] += utilities
            df.loc[df['date'] == current_date, 'repairs_maintenance'] += repairs_maintenance
            df.loc[df['date'] == current_date, 'supplies_inventory'] += supplies_inventory
            df.loc[df['date'] == current_date, 'marketing_advertising'] += marketing_advertising
            df.loc[df['date'] == current_date, 'insurance_premiums'] += insurance_premiums
            df.loc[df['date'] == current_date, 'taxes'] += taxes
            df.loc[df['date'] == current_date, 'bank_fees'] += bank_fees
            df.loc[df['date'] == current_date, 'travel_entertainment'] += travel_entertainment
            df.loc[df['date'] == current_date, 'software_subscriptions'] += software_subscriptions
            df.loc[df['date'] == current_date, 'miscellaneous'] += miscellaneous
            df.loc[df['date'] == current_date, 'legal_professional_fees'] += legal_professional_fees
            df.loc[df['date'] == current_date, 'employee_benefits'] += employee_benefits
            df.loc[df['date'] == current_date, 'business_meals'] += business_meals
            df.loc[df['date'] == current_date, 'office_expenses'] += office_expenses
        else:
            # Initialize a new row for the current date
            new_data = {
                'date': current_date,
                'cost of goods': cost_of_goods,
                'rent': rent,
                'utilities': utilities,
                'repairs_maintenance': repairs_maintenance,
                'supplies_inventory': supplies_inventory,
                'marketing_advertising': marketing_advertising,
                'insurance_premiums': insurance_premiums,
                'taxes': taxes,
                'bank_fees': bank_fees,
                'travel_entertainment': travel_entertainment,
                'software_subscriptions': software_subscriptions,
                'miscellaneous': miscellaneous,
                'legal_professional_fees': legal_professional_fees,
                'employee_benefits': employee_benefits,
                'business_meals': business_meals,
                'office_expenses': office_expenses
            }
            
            # Append the new data to the DataFrame
            df = df.append(new_data, ignore_index=True)
        
        # Save the updated DataFrame to the CSV file
        df.to_csv('manage_finances/manage_finances.csv', index=False)
        
        # Redirect to the homepage
        return redirect(url_for('manage_finances'))

@app.route('/insights')
def insihgts():
    employee_earnings = pd.read_csv('employees/employees.csv')
    
    # Convert the DataFrame to a list of dictionaries
    employee_json = employee_earnings.to_dict(orient='records')
    
    return render_template('insights.html', employee_json=employee_json)

def payrolls():
    employees = pd.read_csv('employees/employees.csv')
    if not os.path.exists("payroll"):
        os.makedirs("payroll")


    employee_df = pd.DataFrame(columns=['Date', 'Time in', 'Time out', 'Daily Sales', 'Commissions'])

    for index, row in employees.iterrows():
        employee_name = row['name']
        csv_filename = f"payroll/{employee_name.replace(' ', '_')}.csv"

        # Check if the CSV file already exists for the employee
        if not os.path.exists(csv_filename):
            employee_df.to_csv(csv_filename)
    

    

@app.route('/payroll')
def payroll():
    a = payrolls()
    payroll_folder = "payroll"
    payroll_files = [file.replace('.csv', '') for file in os.listdir(payroll_folder) if file.endswith(".csv")]
    

    # Replace underscores with spaces and remove the ".csv" extension
    



    return render_template('payroll.html', data = payroll_files)


def safe_eval_sales(x):
    if not x:
        return 0
    try:
        sales_data = ast.literal_eval(x)
        if isinstance(sales_data, list):
            return sum(sale.get('Amount', 0) for sale in sales_data)
    except (ValueError, SyntaxError):
        pass
    return 0

@app.route('/employees')
def employees():
    try:
        # Read the CSV file into the DataFrame
        df = pd.read_csv('employees/employees.csv')

        # Calculate the total sales amount for each employee
        # Modify the lambda function for 'Total Sales' calculation
        df['Total Sales'] = df['sales'].apply(safe_eval_sales)



        # Save the DataFrame back to the CSV file (if needed)
        df.to_csv('employees/employees.csv', index=False)
        df['sales'] = df['sales'].apply(ast.literal_eval)


        # Render the HTML template with the updated DataFrame
        return render_template('employees.html', data=df)
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return render_template('error.html')



@app.route('/add_contact', methods=['POST'])
def add_contact_route():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        add_contact(name, email, phone)
    
    return redirect(url_for('home'))


def add_employee(name):
    # Read the existing CSV data
    df = read_employee_data()

    # Add the new contact to the DataFrame
    new_contact = {'name': name, 'sales': '[]'}
    df = df.append(new_contact, ignore_index=True)
    
    # Save the updated DataFrame to the CSV file
    df.to_csv('employees/employees.csv', index=False)

@app.route('/add_employee', methods=['POST'])
def add_employee_route():
    if request.method == 'POST':
        name = request.form.get('name')
        
        add_employee(name)
    
    return redirect(url_for('employees'))

def add_contact(name, email, phone):
    # Read the existing CSV data
    df = read_csv_data()
    
    # Create a new DataFrame if the file doesn't exist
    if df is None:
        df = pd.DataFrame(columns=['name', 'email', 'phone number'])
    
    # Add the new contact to the DataFrame
    new_contact = {'name': name, 'email': email, 'phone number': phone}
    df = df.append(new_contact, ignore_index=True)
    
    # Save the updated DataFrame to the CSV file
    df.to_csv(csv_file_path, index=False)
    
    # Update the global csv_data variable
    global csv_data
    csv_data = df

    

# Function to generate and save clients.csv (You can remove this if not needed)
def generate_clients_csv():
    # Check if the 'clients' directory exists, and if not, create it
    if not os.path.exists('clients'):
        os.makedirs('clients')

    # Define sample data for the DataFrame
    data = {
        'name': ['John Doe', 'Jane Smith', 'Alice Johnson'],
        'email': ['john@example.com', 'jane@example.com', 'alice@example.com'],
        'phone number': ['123-456-7890', '987-654-3210', '555-555-5555']
    }

    # Create a Pandas DataFrame
    df = pd.DataFrame(data)

    # Check if the CSV file already exists
    if os.path.exists(csv_file_path):
        print("CSV file 'clients.csv' already exists.")
    else:
        # Save the DataFrame to a CSV file
        df.to_csv(csv_file_path, index=False)
        print("CSV file 'clients.csv' has been generated.")

def generate_employees_csv():
    # Check if the 'clients' directory exists, and if not, create it
    if not os.path.exists('employees'):
        os.makedirs('employees')

    # Define sample data for the DataFrame
    data = {
        'name': ['John Doe', 'Jane Smith', 'Alice Johnson'],
        'sales': [0,0,0]
    }

    # Create a Pandas DataFrame
    df = pd.DataFrame(data)

    # Check if the CSV file already exists
    if os.path.exists('employees/employees.csv'):
        print("CSV file 'employees.csv' already exists.")
    else:
        # Save the DataFrame to a CSV file
        df.to_csv('employees/employees.csv', index=False)
        print("CSV file 'employees.csv' has been generated.")

def generate_manage_insights():

    if not os.path.exists('manage_finances'):
        os.makedirs('manage_finances')
    current_date = datetime.now().strftime('%Y-%m-%d')
        
    data = {
        'date': current_date,      
        'cost of goods': 0,
        'rent': 0,
        'utilities': 0,
        'repairs_maintenance': 0,
        'supplies_inventory': 0,
        'marketing_advertising': 0,
        'insurance_premiums': 0,
        'taxes': 0,
        'bank_fees': 0,
        'travel_entertainment': 0,
        'software_subscriptions': 0,
        'miscellaneous': 0,
        'legal_professional_fees': 0,
        'employee_benefits': 0,
        'business_meals': 0,
        'office_expenses': 0
    }
        
    df = pd.DataFrame([data])

    # Set the DataFrame index to the default integer index
    df = df.reset_index(drop=True)

        # Check if the CSV file already exists
    if os.path.exists('manage_finances/manage_finances.csv'):
        print("CSV file 'manage_finances.csv' already exists.")
    else:
        # Save the DataFrame to a CSV file
        df.to_csv('manage_finances/manage_finances.csv', index=True)
        print("CSV file 'manage_finances.csv' has been generated.")



@app.route('/remove/<int:index>')
def remove_contact(index):
    global csv_data

    if csv_data is not None and 0 <= index < len(csv_data):
        # Remove the specific row by its index
        csv_data = csv_data.drop(index)

        # Save the updated DataFrame to the CSV file
        csv_data.to_csv(csv_file_path, index=False)

        return redirect(url_for('home'))  # Redirect to the home page after removal

    return "Contact not found"

@app.route('/remove_employee/<int:index>')
def remove_employees(index):
    df = pd.read_csv('employees/employees.csv')

    if csv_data is not None and 0 <= index < len(df):
        # Remove the specific row by its index
        df = df.drop(index)

        # Save the updated DataFrame to the CSV file
        df.to_csv('employees/employees.csv', index=False)

        return redirect(url_for('employees'))  # Redirect to the home page after removal

    return "Contact not found"

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_contact(index):
    global csv_data

    if request.method == 'POST':
        # Handle editing the contact here
        # You can access form data using request.form

        # For example, to edit an existing contact:
        updated_name = request.form.get('editName')
        updated_email = request.form.get('editEmail')
        updated_phone = request.form.get('editPhone')

        # Update the specific row in the DataFrame
        if csv_data is not None and 0 <= index < len(csv_data):
            csv_data.at[index, 'name'] = updated_name
            csv_data.at[index, 'email'] = updated_email
            csv_data.at[index, 'phone number'] = updated_phone

            # Save the updated DataFrame to the CSV file
            csv_data.to_csv(csv_file_path, index=False)

            # Redirect back to the home page after editing
            return redirect(url_for('home'))

    # If it's a GET request, render the edit contact page
    contact = csv_data.iloc[index] if csv_data is not None else None
    return render_template('edit_contact.html', contact=contact, contact_index=index)
import ast
@app.route('/edit_sale/<int:index>', methods=['GET', 'POST'])
def edit_sale(index):
    if request.method == 'POST':
        try:
            # Read the CSV file into the DataFrame
            df = pd.read_csv('employees/employees.csv')
            df = df.reset_index(drop=True)

            item = request.form['editItem']
            date = request.form['editDate']
            time = request.form['editTime']
            amount = float(request.form['editAmount'])  # Convert amount to a float

            # Ensure 'sales' column contains lists or empty lists
            if pd.isna(df.loc[index, 'sales']) or isinstance(df.loc[index, 'sales'], int):
                df.at[index, 'sales'] = '[]'  # Initialize as a string representation of an empty list

            # Convert the string representation of a list to an actual list
            sales_list = ast.literal_eval(df.loc[index, 'sales'])

            # Append the dictionary to the 'sales' list
            sales_list.append({'Item': item, 'Date': date, 'Time': time, 'Amount': amount})

            # Save the updated 'sales' list as a string
            df.at[index, 'sales'] = str(sales_list)

            # Save the DataFrame back to the CSV file
            df.to_csv('employees/employees.csv', index=False)
        except Exception as e:
            print(f"An error occurred: {str(e)}")

        return redirect(url_for('employees'))






# Add this route to your Flask app
@app.route('/mass_email')
def mass_email():
    return render_template('mass_email.html', csv_data=csv_data)

@app.route('/mass_sms')
def mass_sms():
    return render_template('mass_sms.html', csv_data=csv_data)

# Function to send mass emails
def send_mass_emails(subject, message, recipients):
    # Your email configuration
    smtp_server = 'smtp.example.com'  # Change this to your SMTP server
    smtp_port = 587  # Change this to your SMTP server's port
    smtp_username = 'your_username@example.com'  # Your SMTP username
    smtp_password = 'your_password'  # Your SMTP password

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        for recipient in recipients:
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = recipient
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            server.sendmail(smtp_username, recipient, msg.as_string())

        server.quit()
        return True
    except Exception as e:
        print(f"Error sending emails: {str(e)}")
        return False

# Route to handle the mass email sending
@app.route('/send_mass_emails', methods=['POST'])
def send_mass_emails_route():
    try:
        selected_recipients = request.form.getlist('recipient')
        email_subject = request.form.get('email-message-subject')  # Get subject from the form
        email_message = request.form.get('email-message')  # Get message from the form

        # Read the CSV file containing recipient data
         # Replace with your CSV file path
        global csv_data
        df= read_csv_data()
        # Filter the recipients based on the selected checkboxes
        selected_emails = df.loc[df.index.isin(selected_recipients)]['email'].tolist()

        # Send emails to selected recipients
        for email in selected_emails:
            send_mass_emails(email_subject, email_message, email)

        return "Mass emails sent successfully!"
    except Exception as e:
        return str(e)

def send_sms(message, recipient):
    # Implement your SMS sending logic here
    # You can use a service or library to send SMS messages
    pass

@app.route('/send_mass_sms', methods=['POST'])
def send_mass_sms_route():
    try:
        selected_recipients = request.form.getlist('recipient')
        sms_message = request.form.get('sms-message')  # Get SMS message from the form

        # Read the CSV file containing recipient data
        df = pd.read_csv('your_recipient_data.csv')  # Replace with your CSV file path

        # Filter the recipients based on the selected checkboxes
        selected_phone_numbers = df.loc[df.index.isin(selected_recipients)]['phone number'].tolist()

        # Send SMS messages to selected recipients
        for phone_number in selected_phone_numbers:
            send_sms(sms_message, phone_number)

        return "Mass SMS messages sent successfully!"
    except Exception as e:
        return str(e)
    
@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/add_task', methods=['POST'])
def add_task():
    # Get the task name and date from the form
    task_name = request.form.get('task-name')
    task_date = request.form.get('task-date')
    task_time = request.form.get('task-time')

    # Process the data (for example, you can save it to a database or a list)
    task = {
        'name': task_name,
        'date': task_date,
        'time': task_time
    }
@app.route('/edit_folder/<path:folder_path>')
def edit_folder(folder_path):
    # Combine the provided folder path with the main folder path
    full_folder_path = folder_path

    # Check if the folder exists
    if os.path.exists(full_folder_path) and os.path.isdir(full_folder_path):
        # List all the files and directories in the specified folder
        contents = os.listdir(full_folder_path)
        
        # Render a template that shows the contents of the folder
        return render_template('edit_folder.html', folder_name=folder_path, contents=contents)
    else:
        # Handle the case where the folder doesn't exist
        return "Folder not found", 404 

@app.route('/remove_folder/<path:folder_path>')
def remove_folder(folder_path):
    # Get the absolute path to the folder
    absolute_path = folder_path
    print(absolute_path)

    try:
        if os.path.exists(absolute_path):
            # Remove the folder
            shutil.rmtree(absolute_path)

            return redirect('/my_buildings')
        else:
            return 'Folder does not exist'
        
    except Exception as e:
        return str(e)
    


@app.route('/add_folder/<path:building_title>', methods=['POST', 'GET'])
def add_folder(building_title):
    if request.method == 'POST':
        folder_name = request.form.get('folder_name')  # Use request.form for POST data
        building_title = building_title.replace(' ', '_')
    
        # Create the folder in the specified path
        folder_path = f'static/fidiBuildings/{building_title}/{folder_name}'

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return redirect('/my_buildings')
        else:
            return 'Folder already exists'

    # Handle the GET request (form rendering)
    return render_template('index.html', building_data_list=building_data_list)

@app.route('/add_building', methods=['POST', 'GET'])
def add_building():
    if request.method == 'POST':
        building_name = request.form.get('building_name')  # Use request.form for POST data
        building_title = building_name.replace(' ', '_')
    
        # Create the folder in the specified path
        folder_path = f'static/fidiBuildings/{building_title}'

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            return redirect('/my_buildings')
        else:
            return 'Folder already exists'

    # Handle the GET request (form rendering)
    return redirect('/my_buildings')
    
    
if __name__ == '__main__':
    app.run(debug=True)
    generate_clients_csv()
    generate_employees_csv()
    generate_manage_insights()
    payrolls()
    app.run(debug=True)
