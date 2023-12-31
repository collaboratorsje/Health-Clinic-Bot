#Importing Flask class from the flask web framework, render_templates(which generates HTML pages dynamically), 
#request(to access incoming request), jsonif(to create JSON response)
from flask import Flask, render_template, request, jsonify
import csv
# Import CORS from flask_cors(extension of flask)
from flask_cors import CORS  

#Initializing the flask app by creating an instance of the flask web application
app = Flask(__name__)
# Enable CORS for  Flask app to permit diff domains 
CORS(app)  
#creating a hospital_info empty global dictionary
hospital_info = {}
#creating a class called ChatBot
class ChatBot:
    def __init__(self):     #Defining a init method(consturctor for instances)
        self.user_name = ""     #Initializing instance variables 
        self.facility_type = ""

    def handle_message(self, user_message):     #creating a handle_message method that handles user message

        response = ""       #initializing an empty "response" string 
        if not self.user_name:
            self.user_name = user_message.strip()
            response = f"Hello, {self.user_name}! Please select a facility type:"
        elif not self.facility_type:
            self.facility_type = user_message.strip()
            response = f"You selected: {self.facility_type}. Please enter your postal code:"
        elif user_message.isdigit() and len(user_message) == 6:
            info = self.display_information(self.facility_type, user_message)
            if info:
                response = info
                response += "\nDo you want to have another interaction? (yes/no):"
            else:
                response = "No information found for the selected facility type and postal code."
        else:
            response = "Invalid input. Please enter valid details as requested."
        return response

    def display_information(self, facility_type, postal_code):
        matching_info = []      #initializing an empty list to store dictionaries 
         # reading a csv file
        with open('data_clean/clean_healthCare_data.csv', 'r') as file:
            reader = csv.reader(file)   #reading the file content
            next(reader)  # Skip the header row
            for row in reader:
                if row[10] == facility_type and row[5] == postal_code:
                    matching_info.append({
                        'Hospital Name': row[0],
                        'Hospital Type': row[1],
                        'Address': row[2],
                        'City': row[3],
                        'State': row[4],
                        'Postal Code': row[5],
                        'Email': row[6],
                        'Contact Number': row[7],
                        'Rating': row[8],
                        'Doctor\'s Name': row[9],
                        'Insurance': row[11],
                        'Emergency Services': row[12],
                        'Opening Hours': row[13],
                        'Website URL': row[16]
                    })

        if matching_info:
            matching_info = sorted(matching_info, key=lambda x: float(x['Rating']), reverse=True)
            info = "Here is information for your selection:\n"      #initializing the info variable
            for row in matching_info:
                info += '\n'
                info += f"Hospital Name: {row['Hospital Name']}\n"
                info += f"Hospital Type: {row['Hospital Type']}\n"
                info += f"Address: {row['Address']}\n"
                info += f"City: {row['City']}\n"
                info += f"State: {row['State']}\n"
                info += f"Postal Code: {row['Postal Code']}\n"
                info += f"Email: {row['Email']}\n"
                info += f"Contact Number: {row['Contact Number']}\n"
                info += f"Rating: {row['Rating']}\n"
                info += f"Doctor's Name: {row['Doctor''s Name']}\n"
                info += f"Insurance: {row['Insurance']}\n"
                info += f"Emergency Services: {row['Emergency Services']}\n"
                info += f"Opening Hours: {row['Opening Hours']}\n"
                info += f"Website URL: {row['Website URL']}\n" 
            return info
        else:
            return None

chatbot = ChatBot()     #creating an instance or object of chatbot class
#Defining a route for the root URL of the web application.
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/map')  # Define a new route for the map view
def map_view():
    # gets queries from request url and assigns to variables
    facility_type = request.args.get('facility_type')
    postal_code = request.args.get('postal_code')

    # Use the global hospital_info dictionary
    global hospital_info

    return render_template('map.html', hospital_info=hospital_info)

@app.route('/submit_message', methods=['POST'])     #receives a user message as a post request
def submit_message():
    user_message = request.form['user_message']     #retrives the user message as a form data 
    response = chatbot.handle_message(user_message) #process the message using chatbot object
    return jsonify({'bot_response': response})      #converts the bot resonse into JSON

@app.route('/get_data', methods=['GET'])
def get_data():
    facility_type = request.args.get('facility_type')
    postal_code = request.args.get('postal_code')
    #print(facility_type)
    #print(postal_code)
    
    matching_info = []
    try:
        #print("file before")
        with open('data_clean/clean_healthCare_data.csv', 'r') as file:
            #print("file oppened")
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                #print(row[10], facility_type, len(row[10]), len(facility_type))
                if row[10] == facility_type and row[5] == postal_code:
                    matching_info.append({
                        'Hospital Name': row[0],
                        'Hospital Type': row[1],
                        'Address': row[2],
                        'City': row[3],
                        'State': row[4],
                        'Postal Code': row[5],
                        'Email': row[6],
                        'Contact Number': row[7],
                        'Rating': row[8],
                        'Doctor\'s Name': row[9],
                        'Insurance': row[11],
                        'Emergency Services': row[12],
                        'Opening Hours': row[13],
                        'Latitude': row[14],
                        'Longitude': row[15],
                        'Website URL': row[16]
                    })

        if matching_info:
            matching_info = sorted(matching_info, key=lambda x: float(x['Rating']), reverse=True)
            global hospital_info
            hospital_info = matching_info
            print(f'\nstart\n {hospital_info} \nend\n')
            return jsonify({'data': matching_info})
        else:
            return jsonify({'data': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Return an error message with HTTP status 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)

    