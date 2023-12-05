from flask import Flask, render_template, request, flash, redirect, url_for, make_response, jsonify, Response
import os, datetime, time, cv2
'''import numpy as np
from threading import Thread'''
import json, firebase_admin
from firebase_admin import db, credentials
from datetime import timedelta, datetime

'''global capture, rec_frame, switch, rec, out
capture = 0
switch = 1
rec = 0

try:
    os.mkdir('./shots')
except OSError as error:
    pass

net = cv2.dnn.readNetFromCaffe('flaskapp/website/saved_model/deploy.prototxt.txt',
                               'flaskapp/website/saved_model/res10_300x300_ssd_iter_140000.caffemodel')'''

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the credentials file
cred_path = os.path.join(current_dir, 'credentials.json')

# Use the absolute path in the credentials.Certificate() function
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {"databaseURL": "https://incubator-sensors-default-rtdb.asia-southeast1.firebasedatabase.app/"})

'''camera = cv2.VideoCapture(0)'''

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mira'

# Link for the home of the website
@app.route('/')
def home():
    return render_template("home.htm")

@app.route('/about')
def about():
    return render_template("about.htm")

@app.route('/cleaning')
def cleaning():
    return render_template("cleaning.htm")

@app.route('/candling')
def candling():
    return render_template("candling.htm")

def record(out):
    global rec_frame
    while rec:
        time.sleep(0.05)
        out.write(rec_frame)

def gen_frames():
    global out, capture, rec_frame
    while True:
        success, frame = camera.read()
        if success:
            if capture:
                capture = 0
                now = datetime.datetime.now()
                p = os.path.sep.join(['shots', "shot_{}.png".format(str(now).replace(":", ''))])
                cv2.imwrite(p, frame)

            if rec:
                rec_frame = frame
                frame = cv2.putText(cv2.flip(frame, 1), "Recording...", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
                frame = cv2.flip(frame, 1)

            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()

                # Update Firebase Realtime Database with relevant information
                db.reference('camera_feed').set({
                    'frame_data': frame,
                    'timestamp': firebase_admin.db.ServerValue.TIMESTAMP
                })

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass

        else:
            pass

    
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/requests',methods=['POST','GET'])
def tasks():
    global switch,camera
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture=1
        elif  request.form.get('stop') == 'Stop/Start':
            if(switch==1):
                switch=0
                camera.release()
                cv2.destroyAllWindows()
            else:
                camera = cv2.VideoCapture(0)
                switch=1
        elif  request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec= not rec
            if(rec):
                now=datetime.datetime.now() 
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":",'')), fourcc, 20.0, (640, 480))
                #Start new thread for recording the video
                thread = Thread(target = record, args=[out,])
                thread.start()
            elif(rec==False):
                out.release()
                 
    elif request.method=='GET':
        return render_template('candling.htm')
    return render_template('candling.htm')

@app.route('/turning')
def turning():
    return render_template("turning.htm")

@app.route('/solar')
def solar():
    return render_template("solar.htm")

@app.route('/solar/data')
def solar_data():
    ref_BatteryPercentage = db.reference("/solar/BatteryPercentage").get()
    ref_CurrentSensorBattery = db.reference("/solar/CurrentSensorBattery").get()
    ref_PowerBattery = db.reference("/solar/PowerBattery").get()
    ref_VoltageSensorBattery = db.reference("/solar/VoltageSensorBattery").get()

    data = {
        "BatteryPercentage": float(ref_BatteryPercentage),
        "CurrentSensorBattery": float(ref_CurrentSensorBattery),
        "PowerBattery": float(ref_PowerBattery),
        "VoltageSensorBattery": float(ref_VoltageSensorBattery),
    }
    return jsonify(data)

   

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
    camera.release()
    cv2.destroyAllWindows()

'''@app.route('/capture_image', methods=["GET"])
def capture_image():
    # Check the light status
    ref_status = db.reference("/humid_temp/components/Status").get()
    status = str(ref_status)

    if status == 'on':
        # Perform actions to capture an image (replace this with your actual image capture logic)
        # For example, you can call a function to capture an image using a camera module
        capture_image_function()

        return jsonify({"message": "Image captured successfully"})
    else:
        return jsonify({"message": "Light is off, image not captured"})'''