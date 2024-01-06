from flask import Flask, render_template, request, flash, redirect, url_for, make_response, jsonify
import os, datetime
import json, firebase_admin
from firebase_admin import db, credentials
from datetime import timedelta, datetime

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the credentials file
cred_path = os.path.join(current_dir, 'credentials.json')

# Use the absolute path in the credentials.Certificate() function
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {"databaseURL": "https://incubator-sensors-default-rtdb.asia-southeast1.firebasedatabase.app/"})

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mira'

# Link for the home of the website
@app.route('/')
def index():
    return render_template("home.htm")

@app.route('/home')
def home():
    return render_template("home.htm")

@app.route('/about')
def about():
    return render_template("about.htm")

@app.route('/cleaning')
def cleaning():
    return render_template("cleaning.htm")

@app.route('/cleaning_data', methods=["GET"])
def get_cleaning_data():
    cleaning_data = db.reference("/Cleaning Table").get()
    return jsonify(cleaning_data)

@app.route('/cand_turn')
def cand_turn():
    return render_template("cand_turn.htm")

@app.route('/solar')
def solar():
    return render_template("solar.htm")

@app.route('/solar/data')
def solar_data():
    ref_BatteryPercentage = db.reference("/solar/components/BatteryPercentage").get()
    ref_BatteryDischarge = db.reference("/solar/components/BatteryDischarge").get()
    ref_SolarVoltage = db.reference("/solar/components/SolarVoltage").get()
    
    data = {
        "BatteryPercentage": float(ref_BatteryPercentage),
        "BatteryDischarge": float(ref_BatteryDischarge),
        "SolarVoltage": float(ref_SolarVoltage),
    }
    return jsonify(data)

@app.route('/SolarAdjustment', methods=["GET"])
def get_SolarAdjustment():
    ref_SolarAdjustment = db.reference("/solar/components/SolarAdjustment").get()
    SolarAdjustment = str(ref_SolarAdjustment)
    return jsonify({"SolarAdjustment": SolarAdjustment})

@app.route('/solar_data', methods=["GET"])
def get_solar_data():
    solar_data = db.reference("/SolarTable").get()
    return jsonify(solar_data)

# Link for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        user = request.form.get('username')
        password = request.form.get('password')

        if user == "admin" and password == "admin":
            flash("Logged in successfully!", category='success')
            return redirect(url_for('overview'))
        else:
            error = "Invalid Username or Password"

    return render_template('login.htm', error=error)

# Link for the overview of the website
@app.route('/overview', methods=['GET', 'POST'])
def overview():
    return render_template('overview.htm')

@app.route('/humid_temp', methods=['GET', 'POST'])
def humid_temp():
    return render_template('humid_temp.htm')

@app.route('/humid_temp_data', methods=["GET"])
def get_humid_temp_data():
    humid_temp_data = db.reference("/TempTable").get()
    return jsonify(humid_temp_data)

@app.route('/light_status', methods=["GET"])
def get_light_status():
    ref_status = db.reference("/humid_temp/components/Light 1").get()
    status = str(ref_status)
    return jsonify({"status": status})

@app.route('/light_status1', methods=["GET"])
def get_light_status1():
    ref_status1 = db.reference("/humid_temp/components/Light 2").get()
    status1 = str(ref_status1)
    return jsonify({"status1": status1})

@app.route('/Fan', methods=["GET"])
def get_Fan():
    ref_Fan = db.reference("/humid_temp/components/Fan").get()
    Fan = str(ref_Fan)
    return jsonify({"Fan": Fan})

@app.route('/Buzzer', methods=["GET"])
def get_Buzzer():
    ref_Buzzer = db.reference("/cleaning/components/Buzzer").get()
    Buzzer = str(ref_Buzzer)
    return jsonify({"Buzzer": Buzzer})

@app.route('/UV', methods=["GET"])
def get_UV():
    ref_UV = db.reference("/cleaning/components/UV").get()
    UV = str(ref_UV)
    return jsonify({"UV": UV})

@app.route('/data', methods=["GET", "POST"])
def data():
    # Data Format
    # [TIME, Temperature, Humidity]
    ref_temperature = db.reference("/humid_temp/components/Temperature").get()
    ref_humidity = db.reference("/humid_temp/components/Humidity").get()
    # Assuming ref_temperature and ref_humidity are numbers, you might need to adjust accordingly
    Temperature = float(ref_temperature)
    Humidity = float(ref_humidity)
    current_datetime = datetime.now()

    # Add 8 hours to the current time
    adjusted_datetime = current_datetime + timedelta(hours=8)

    data = [
        int(adjusted_datetime.timestamp() * 1000),  # Convert to milliseconds
        Temperature,
        Humidity,
    ]
    
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'

    return response

if __name__ == "__main__":
    app.run(debug=True)